import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px

# Page Setup
st.set_page_config(page_title="AI Wealth Advisor 2026", layout="wide")
st.title("🛡️ AI-Powered Portfolio Advisor")

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
    st.sidebar.error("Formatting error!")

# --- DATA & RISK CALCULATION ---
@st.cache_data(ttl=300)
def analyze_portfolio(portfolio):
    data, hist_combined = [], pd.DataFrame()
    
    for ticker, shares in portfolio.items():
        stock = yf.Ticker(ticker)
        h = stock.history(period="1y") # Need 1 year for risk metrics
        if not h.empty:
            price = h['Close'].iloc[-1]
            data.append({"Ticker": ticker, "Shares": shares, "Value": price * shares, "Returns": h['Close'].pct_change()})
            
            ticker_val_history = h['Close'] * shares
            hist_combined[ticker] = ticker_val_history

    # Calculate Portfolio Daily Returns
    hist_combined['Total'] = hist_combined.sum(axis=1)
    portfolio_returns = hist_combined['Total'].pct_change().dropna()
    
    # Risk Metrics
    volatility = portfolio_returns.std() * np.sqrt(252) * 100 # Annualized %
    sharpe = (portfolio_returns.mean() / portfolio_returns.std()) * np.sqrt(252)
    
    return pd.DataFrame(data), hist_combined['Total'], volatility, sharpe

# --- DASHBOARD UI ---
if portfolio_dict:
    df, trend, vol, sharpe = analyze_portfolio(portfolio_dict)
    
    # 1. Summary Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Value", f"${trend.iloc[-1]:,.2f}")
    c2.metric("Annual Volatility", f"{vol:.1f}%", help="Higher % means more price swings.")
    c3.metric("Sharpe Ratio", f"{sharpe:.2f}", help="Above 1.0 is good, above 2.0 is excellent.")

    # 2. Performance Trend
    st.plotly_chart(px.line(trend, title="1-Year Portfolio Growth", template="plotly_dark"), use_container_width=True)

    # 3. AI RISK ANALYSIS SECTION
    st.divider()
    st.subheader("🤖 Gemini AI Risk Summary")
    
    # Logic to generate AI-style advice based on metrics
    risk_level = "High" if vol > 30 else "Moderate" if vol > 15 else "Low"
    advice = ""
    if sharpe < 1:
        advice = "Your risk-adjusted returns are low. Consider diversifying into less volatile assets."
    elif vol > 40:
        advice = "Extreme volatility detected. Ensure you have a long-term horizon or a higher cash reserve."
    else:
        advice = "Your portfolio shows a healthy balance of growth and stability."

    st.info(f"**Risk Profile:** {risk_level} Risk\n\n**AI Insight:** {advice}")

    # 4. Allocation
    st.plotly_chart(px.pie(df, values='Value', names='Ticker', title="Asset Allocation", hole=0.4), use_container_width=True)

else:
    st.info("Enter tickers in the sidebar to begin.")
