import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# Page Setup
st.set_page_config(page_title="Pro Stock Dashboard 2026", layout="wide")
st.title("📈 Real-Time Stock Portfolio")

# --- SIDEBAR: CONFIGURATION ---
st.sidebar.header("Portfolio Configuration")
default_portfolio = "AAPL:10, TSLA:5, BTC-USD:0.1, MSFT:12"
user_input = st.sidebar.text_area("Format: TICKER:SHARES", default_portfolio)

portfolio_dict = {}
try:
    for item in user_input.split(","):
        if ":" in item:
            ticker, shares = item.split(":")
            portfolio_dict[ticker.strip().upper()] = float(shares.strip())
except Exception:
    st.sidebar.error("⚠️ Formatting error! Use 'TICKER:SHARES' (comma separated).")

# --- DATA FETCHING (Current & Historical) ---
@st.cache_data(ttl=300)
def get_portfolio_analysis(portfolio):
    current_data = []
    total_val = 0
    history_combined = pd.DataFrame()

    for ticker, shares in portfolio.items():
        try:
            stock = yf.Ticker(ticker)
            # Fetch 1 month of history for the trend line
            hist = stock.history(period="1mo")
            
            if not hist.empty:
                # 1. Process Current Metrics
                curr_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else curr_price
                change = ((curr_price - prev_price) / prev_price) * 100
                val = curr_price * shares
                total_val += val
                
                current_data.append({
                    "Ticker": ticker, "Shares": shares, 
                    "Price": round(curr_price, 2), "Value ($)": round(val, 2), 
                    "Day Change %": round(change, 2)
                })

                # 2. Process Historical Trend (Shares * Daily Close)
                ticker_history = hist['Close'] * shares
                if history_combined.empty:
                    history_combined = ticker_history.to_frame(name=ticker)
                else:
                    history_combined = history_combined.join(ticker_history.to_frame(name=ticker), how='outer')
        
        except Exception as e:
            st.warning(f"Error loading {ticker}: {e}")

    # Calculate total portfolio value for each day
    if not history_combined.empty:
        history_combined['Total Portfolio Value'] = history_combined.sum(axis=1)

    return pd.DataFrame(current_data), total_val, history_combined

# --- MAIN DASHBOARD ---
if portfolio_dict:
    with st.spinner('Calculating 30-day trends...'):
        df, total_val, history_df = get_portfolio_analysis(portfolio_dict)

    if not df.empty:
        # Metrics Top Row
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Portfolio Value", f"${total_val:,.2f}")
        col2.metric("Assets Tracked", len(df))
        col3.metric("Status", "🟢 Live Market Data")

        # 1. Trend Chart (The New Feature)
        st.subheader("📊 30-Day Portfolio Performance")
        fig_trend = px.line(history_df, y='Total Portfolio Value', 
                            labels={'index': 'Date', 'Total Portfolio Value': 'Value ($)'},
                            template="plotly_dark")
        fig_trend.update_traces(line_color='#00ffcc', line_width=3)
        st.plotly_chart(fig_trend, use_container_width=True)

        # 2. Holdings Table
        st.subheader("Holdings Breakdown")
        st.dataframe(df, use_container_width=True, hide_index=True)

        # 3. Allocation Pie Chart
        st.divider()
        st.subheader("Portfolio Allocation")
        fig_pie = px.pie(df, values='Value ($)', names='Ticker', hole=0.5,
                         color_discrete_sequence=px.colors.sequential.Tealgrn)
        st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.info("👈 Enter your tickers in the sidebar to visualize your wealth!")
