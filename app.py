import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px

# Page Setup
st.set_page_config(page_title="AI Wealth Advisor 2026", layout="wide")
st.title("🏛️ Professional Portfolio Dashboard")

# --- SIDEBAR ---
st.sidebar.header("Portfolio Config")
default_portfolio = "AAPL:10, TSLA:5, BTC-USD:0.1, NVDA:20"
user_input = st.sidebar.text_area("Format: TICKER:SHARES", default_portfolio)

portfolio_dict = {}
try:
    for item in user_input.split(","):
        if ":" in item:
            ticker, shares = item.split(":")
            portfolio_dict[ticker.strip().upper()] = float(shares.strip())
except:
    st.sidebar.error("Formatting error! Use TICKER:SHARES")

# --- DATA & RISK CALCULATION ---
@st.cache_data(ttl=300)
def analyze_portfolio(portfolio):
    current_data, hist_combined = [], pd.DataFrame()
    
    for ticker, shares in portfolio.items():
        try:
            stock = yf.Ticker(ticker)
            h = stock.history(period="1y") # 1 year for risk + trend
            if not h.empty:
                curr_price = h['Close'].iloc[-1]
                prev_price = h['Close'].iloc[-2] if len(h) > 1 else curr_price
                day_change = ((curr_price - prev_price) / prev_price) * 100
                val = curr_price * shares
                
                current_data.append({
                    "Ticker": ticker, "Shares": shares, 
                    "Price": round(curr_price, 2), "Value ($)": round(val, 2), 
                    "Day Change %": round(day_change, 2)
                })
                
                # Build history for trend and risk
                hist_combined[ticker] = h['Close'] * shares
        except Exception as e:
            st.warning(f"Could not load {ticker}: {e}")

    # Aggregating Metrics
    hist_combined['Total'] = hist_combined.sum(axis=1)
    portfolio_returns = hist_combined['Total'].pct_change().dropna()
    
    volatility = portfolio_returns.std() * np.sqrt(252) * 100
    sharpe = (portfolio_returns.mean() / portfolio_returns.std()) * np.sqrt(252)
    
    return pd.DataFrame(current_data), hist_combined['Total'], volatility, sharpe

# --- DASHBOARD UI ---
if portfolio_dict:
    with st.spinner('Updating your financial world...'):
        df, trend, vol, sharpe = analyze_portfolio(portfolio_dict)
    
    # Create the 3 Tabs
    tab_val, tab_perf, tab_ai = st.tabs(["💰 Portfolio Valuation", "📈 Performance Trends", "🤖 AI Advisor"])

    # --- TAB 1: VALUATION ---
    with tab_val:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Total Portfolio Value", f"${trend.iloc[-1]:,.2f}")
            st.metric("Total Assets", len(df))
            st.subheader("Allocation")
            fig_pie = px.pie(df, values='Value ($)', names='Ticker', hole=0.4, template="plotly_dark")
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            st.subheader("Holdings Detail")
            st.dataframe(df, use_container_width=True, hide_index=True)

    # --- TAB 2: PERFORMANCE ---
    with tab_perf:
        st.subheader("30-Day Value History")
        # Just the last 30 entries for the trend line
        trend_30 = trend.last('30D') if hasattr(trend.index, 'freq') else trend.tail(30)
        fig_line = px.line(trend_30, title="Portfolio Growth Trend", labels={'value': 'Total Value ($)', 'Date': 'Date'}, template="plotly_dark")
        fig_line.update_traces(line_color='#00d4ff', line_width=4)
        st.plotly_chart(fig_line, use_container_width=True)

    # --- TAB 3: AI ADVISOR ---
    with tab_ai:
        c1, c2 = st.columns(2)
        c1.metric("Annual Volatility", f"{vol:.1f}%")
        c2.metric("Sharpe Ratio", f"{sharpe:.2f}")
        
        st.divider()
        st.subheader("Gemini Insights")
        risk_level = "High" if vol > 35 else "Balanced" if vol > 15 else "Conservative"
        
        st.info(f"**Strategy Profile:** {risk_level}")
        if sharpe > 2:
            st.success("Your portfolio is highly efficient. You are gaining significant return for the risk taken.")
        elif vol > 40:
            st.warning("Your portfolio has high 'swing' potential. Be prepared for short-term 10-20% dips.")
        else:
            st.write("Your portfolio is currently tracking within normal market risk parameters.")

else:
    st.info("👈 Please configure your portfolio in the sidebar.")
