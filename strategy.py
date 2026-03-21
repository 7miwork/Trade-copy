"""
Trading strategy module for generating BUY/SELL/HOLD signals
"""


def generate_signal(current_price, predicted_price):
    """
    Generate trading signal based on price prediction
    
    Args:
        current_price (float): Current closing price
        predicted_price (float): Predicted next price
    
    Returns:
        str: Trading signal - 'BUY', 'SELL', or 'HOLD'
    """
    # Calculate percentage change
    price_change_pct = ((predicted_price - current_price) / current_price) * 100
    
    # Define thresholds
    BUY_THRESHOLD = 0.5   # Predicted increase > 0.5%
    SELL_THRESHOLD = -0.5  # Predicted decrease > 0.5%
    
    if price_change_pct > BUY_THRESHOLD:
        return 'BUY'
    elif price_change_pct < SELL_THRESHOLD:
        return 'SELL'
    else:
        return 'HOLD'


def get_signal_color(signal):
    """
    Get the color associated with a trading signal
    
    Args:
        signal (str): Trading signal
    
    Returns:
        str: CSS color value
    """
    colors = {
        'BUY': '#00ff88',    # Green
        'SELL': '#ff4444',   # Red
        'HOLD': '#888888'    # Gray
    }
    return colors.get(signal, '#888888')


def get_signal_description(signal):
    """
    Get a description for the trading signal
    
    Args:
        signal (str): Trading signal
    
    Returns:
        str: Signal description
    """
    descriptions = {
        'BUY': 'Price expected to rise - Consider buying',
        'SELL': 'Price expected to fall - Consider selling',
        'HOLD': 'Price stable - Hold position'
    }
    return descriptions.get(signal, 'Unknown signal')


def analyze_indicators(df):
    """
    Analyze technical indicators for additional signal confirmation
    
    Args:
        df (pd.DataFrame): DataFrame with indicators
    
    Returns:
        dict: Dictionary with indicator-based signals
    """
    if df.empty:
        return {}
    
    latest = df.iloc[-1]
    signals = {}
    
    # RSI analysis
    if 'RSI' in latest:
        rsi = latest['RSI']
        if rsi < 30:
            signals['rsi_signal'] = 'OVERSOLD'
        elif rsi > 70:
            signals['rsi_signal'] = 'OVERBOUGHT'
        else:
            signals['rsi_signal'] = 'NEUTRAL'
    
    # SMA/EMA crossover
    if 'SMA' in latest and 'EMA' in latest:
        if latest['EMA'] > latest['SMA']:
            signals['ma_signal'] = 'BULLISH'
        else:
            signals['ma_signal'] = 'BEARISH'
    
    # MACD analysis
    if 'MACD' in latest and 'MACD_Signal' in latest:
        if latest['MACD'] > latest['MACD_Signal']:
            signals['macd_signal'] = 'BULLISH'
        else:
            signals['macd_signal'] = 'BEARISH'
    
    # Bollinger Bands analysis
    if 'BB_Upper' in latest and 'BB_Lower' in latest:
        price = latest['Close']
        if price > latest['BB_Upper']:
            signals['bb_signal'] = 'OVERBOUGHT'
        elif price < latest['BB_Lower']:
            signals['bb_signal'] = 'OVERSOLD'
        else:
            signals['bb_signal'] = 'NEUTRAL'
    
    return signals


def get_combined_signal(current_price, predicted_price, indicator_signals):
    """
    Get combined signal considering both prediction and indicators
    
    Args:
        current_price (float): Current closing price
        predicted_price (float): Predicted next price
        indicator_signals (dict): Signals from technical indicators
    
    Returns:
        dict: Combined signal analysis
    """
    # Primary signal from prediction
    primary_signal = generate_signal(current_price, predicted_price)
    
    # Count bullish/bearish indicators
    bullish_count = 0
    bearish_count = 0
    
    for key, value in indicator_signals.items():
        if value in ['BULLISH', 'OVERSOLD']:
            bullish_count += 1
        elif value in ['BEARISH', 'OVERBOUGHT']:
            bearish_count += 1
    
    # Determine confidence
    if primary_signal == 'BUY' and bullish_count > bearish_count:
        confidence = 'HIGH'
    elif primary_signal == 'SELL' and bearish_count > bullish_count:
        confidence = 'HIGH'
    elif primary_signal == 'HOLD':
        confidence = 'MEDIUM'
    else:
        confidence = 'LOW'
    
    return {
        'signal': primary_signal,
        'confidence': confidence,
        'bullish_indicators': bullish_count,
        'bearish_indicators': bearish_count,
        'indicator_signals': indicator_signals
    }


if __name__ == "__main__":
    # Test the strategy
    test_cases = [
        (100, 102),   # Should be BUY
        (100, 98),    # Should be SELL
        (100, 100.2), # Should be HOLD
    ]
    
    print("=== Signal Generation Tests ===")
    for current, predicted in test_cases:
        signal = generate_signal(current, predicted)
        change = ((predicted - current) / current) * 100
        print(f"\nCurrent: ${current:.2f}, Predicted: ${predicted:.2f}")
        print(f"Change: {change:.2f}%, Signal: {signal}")
        print(f"Description: {get_signal_description(signal)}")
        print(f"Color: {get_signal_color(signal)}")