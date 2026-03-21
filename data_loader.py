"""
Data loader module for fetching stock data
Supports stocks and ETFs only (NO cryptocurrencies)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import SUPPORTED_SYMBOLS


def generate_mock_stock_data(symbol, days=60):
    """
    Generate realistic mock stock data for testing
    
    Args:
        symbol (str): Stock symbol
        days (int): Number of days of data
    
    Returns:
        pd.DataFrame: DataFrame with OHLCV data
    """
    # Base prices for different stocks
    base_prices = {
        "AAPL": 175.0,
        "TSLA": 250.0,
        "SPY": 450.0,
        "QQQ": 380.0,
        "MSFT": 380.0,
        "GOOGL": 140.0,
        "AMZN": 175.0,
        "META": 500.0
    }
    
    base_price = base_prices.get(symbol, 100.0)
    
    # Generate dates
    end_date = datetime.now()
    dates = [end_date - timedelta(days=i) for i in range(days, 0, -1)]
    
    # Generate price data with realistic volatility
    np.random.seed(hash(symbol) % 2**32)
    
    # Daily returns with slight upward bias
    daily_returns = np.random.normal(0.0005, 0.02, days)
    
    # Calculate prices
    close_prices = [base_price]
    for ret in daily_returns[1:]:
        close_prices.append(close_prices[-1] * (1 + ret))
    
    # Generate OHLCV data
    data = []
    for i, date in enumerate(dates):
        close = close_prices[i]
        high = close * (1 + abs(np.random.normal(0, 0.01)))
        low = close * (1 - abs(np.random.normal(0, 0.01)))
        open_price = low + (high - low) * np.random.random()
        volume = int(np.random.lognormal(15, 1))
        
        data.append({
            "Date": date,
            "Open": round(open_price, 2),
            "High": round(high, 2),
            "Low": round(low, 2),
            "Close": round(close, 2),
            "Volume": volume
        })
    
    df = pd.DataFrame(data)
    df.set_index("Date", inplace=True)
    df.sort_index(inplace=True)
    
    return df


def get_stock_data_from_sinotrade(symbol):
    """
    Placeholder for Sinotrade API integration
    
    TODO: Integrate real Sinotrade API
    Documentation: https://sinotrade.github.io/
    
    Args:
        symbol (str): Stock symbol
    
    Returns:
        pd.DataFrame: DataFrame with OHLCV data (mock for now)
    """
    # TODO: Implement real Sinotrade API call
    # Example implementation:
    # import requests
    # response = requests.get(f"{SINOTRADE_API_URL}/stocks/{symbol}")
    # data = response.json()
    # return pd.DataFrame(data)
    
    print(f"[PLACEHOLDER] Sinotrade API called for {symbol}")
    return generate_mock_stock_data(symbol)


def get_stock_data(symbol, use_yfinance=False):
    """
    Fetch stock data for the given symbol
    
    Args:
        symbol (str): Stock symbol (e.g., AAPL, TSLA, SPY)
        use_yfinance (bool): Whether to try yfinance first
    
    Returns:
        pd.DataFrame: DataFrame with OHLCV data
    """
    # Validate symbol
    if symbol not in SUPPORTED_SYMBOLS:
        print(f"Warning: {symbol} not in supported list. Supported: {SUPPORTED_SYMBOLS}")
    
    # Try yfinance if requested
    if use_yfinance:
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="60d", interval="1d")
            
            if not df.empty:
                print(f"Loaded {len(df)} days of {symbol} data from yfinance")
                return df
        except Exception as e:
            print(f"yfinance failed for {symbol}: {e}")
            print("Falling back to mock data...")
    
    # Use Sinotrade placeholder (returns mock data)
    return get_stock_data_from_sinotrade(symbol)


def get_multiple_stocks(symbols, use_yfinance=False):
    """
    Fetch data for multiple stock symbols
    
    Args:
        symbols (list): List of stock symbols
        use_yfinance (bool): Whether to try yfinance first
    
    Returns:
        dict: Dictionary mapping symbols to DataFrames
    """
    results = {}
    for symbol in symbols:
        try:
            results[symbol] = get_stock_data(symbol, use_yfinance)
        except Exception as e:
            print(f"Error loading {symbol}: {e}")
    return results


if __name__ == "__main__":
    # Test the data loader
    print("Testing data loader...")
    
    # Test single stock
    df = get_stock_data("AAPL")
    print(f"\nAAPL Data Preview:")
    print(df.tail())
    
    # Test multiple stocks
    symbols = ["AAPL", "TSLA", "SPY"]
    data = get_multiple_stocks(symbols)
    print(f"\nLoaded {len(data)} stocks")