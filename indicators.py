"""
Technical indicators module for computing SMA, EMA, and RSI
"""

import pandas as pd
import numpy as np
from config import SMA_PERIOD, EMA_PERIOD, RSI_PERIOD


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


def add_indicators(df):
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
    
    # Drop rows with NaN values from indicator calculations
    df = df.dropna()
    
    print(f"Added indicators: SMA({SMA_PERIOD}), EMA({EMA_PERIOD}), RSI({RSI_PERIOD})")
    print(f"Data points after indicators: {len(df)}")
    
    return df


if __name__ == "__main__":
    # Test the indicators
    from data_loader import load_data
    
    df = load_data()
    df = add_indicators(df)
    print("\nData with Indicators:")
    print(df[['Close', 'SMA', 'EMA', 'RSI']].tail())