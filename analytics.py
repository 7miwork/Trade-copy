"""
Analytics module for computing technical indicators
"""

import pandas as pd
import numpy as np
from config import SMA_PERIOD, EMA_PERIOD, RSI_PERIOD, MOMENTUM_PERIOD


def calculate_sma(df, period=SMA_PERIOD):
    """
    Calculate Simple Moving Average
    
    Args:
        df (pd.DataFrame): DataFrame with 'Close' column
        period (int): Period for SMA calculation
    
    Returns:
        pd.Series: SMA values
    """
    return df['Close'].rolling(window=period).mean()


def calculate_ema(df, period=EMA_PERIOD):
    """
    Calculate Exponential Moving Average
    
    Args:
        df (pd.DataFrame): DataFrame with 'Close' column
        period (int): Period for EMA calculation
    
    Returns:
        pd.Series: EMA values
    """
    return df['Close'].ewm(span=period, adjust=False).mean()


def calculate_rsi(df, period=RSI_PERIOD):
    """
    Calculate Relative Strength Index
    
    Args:
        df (pd.DataFrame): DataFrame with 'Close' column
        period (int): Period for RSI calculation
    
    Returns:
        pd.Series: RSI values (0-100)
    """
    delta = df['Close'].diff()
    
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_momentum(df, period=MOMENTUM_PERIOD):
    """
    Calculate Price Momentum
    
    Args:
        df (pd.DataFrame): DataFrame with 'Close' column
        period (int): Period for momentum calculation
    
    Returns:
        pd.Series: Momentum values
    """
    return df['Close'] - df['Close'].shift(period)


def calculate_macd(df, fast=12, slow=26, signal=9):
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    Args:
        df (pd.DataFrame): DataFrame with 'Close' column
        fast (int): Fast EMA period
        slow (int): Slow EMA period
        signal (int): Signal line period
    
    Returns:
        tuple: (MACD line, Signal line, Histogram)
    """
    ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(df, period=20, std_dev=2):
    """
    Calculate Bollinger Bands
    
    Args:
        df (pd.DataFrame): DataFrame with 'Close' column
        period (int): Period for SMA
        std_dev (int): Number of standard deviations
    
    Returns:
        tuple: (Upper band, Middle band, Lower band)
    """
    middle = df['Close'].rolling(window=period).mean()
    std = df['Close'].rolling(window=period).std()
    
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    
    return upper, middle, lower


def add_all_indicators(df):
    """
    Add all technical indicators to the DataFrame
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data
    
    Returns:
        pd.DataFrame: DataFrame with added indicator columns
    """
    df = df.copy()
    
    # Calculate indicators
    df['SMA'] = calculate_sma(df)
    df['EMA'] = calculate_ema(df)
    df['RSI'] = calculate_rsi(df)
    df['Momentum'] = calculate_momentum(df)
    
    # MACD
    macd_line, signal_line, histogram = calculate_macd(df)
    df['MACD'] = macd_line
    df['MACD_Signal'] = signal_line
    df['MACD_Histogram'] = histogram
    
    # Bollinger Bands
    upper, middle, lower = calculate_bollinger_bands(df)
    df['BB_Upper'] = upper
    df['BB_Middle'] = middle
    df['BB_Lower'] = lower
    
    # Drop rows with NaN values from indicator calculations
    df = df.dropna()
    
    print(f"Added indicators: SMA({SMA_PERIOD}), EMA({EMA_PERIOD}), RSI({RSI_PERIOD}), Momentum({MOMENTUM_PERIOD})")
    print(f"Data points after indicators: {len(df)}")
    
    return df


def get_indicator_summary(df):
    """
    Get a summary of current indicator values
    
    Args:
        df (pd.DataFrame): DataFrame with indicators
    
    Returns:
        dict: Dictionary with indicator summaries
    """
    if df.empty:
        return {}
    
    latest = df.iloc[-1]
    
    return {
        "current_price": round(latest['Close'], 2),
        "sma": round(latest['SMA'], 2) if 'SMA' in latest else None,
        "ema": round(latest['EMA'], 2) if 'EMA' in latest else None,
        "rsi": round(latest['RSI'], 2) if 'RSI' in latest else None,
        "momentum": round(latest['Momentum'], 2) if 'Momentum' in latest else None,
        "macd": round(latest['MACD'], 2) if 'MACD' in latest else None,
        "macd_signal": round(latest['MACD_Signal'], 2) if 'MACD_Signal' in latest else None,
        "bb_upper": round(latest['BB_Upper'], 2) if 'BB_Upper' in latest else None,
        "bb_lower": round(latest['BB_Lower'], 2) if 'BB_Lower' in latest else None
    }


if __name__ == "__main__":
    # Test the analytics
    from data_loader import get_stock_data
    
    df = get_stock_data("AAPL")
    df = add_all_indicators(df)
    
    print("\nData with Indicators:")
    print(df[['Close', 'SMA', 'EMA', 'RSI', 'Momentum']].tail())
    
    print("\nIndicator Summary:")
    summary = get_indicator_summary(df)
    for key, value in summary.items():
        print(f"  {key}: {value}")