import streamlit as st
import pandas as pd
import plotly.express as px
import time
from alpaca_trade_api.rest import REST

# --- 1. SECURE CONFIG ---
try:
    # Accessing secrets via the st.secrets dictionary
    api_key = st.secrets["ALPACA_KEY"]
    api_secret = st.secrets["ALPACA_SECRET"]
    base_url = st.secrets.get("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
    
    # Initialize the Alpaca REST Client
    alpaca = REST(api_key, api_secret, base_url)
except Exception as e:
    st.error(f"Secret Manager Error: {e}")
    st.info("Check your .streamlit/secrets.toml file!")
    st.stop()

# --- 2. PAGE SETUP ---
st.set_page_config(page_title="Alpaca Secure Stream 2026", layout="wide")
st.title("🏛️ Real-Time Portfolio Dashboard")

# Sidebar for user input
st.sidebar.header("Portfolio Config")
default_portfolio = "AAPL:10, TSLA:5, NVDA:20, BTC/USD:0.5"
user_input = st.sidebar.text_area("Format: TICKER:SHARES", default_portfolio)
refresh_rate = st.sidebar.slider("Refresh Speed (sec)", 5, 60, 10)

# --- 3. LIVE DATA LOGIC ---
def get_live_portfolio_data(portfolio_map):
    tickers = list(portfolio_map.keys())
    
    # Alpaca's get_latest_bars handles multiple tickers efficiently
    # It returns a dictionary-like object mapping tickers to Bar objects
    bars = alpaca.get_latest_bars(tickers)
    
    data_rows = []
    total_value = 0
    
    for ticker, shares in portfolio_map.items():
        if ticker in bars:
            price = bars[ticker].c  # .c is the closing price
            val = price * shares
            total_value += val
            data_rows.append({
                "Ticker": ticker,
                "Price": f"${price:,.2f}",
                "Value": val,
                "Shares": shares
            })
    
    return pd.DataFrame(data_rows), total_value

# --- 4. MAIN UI LOOP ---
# Parse the text input into a dictionary
portfolio_dict = {}
for item in user_input.split(","):
    if ":" in item:
        t, s = item.split(":")
        portfolio_dict[t.strip().upper()] = float(s.strip())

# Placeholder for the live content
dashboard_container = st.empty()

if portfolio_dict:
    while True:
        try:
            df, total_val = get_live_portfolio_data(portfolio_dict)
            
            with dashboard_container.container():
                # Top Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Portfolio Value", f"${total_val:,.2f}")
                m2.metric("Assets Tracked", len(df))
                m3.metric("Last Updated", time.strftime("%H:%M:%S"))
                
                # Visuals
                col_left, col_right = st.columns([1, 1])
                
                with col_left:
                    st.subheader("Asset Allocation")
                    fig = px.pie(df, values='Value', names='Ticker', hole=0.5, 
                                 template="plotly_dark", color_discrete_sequence=px.colors.sequential.Tealgrn)
                    fig.update_layout(margin=dict(t=20, b=0, l=0, r=0))
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_right:
                    st.subheader("Live Holdings")
                    # Formatting Value for display
                    display_df = df.copy()
                    display_df['Value'] = display_df['Value'].map('${:,.2f}'.format)
                    st.dataframe(display_df, use_container_width=True, hide_index=True)

            time.sleep(refresh_rate)
            
        except Exception as e:
            st.error(f"Stream interrupted: {e}")
            break
else:
    st.info("Enter your portfolio in the sidebar to start the live stream.")
