import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# Page Setup
st.set_page_config(page_title="My AI Stock Dashboard", layout="wide")
st.title("📈 Real-Time Stock Portfolio")

# --- SIDEBAR: CONFIGURATION ---
st.sidebar.header("Portfolio Configuration")
st.sidebar.markdown("Enter your tickers and the number of shares you own.")

# Default list of tickers and shares
default_portfolio = "AAPL:10, TSLA:5, BTC-USD:0.1, GOOGL:15"
user_input = st.sidebar.text_area("Format: TICKER:SHARES (comma separated)", default_portfolio)

# Process the input into a dictionary
portfolio_dict = {}
try:
    for item in user_input.split(","):
        if ":" in item:
            ticker, shares = item.split(":")
            portfolio_dict[ticker.strip().upper()] = float(shares.strip())
except Exception:
    st.sidebar.error("⚠️ Formatting error! Use 'TICKER:SHARES' format.")

# --- DATA FETCHING ---
@st.cache_data(ttl=300) # Refresh every 5 minutes
def fetch_portfolio_data(portfolio):
    data = []
    total_val = 0
    for ticker, shares in portfolio.items():
        try:
            stock = yf.Ticker(ticker)
            # Fetch recent history to calculate manual price change
            hist = stock.history(period="2d")
            
            if len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change_pct = ((current_price - prev_price) / prev_price) * 100
            else:
                # Fallback for assets with limited history
                current_price = stock.fast_info['last_price']
                change_pct = 0.0
            
            current_value = current_price * shares
            total_val += current_value
            
            data.append({
                "Ticker": ticker,
                "Shares": shares,
                "Price": round(current_price, 2),
                "Value ($)": round(current_value, 2),
                "Day Change %": round(change_pct, 2)
            })
        except Exception as e:
            st.warning(f"Could not update {ticker}: {e}")
            
    return pd.DataFrame(data), total_val

# --- MAIN DASHBOARD ---
if portfolio_dict:
    with st.spinner('Updating market data...'):
        df, total_portfolio_value = fetch_portfolio_data(portfolio_dict)

    if not df.empty:
        # 1. Metrics Top Row
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Portfolio Value", f"${total_portfolio_value:,.2f}")
        col2.metric("Total Assets", len(df))
        col3.metric("Status", "🟢 Live Data")

        # 2. Portfolio Table
        st.subheader("Holdings Breakdown")
        # Highlighting positive/negative changes
        st.dataframe(df.style.format({"Day Change %": "{:.2f}%"}), use_container_width=True, hide_index=True)

        # 3. Visualizations
        st.divider()
        left_chart, right_chart = st.columns(2)
        
        with left_chart:
            st.subheader("Value Allocation")
            fig_pie = px.pie(df, values='Value ($)', names='Ticker', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

        with right_chart:
            st.subheader("Price Performance (Today)")
            fig_bar = px.bar(df, x='Ticker', y='Day Change %', color='Day Change %',
                             color_continuous_scale='RdYlGn')
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.error("No valid data found for the provided tickers.")
else:
    st.info("👈 Enter your tickers in the sidebar to get started!")
