import streamlit as st
import pandas as pd
import plotly.express as px
import time
from alpaca_trade_api.rest import REST

# --- 1. SECURE CONFIG ---
try:
    # Pulling keys from Streamlit Secrets
    api_key = st.secrets["ALPACA_KEY"]
    api_secret = st.secrets["ALPACA_SECRET"]
    # Defaulting to paper if base_url isn't provided
    base_url = st.secrets.get("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
    
    # Initialize the Alpaca REST Client
    alpaca = REST(api_key, api_secret, base_url)
except Exception as e:
    st.error(f"Secret Manager Error: {e}")
    st.info("Ensure your .streamlit/secrets.toml (local) or Cloud Secrets are set up.")
    st.stop()

# --- 2. PAGE SETUP ---
st.set_page_config(page_title="Stock Stream 2026", layout="wide")
st.title("🏛️ Real-Time Portfolio Dashboard")

# Initialize a counter in session state to prevent Plotly Duplicate ID errors
if "run_count" not in st.session_state:
    st.session_state.run_count = 0

# Sidebar for user input
st.sidebar.header("Portfolio Config")
default_portfolio = "AAPL:10, TSLA:5, NVDA:20, BTC/USD:0.1"
user_input = st.sidebar.text_area("Format: TICKER:SHARES", default_portfolio)
refresh_rate = st.sidebar.slider("Refresh Speed (sec)", 5, 60, 15)

# --- 3. DATA FETCHING LOGIC ---
def get_live_portfolio_data(portfolio_map):
    tickers = list(portfolio_map.keys())
    # Fetches latest minute bars for all tickers
    bars = alpaca.get_latest_bars(tickers)
    
    data_rows = []
    total_val = 0
    
    for ticker, shares in portfolio_map.items():
        if ticker in bars:
            price = bars[ticker].c  # 'c' is the close price
            val = price * shares
            total_val += val
            data_rows.append({
                "Ticker": ticker,
                "Price": price,
                "Value": val,
                "Shares": shares
            })
    return pd.DataFrame(data_rows), total_val

# --- 4. MAIN UI LOOP ---
# Parse input into a dictionary
portfolio_dict = {}
try:
    for item in user_input.split(","):
        if ":" in item:
            t, s = item.split(":")
            portfolio_dict[t.strip().upper()] = float(s.strip())
except Exception as e:
    st.sidebar.error("Formatting error in ticker list.")

# Placeholder to update content without refreshing the whole page
dashboard_container = st.empty()

if portfolio_dict:
    while True:
        try:
            st.session_state.run_count += 1
            df, total_value = get_live_portfolio_data(portfolio_dict)
            
            with dashboard_container.container():
                # Top Level Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Portfolio Value", f"${total_value:,.2f}")
                m2.metric("Assets Tracked", len(df))
                m3.metric("Last Feed Update", time.strftime("%H:%M:%S"))
                
                # Visual Layout
                col_chart, col_table = st.columns([1, 1])
                
                with col_chart:
                    st.subheader("Asset Allocation")
                    fig = px.pie(df, values='Value', names='Ticker', hole=0.5, template="plotly_dark")
                    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                    # FIXED: Added unique key to prevent ID duplication
                    st.plotly_chart(fig, use_container_width=True, key=f"pie_{st.session_state.run_count}")
                
                with col_table:
                    st.subheader("Holdings Detail")
                    # Formatted display
                    display_df = df.copy()
                    display_df['Price'] = display_df['Price'].map('${:,.2f}'.format)
                    display_df['Value'] = display_df['Value'].map('${:,.2f}'.format)
                    st.dataframe(display_df, use_container_width=True, hide_index=True)

            time.sleep(refresh_rate)

        except Exception as e:
            st.error(f"Stream interrupted: {e}")
            break
else:
    st.info("👈 Enter your tickers and shares in the sidebar
