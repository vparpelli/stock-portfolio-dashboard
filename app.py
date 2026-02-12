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
        stock = yf.Ticker(ticker)
        price = stock.fast_info['last_price']
        change = stock.fast_info['year_to_date_change'] * 100 # Approx day change
        current_value = price * shares
        total_val += current_value
        data.append({
            "Ticker": ticker,
            "Shares": shares,
            "Price": round(price, 2),
            "Value ($)": round(current_value, 2),
            "Change %": round(change, 2)
        })
    return pd.DataFrame(data), total_val

# --- MAIN DASHBOARD ---
if portfolio_dict:
    with st.spinner('Fetching market data...'):
        df, total_portfolio_value = fetch_portfolio_data(portfolio_dict)

    # 1. Metrics Top Row
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Portfolio Value", f"${total_portfolio_value:,.2f}")
    col2.metric("Total Assets", len(df))
    col3.metric("Market Status", "🟢 Open" if total_portfolio_value > 0 else "🔴 Closed")

    # 2. Portfolio Table
    st.subheader("Holdings Breakdown")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # 3. Visualizations
    st.divider()
    left_chart, right_chart = st.columns(2)
    
    with left_chart:
        st.subheader("Value Allocation")
        fig_pie = px.pie(df, values='Value ($)', names='Ticker', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    with right_chart:
        st.subheader("Price Comparison")
        st.bar_chart(df.set_index("Ticker")["Price"])
else:
    st.info("👈 Enter your tickers in the sidebar to get started!")
