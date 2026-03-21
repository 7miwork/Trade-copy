"""
Stock Market Analytics Platform - Flask Application
REST API designed for future mobile app integration
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime
import json
import os
import pandas as pd

from data_loader import get_stock_data, get_multiple_stocks
from analytics import add_all_indicators, get_indicator_summary
from model import train_random_forest, predict_next_price, get_feature_importance
from strategy import generate_signal, get_signal_color, get_signal_description, analyze_indicators, get_combined_signal
from ai_placeholder import get_ai_analysis, get_risk_assessment
from config import SUPPORTED_SYMBOLS, EXPORT_PATH, DEFAULT_SYMBOL

app = Flask(__name__)
app.secret_key = 'stock-analytics-secret-key-2024'

# Store analysis history
analysis_history = []


def run_analysis_pipeline(symbol):
    """
    Run the complete stock analysis pipeline
    
    Args:
        symbol (str): Stock symbol to analyze
    
    Returns:
        dict: Complete analysis results
    """
    try:
        # Step 1: Load data
        print(f"Loading data for {symbol}...")
        df = get_stock_data(symbol)
        
        # Step 2: Compute indicators
        print("Computing indicators...")
        df = add_all_indicators(df)
        
        # Step 3: Train model
        print("Training model...")
        model, X, y = train_random_forest(df)
        
        # Step 4: Predict next price
        print("Predicting next price...")
        predicted_price = predict_next_price(model, df)
        
        # Step 5: Generate signal
        current_price = df['Close'].iloc[-1]
        signal = generate_signal(current_price, predicted_price)
        
        # Step 6: Get indicator signals
        indicator_signals = analyze_indicators(df)
        
        # Step 7: Get combined signal
        combined = get_combined_signal(current_price, predicted_price, indicator_signals)
        
        # Step 8: Get indicator summary
        indicators = get_indicator_summary(df)
        
        # Step 9: Get AI analysis
        ai_data = {
            "symbol": symbol,
            "current_price": current_price,
            "predicted_price": predicted_price,
            "signal": signal,
            "indicators": indicators
        }
        ai_analysis = get_ai_analysis(ai_data)
        
        # Step 10: Get risk assessment
        risk = get_risk_assessment(ai_data)
        
        # Calculate price change
        price_change = predicted_price - current_price
        price_change_pct = (price_change / current_price) * 100
        
        # Get feature importance
        feature_importance = get_feature_importance(model, df)
        
        # Get last 30 days of prices for chart
        prices = df['Close'].tail(30).tolist()
        dates = [d.strftime('%Y-%m-%d') for d in df.index[-30:]]
        
        result = {
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "predicted_price": round(predicted_price, 2),
            "signal": signal,
            "signal_color": get_signal_color(signal),
            "signal_description": get_signal_description(signal),
            "confidence": combined['confidence'],
            "price_change": round(price_change, 2),
            "price_change_pct": round(price_change_pct, 2),
            "indicators": indicators,
            "indicator_signals": indicator_signals,
            "ai_analysis": ai_analysis,
            "risk_assessment": risk,
            "feature_importance": feature_importance,
            "prices": prices,
            "dates": dates,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return result
    
    except Exception as e:
        print(f"Error in pipeline for {symbol}: {e}")
        return {
            "symbol": symbol,
            "error": str(e),
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


# ==================== WEB ROUTES ====================

@app.route('/')
def index():
    """
    Main dashboard route
    """
    symbol = request.args.get('symbol', DEFAULT_SYMBOL)
    result = run_analysis_pipeline(symbol)
    
    # Add to history
    if 'error' not in result:
        analysis_history.append({
            'timestamp': result['timestamp'],
            'symbol': result['symbol'],
            'current_price': result['current_price'],
            'predicted_price': result['predicted_price'],
            'signal': result['signal']
        })
        
        # Keep only last 20 analyses
        if len(analysis_history) > 20:
            analysis_history.pop(0)
    
    # Reverse history to show newest first
    history_display = list(reversed(analysis_history))
    
    return render_template(
        'index.html',
        result=result,
        history=history_display,
        symbols=SUPPORTED_SYMBOLS
    )


# ==================== API ENDPOINTS ====================

@app.route('/api/analyze', methods=['GET'])
def api_analyze():
    """
    Analyze a single stock symbol
    
    Query Parameters:
        symbol (str): Stock symbol to analyze
    
    Returns:
        JSON: Analysis results
    """
    symbol = request.args.get('symbol', DEFAULT_SYMBOL).upper()
    
    if symbol not in SUPPORTED_SYMBOLS:
        return jsonify({
            "error": f"Symbol {symbol} not supported. Supported: {SUPPORTED_SYMBOLS}"
        }), 400
    
    result = run_analysis_pipeline(symbol)
    
    if 'error' in result:
        return jsonify(result), 500
    
    return jsonify(result)


@app.route('/api/batch', methods=['GET'])
def api_batch():
    """
    Analyze multiple stock symbols
    
    Query Parameters:
        symbols (str): Comma-separated list of symbols
    
    Returns:
        JSON: Analysis results for all symbols
    """
    symbols_param = request.args.get('symbols', ','.join(SUPPORTED_SYMBOLS[:4]))
    symbols = [s.strip().upper() for s in symbols_param.split(',')]
    
    results = []
    for symbol in symbols:
        if symbol in SUPPORTED_SYMBOLS:
            result = run_analysis_pipeline(symbol)
            results.append(result)
    
    return jsonify({
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "count": len(results),
        "results": results
    })


@app.route('/api/export', methods=['GET'])
def api_export():
    """
    Export analysis results to Excel file
    
    Query Parameters:
        symbols (str): Comma-separated list of symbols
    
    Returns:
        JSON: Export status and file path
    """
    symbols_param = request.args.get('symbols', ','.join(SUPPORTED_SYMBOLS))
    symbols = [s.strip().upper() for s in symbols_param.split(',')]
    
    # Run analysis for all symbols
    export_data = []
    for symbol in symbols:
        if symbol in SUPPORTED_SYMBOLS:
            result = run_analysis_pipeline(symbol)
            if 'error' not in result:
                export_data.append({
                    'Symbol': result['symbol'],
                    'Current Price': result['current_price'],
                    'Predicted Price': result['predicted_price'],
                    'Signal': result['signal'],
                    'Confidence': result['confidence'],
                    'Price Change %': result['price_change_pct'],
                    'RSI': result['indicators'].get('rsi', 'N/A'),
                    'SMA': result['indicators'].get('sma', 'N/A'),
                    'EMA': result['indicators'].get('ema', 'N/A'),
                    'Timestamp': result['timestamp']
                })
    
    if not export_data:
        return jsonify({"error": "No data to export"}), 400
    
    # Create exports directory if it doesn't exist
    os.makedirs(os.path.dirname(EXPORT_PATH), exist_ok=True)
    
    # Export to Excel
    df = pd.DataFrame(export_data)
    df.to_excel(EXPORT_PATH, index=False, sheet_name='Stock Analysis')
    
    return jsonify({
        "status": "success",
        "file": EXPORT_PATH,
        "records": len(export_data),
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })


@app.route('/api/symbols', methods=['GET'])
def api_symbols():
    """
    Get list of supported stock symbols
    
    Returns:
        JSON: List of supported symbols
    """
    return jsonify({
        "symbols": SUPPORTED_SYMBOLS,
        "count": len(SUPPORTED_SYMBOLS)
    })


@app.route('/api/history', methods=['GET'])
def api_history():
    """
    Get analysis history
    
    Returns:
        JSON: List of recent analyses
    """
    return jsonify({
        "history": list(reversed(analysis_history)),
        "count": len(analysis_history)
    })


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Stock Market Analytics Platform")
    print("=" * 60)
    print(f"Supported symbols: {SUPPORTED_SYMBOLS}")
    print(f"Starting server at http://127.0.0.1:5000")
    print("=" * 60)
    print("\nAPI Endpoints:")
    print("  GET  /              - Web Dashboard")
    print("  GET  /api/analyze   - Analyze single stock")
    print("  GET  /api/batch     - Analyze multiple stocks")
    print("  GET  /api/export    - Export to Excel")
    print("  GET  /api/symbols   - List supported symbols")
    print("  GET  /api/history   - Get analysis history")
    print("=" * 60)
    print("\nPress Ctrl+C to stop")
    print("=" * 60)
    
    app.run(debug=True, host='127.0.0.1', port=5000)