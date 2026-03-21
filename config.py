"""
Configuration settings for Stock Market Analytics Platform
"""

# Stock Configuration
DEFAULT_SYMBOL = "AAPL"
SUPPORTED_SYMBOLS = ["AAPL", "TSLA", "SPY", "QQQ", "MSFT", "GOOGL", "AMZN", "META"]

# Technical Indicators
SMA_PERIOD = 20
EMA_PERIOD = 20
RSI_PERIOD = 14
MOMENTUM_PERIOD = 10

# Model Configuration
LAG_FEATURES = 5
N_ESTIMATORS = 100
RANDOM_STATE = 42

# Export Configuration
EXPORT_PATH = "exports/stocks.xlsx"

# API Configuration (Placeholders)
SINOTRADE_API_URL = "https://sinotrade.github.io/api"
CLAUDE_API_KEY = "PLACEHOLDER_KEY"