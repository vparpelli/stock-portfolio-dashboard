"""Configuration for Stock Portfolio Dashboard"""

# Default tickers for the portfolio
DEFAULT_TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']

# Dashboard settings
DASHBOARD_TITLE = "Stock Portfolio Dashboard"
DASHBOARD_SUBTITLE = "Real-time portfolio tracking using Google Finance API"

# API settings
API_TIMEOUT = 10  # seconds
CACHE_DURATION = 3600  # 1 hour in seconds

# Display settings
CHART_HEIGHT = 500
DATE_FORMAT = "%Y-%m-%d"
CURRENCY = "USD"