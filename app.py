"""
Stock Market Analytics Platform - Flask Application
REST API designed for future mobile app integration
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime
import json
import os
import pandas as pd
import threading
import time
from functools import wraps

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

# Cache for analysis results (symbol -> {result, timestamp})
analysis_cache = {}
CACHE_DURATION = 300  # 5 minutes cache

# Multi-language translations
TRANSLATIONS = {
    'en': {
        'title': '📈 Stock Analytics Platform',
        'subtitle': 'AI-Powered Stock Market Analysis & Forecasting',
        'select_stock': 'Select Stock:',
        'analyze': 'Analyze',
        'analyzing': 'Analyzing...',
        'current_price': 'Current Price',
        'predicted_price': 'Predicted Price',
        'price_change': 'Price Change',
        'confidence': 'Confidence',
        'technical_indicators': 'Technical Indicators',
        'ai_analysis': '🤖 AI Analysis',
        'risk_assessment': '⚠️ Risk Assessment',
        'risk_level': 'Risk Level:',
        'price_history': 'Price History (Last 30 Days)',
        'analysis_history': 'Analysis History',
        'time': 'Time',
        'symbol': 'Symbol',
        'current': 'Current',
        'predicted': 'Predicted',
        'signal': 'Signal',
        'no_history': 'No analysis history yet. Select a stock to begin.',
        'error': '⚠️ Error',
        'loading': 'Loading analysis...',
        'analysis_complete': 'Analysis complete',
        'analysis_timeout': 'Analysis timeout',
        'analysis_failed': 'Analysis failed',
        'api_endpoints': 'API: /api/analyze | /api/batch | /api/export',
        'footer': 'Stock Analytics Platform | REST API available for mobile integration',
        'buy': 'BUY',
        'sell': 'SELL',
        'hold': 'HOLD',
        'high': 'HIGH',
        'medium': 'MEDIUM',
        'low': 'LOW',
        'oversold': 'OVERSOLD',
        'overbought': 'OVERBOUGHT',
        'neutral': 'NEUTRAL',
        'bullish': 'BULLISH',
        'bearish': 'BEARISH',
        'rsi': 'RSI',
        'sma': 'SMA (20)',
        'ema': 'EMA (20)',
        'macd': 'MACD',
        'momentum': 'Momentum',
        'bollinger': 'Bollinger Bands',
        'model': 'Model:',
        'risk_recommendation': 'Standard position sizing with stop-loss'
    },
    'zh': {
        'title': '📈 股票分析平台',
        'subtitle': 'AI驱动的股票市场分析与预测',
        'select_stock': '选择股票:',
        'analyze': '分析',
        'analyzing': '分析中...',
        'current_price': '当前价格',
        'predicted_price': '预测价格',
        'price_change': '价格变化',
        'confidence': '置信度',
        'technical_indicators': '技术指标',
        'ai_analysis': '🤖 AI分析',
        'risk_assessment': '⚠️ 风险评估',
        'risk_level': '风险等级:',
        'price_history': '价格历史 (最近30天)',
        'analysis_history': '分析历史',
        'time': '时间',
        'symbol': '股票',
        'current': '当前',
        'predicted': '预测',
        'signal': '信号',
        'no_history': '暂无分析历史。选择股票开始分析。',
        'error': '⚠️ 错误',
        'loading': '加载分析中...',
        'analysis_complete': '分析完成',
        'analysis_timeout': '分析超时',
        'analysis_failed': '分析失败',
        'api_endpoints': 'API: /api/analyze | /api/batch | /api/export',
        'footer': '股票分析平台 | REST API可用于移动应用集成',
        'buy': '买入',
        'sell': '卖出',
        'hold': '持有',
        'high': '高',
        'medium': '中',
        'low': '低',
        'oversold': '超卖',
        'overbought': '超买',
        'neutral': '中性',
        'bullish': '看涨',
        'bearish': '看跌',
        'rsi': 'RSI',
        'sma': 'SMA (20)',
        'ema': 'EMA (20)',
        'macd': 'MACD',
        'momentum': '动量',
        'bollinger': '布林带',
        'model': '模型:',
        'risk_recommendation': '标准仓位管理，设置止损'
    }
}


def get_lang():
    """Get language from request parameter or default to English"""
    lang = request.args.get('lang', 'en').lower()
    if lang not in TRANSLATIONS:
        lang = 'en'
    return lang


def t(key, lang=None):
    """Translate a key to the current language"""
    if lang is None:
        lang = get_lang()
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)


def api_response(data=None, error=None, status_code=200, lang='en'):
    """
    Create standardized API response
    
    Args:
        data: Response data (for success)
        error: Error message (for failure)
        status_code: HTTP status code
        lang: Language for messages
    
    Returns:
        tuple: (JSON response, status code)
    """
    response = {"success": error is None}
    if error:
        response["error"] = error
    else:
        response["data"] = data
    return jsonify(response), status_code


def get_cached_result(symbol):
    """Get cached result if still valid"""
    if symbol in analysis_cache:
        cached = analysis_cache[symbol]
        if time.time() - cached['timestamp'] < CACHE_DURATION:
            print(f"[INFO] Using cached result for {symbol}")
            return cached['result']
    return None


def cache_result(symbol, result):
    """Cache the analysis result"""
    analysis_cache[symbol] = {
        'result': result,
        'timestamp': time.time()
    }


def run_analysis_pipeline(symbol, timeout=10):
    """
    Run the complete stock analysis pipeline with timeout protection
    
    Args:
        symbol (str): Stock symbol to analyze
        timeout (int): Maximum time in seconds for analysis
    
    Returns:
        dict: Complete analysis results or error structure
    """
    # Check cache first
    cached = get_cached_result(symbol)
    if cached:
        return cached
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result = [None]  # Use list to allow modification in nested function
    
    def analyze():
        try:
            # Step 1: Load data
            print(f"[INFO] Loading data for {symbol}")
            try:
                df = get_stock_data(symbol)
                if df is None or df.empty:
                    raise ValueError(f"No data returned for {symbol}")
                print(f"[INFO] Loaded {len(df)} data points for {symbol}")
            except Exception as e:
                print(f"[ERROR] Failed to load data for {symbol}: {str(e)}")
                result[0] = {
                    "symbol": symbol,
                    "success": False,
                    "error": f"Data loading failed: {str(e)}",
                    "timestamp": timestamp
                }
                return
            
            # Step 2: Compute indicators
            print(f"[INFO] Computing indicators for {symbol}")
            try:
                df = add_all_indicators(df)
                if df is None or df.empty:
                    raise ValueError("Indicator calculation returned empty data")
                print(f"[INFO] Indicators computed successfully, {len(df)} data points remaining")
            except Exception as e:
                print(f"[ERROR] Failed to compute indicators for {symbol}: {str(e)}")
                result[0] = {
                    "symbol": symbol,
                    "success": False,
                    "error": f"Indicator calculation failed: {str(e)}",
                    "timestamp": timestamp
                }
                return
            
            # Step 3: Train model
            print(f"[INFO] Training model for {symbol}")
            try:
                model, X, y = train_random_forest(df)
                if model is None:
                    raise ValueError("Model training returned None")
                print(f"[INFO] Model trained successfully for {symbol}")
            except Exception as e:
                print(f"[ERROR] Failed to train model for {symbol}: {str(e)}")
                result[0] = {
                    "symbol": symbol,
                    "success": False,
                    "error": f"Model training failed: {str(e)}",
                    "timestamp": timestamp
                }
                return
            
            # Step 4: Predict next price
            print(f"[INFO] Predicting next price for {symbol}")
            try:
                predicted_price = predict_next_price(model, df)
                if predicted_price is None or not isinstance(predicted_price, (int, float)):
                    raise ValueError("Prediction returned invalid value")
                print(f"[INFO] Predicted price for {symbol}: ${predicted_price:.2f}")
            except Exception as e:
                print(f"[ERROR] Failed to predict price for {symbol}: {str(e)}")
                result[0] = {
                    "symbol": symbol,
                    "success": False,
                    "error": f"Price prediction failed: {str(e)}",
                    "timestamp": timestamp
                }
                return
            
            # Step 5: Generate signal
            print(f"[INFO] Generating trading signal for {symbol}")
            try:
                current_price = df['Close'].iloc[-1]
                signal = generate_signal(current_price, predicted_price)
                print(f"[INFO] Signal for {symbol}: {signal}")
            except Exception as e:
                print(f"[ERROR] Failed to generate signal for {symbol}: {str(e)}")
                result[0] = {
                    "symbol": symbol,
                    "success": False,
                    "error": f"Signal generation failed: {str(e)}",
                    "timestamp": timestamp
                }
                return
            
            # Step 6: Get indicator signals
            print(f"[INFO] Analyzing indicator signals for {symbol}")
            try:
                indicator_signals = analyze_indicators(df)
            except Exception as e:
                print(f"[WARNING] Failed to analyze indicators for {symbol}: {str(e)}")
                indicator_signals = {}
            
            # Step 7: Get combined signal
            print(f"[INFO] Computing combined signal for {symbol}")
            try:
                combined = get_combined_signal(current_price, predicted_price, indicator_signals)
            except Exception as e:
                print(f"[WARNING] Failed to get combined signal for {symbol}: {str(e)}")
                combined = {"confidence": "MEDIUM"}
            
            # Step 8: Get indicator summary
            print(f"[INFO] Getting indicator summary for {symbol}")
            try:
                indicators = get_indicator_summary(df)
            except Exception as e:
                print(f"[WARNING] Failed to get indicator summary for {symbol}: {str(e)}")
                indicators = {}
            
            # Step 9: Get AI analysis
            print(f"[INFO] Getting AI analysis for {symbol}")
            try:
                ai_data = {
                    "symbol": symbol,
                    "current_price": current_price,
                    "predicted_price": predicted_price,
                    "signal": signal,
                    "indicators": indicators
                }
                ai_analysis = get_ai_analysis(ai_data)
            except Exception as e:
                print(f"[WARNING] Failed to get AI analysis for {symbol}: {str(e)}")
                ai_analysis = {"analysis": "AI analysis unavailable", "is_placeholder": True}
            
            # Step 10: Get risk assessment
            print(f"[INFO] Getting risk assessment for {symbol}")
            try:
                risk = get_risk_assessment(ai_data)
            except Exception as e:
                print(f"[WARNING] Failed to get risk assessment for {symbol}: {str(e)}")
                risk = {"risk_level": "unknown", "is_placeholder": True}
            
            # Calculate price change
            price_change = predicted_price - current_price
            price_change_pct = (price_change / current_price) * 100
            
            # Get feature importance
            print(f"[INFO] Getting feature importance for {symbol}")
            try:
                feature_importance = get_feature_importance(model, df)
            except Exception as e:
                print(f"[WARNING] Failed to get feature importance for {symbol}: {str(e)}")
                feature_importance = {}
            
            # Get last 30 days of prices for chart
            try:
                prices = df['Close'].tail(30).tolist()
                dates = [d.strftime('%Y-%m-%d') for d in df.index[-30:]]
            except Exception as e:
                print(f"[WARNING] Failed to get price history for {symbol}: {str(e)}")
                prices = []
                dates = []
            
            print(f"[INFO] Analysis completed successfully for {symbol}")
            
            res = {
                "symbol": symbol,
                "success": True,
                "current_price": round(current_price, 2),
                "predicted_price": round(predicted_price, 2),
                "signal": signal,
                "signal_color": get_signal_color(signal),
                "signal_description": get_signal_description(signal),
                "confidence": combined.get('confidence', 'MEDIUM'),
                "price_change": round(price_change, 2),
                "price_change_pct": round(price_change_pct, 2),
                "indicators": indicators,
                "indicator_signals": indicator_signals,
                "ai_analysis": ai_analysis,
                "risk_assessment": risk,
                "feature_importance": feature_importance,
                "prices": prices,
                "dates": dates,
                "timestamp": timestamp
            }
            
            # Cache the result
            cache_result(symbol, res)
            result[0] = res
            
        except Exception as e:
            print(f"[ERROR] Unexpected error in pipeline for {symbol}: {str(e)}")
            result[0] = {
                "symbol": symbol,
                "success": False,
                "error": f"Pipeline failed: {str(e)}",
                "timestamp": timestamp
            }
    
    # Run analysis in a thread with timeout
    thread = threading.Thread(target=analyze)
    thread.start()
    thread.join(timeout=timeout)
    
    if thread.is_alive():
        print(f"[ERROR] Analysis timeout for {symbol} after {timeout} seconds")
        return {
            "symbol": symbol,
            "success": False,
            "error": "Analysis timeout",
            "timestamp": timestamp
        }
    
    return result[0]


# ==================== WEB ROUTES ====================

@app.route('/')
def index():
    """
    Main dashboard route
    """
    lang = get_lang()
    symbol = request.args.get('symbol', DEFAULT_SYMBOL)
    result = run_analysis_pipeline(symbol)
    
    # Add to history (only if successful)
    if result and result.get('success', False):
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
        symbols=SUPPORTED_SYMBOLS,
        lang=lang,
        t=lambda key: t(key, lang)
    )


# ==================== API ENDPOINTS ====================

@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint for monitoring
    
    Returns:
        JSON: Health status
    """
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })


@app.route('/api/analyze', methods=['GET'])
def api_analyze():
    """
    Analyze a single stock symbol
    
    Query Parameters:
        symbol (str): Stock symbol to analyze
        lang (str): Language code (en/zh)
    
    Returns:
        JSON: Analysis results
    """
    try:
        lang = get_lang()
        symbol = request.args.get('symbol', '').strip().upper()
        
        # Validate symbol input
        if not symbol:
            return api_response(error="Symbol parameter is required", status_code=400, lang=lang)
        
        if symbol not in SUPPORTED_SYMBOLS:
            return api_response(
                error=f"Symbol '{symbol}' not supported. Supported symbols: {', '.join(SUPPORTED_SYMBOLS)}",
                status_code=400,
                lang=lang
            )
        
        # Run analysis pipeline with timeout
        result = run_analysis_pipeline(symbol, timeout=10)
        
        # Check if analysis was successful
        if not result or not result.get('success', False):
            error_msg = result.get('error', 'Analysis failed') if result else 'Analysis failed'
            return api_response(error=error_msg, status_code=500, lang=lang)
        
        return api_response(data=result, lang=lang)
    
    except Exception as e:
        print(f"[ERROR] Unexpected error in /api/analyze: {str(e)}")
        return api_response(error=f"Internal server error: {str(e)}", status_code=500, lang=get_lang())


@app.route('/api/batch', methods=['GET'])
def api_batch():
    """
    Analyze multiple stock symbols
    
    Query Parameters:
        symbols (str): Comma-separated list of symbols
        lang (str): Language code (en/zh)
    
    Returns:
        JSON: Analysis results for all symbols
    """
    try:
        lang = get_lang()
        symbols_param = request.args.get('symbols', '').strip()
        
        # Parse symbols
        if symbols_param:
            symbols = [s.strip().upper() for s in symbols_param.split(',') if s.strip()]
        else:
            symbols = SUPPORTED_SYMBOLS[:4]
        
        if not symbols:
            return api_response(error="No symbols provided", status_code=400, lang=lang)
        
        results = []
        successful = 0
        failed = 0
        
        for symbol in symbols:
            try:
                if symbol not in SUPPORTED_SYMBOLS:
                    print(f"[WARNING] Skipping unsupported symbol: {symbol}")
                    results.append({
                        "symbol": symbol,
                        "success": False,
                        "error": f"Symbol '{symbol}' not supported"
                    })
                    failed += 1
                    continue
                
                result = run_analysis_pipeline(symbol, timeout=10)
                results.append(result)
                
                if result and result.get('success', False):
                    successful += 1
                else:
                    failed += 1
                    
            except Exception as e:
                print(f"[ERROR] Failed to analyze {symbol}: {str(e)}")
                results.append({
                    "symbol": symbol,
                    "success": False,
                    "error": f"Analysis failed: {str(e)}"
                })
                failed += 1
        
        return api_response(data={
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "total": len(symbols),
            "successful": successful,
            "failed": failed,
            "results": results
        }, lang=lang)
    
    except Exception as e:
        print(f"[ERROR] Unexpected error in /api/batch: {str(e)}")
        return api_response(error=f"Internal server error: {str(e)}", status_code=500, lang=get_lang())


@app.route('/api/export', methods=['GET'])
def api_export():
    """
    Export analysis results to Excel file
    
    Query Parameters:
        symbols (str): Comma-separated list of symbols
        lang (str): Language code (en/zh)
    
    Returns:
        JSON: Export status and file path
    """
    try:
        lang = get_lang()
        symbols_param = request.args.get('symbols', '').strip()
        
        # Parse symbols
        if symbols_param:
            symbols = [s.strip().upper() for s in symbols_param.split(',') if s.strip()]
        else:
            symbols = SUPPORTED_SYMBOLS
        
        if not symbols:
            return api_response(error="No symbols provided", status_code=400, lang=lang)
        
        # Run analysis for all symbols
        export_data = []
        for symbol in symbols:
            try:
                if symbol not in SUPPORTED_SYMBOLS:
                    print(f"[WARNING] Skipping unsupported symbol: {symbol}")
                    continue
                
                result = run_analysis_pipeline(symbol, timeout=10)
                if result and result.get('success', False):
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
            except Exception as e:
                print(f"[WARNING] Failed to export {symbol}: {str(e)}")
                continue
        
        if not export_data:
            return api_response(error="No data to export", status_code=400, lang=lang)
        
        # Create exports directory if it doesn't exist
        try:
            os.makedirs(os.path.dirname(EXPORT_PATH), exist_ok=True)
        except Exception as e:
            print(f"[ERROR] Failed to create export directory: {str(e)}")
            return api_response(error="Failed to create export directory", status_code=500, lang=lang)
        
        # Export to Excel
        try:
            df = pd.DataFrame(export_data)
            df.to_excel(EXPORT_PATH, index=False, sheet_name='Stock Analysis')
            print(f"[INFO] Exported {len(export_data)} records to {EXPORT_PATH}")
        except Exception as e:
            print(f"[ERROR] Failed to export to Excel: {str(e)}")
            return api_response(error="Failed to export data", status_code=500, lang=lang)
        
        return api_response(data={
            "status": "success",
            "file": EXPORT_PATH,
            "records": len(export_data),
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }, lang=lang)
    
    except Exception as e:
        print(f"[ERROR] Unexpected error in /api/export: {str(e)}")
        return api_response(error=f"Internal server error: {str(e)}", status_code=500, lang=get_lang())


@app.route('/api/symbols', methods=['GET'])
def api_symbols():
    """
    Get list of supported stock symbols
    
    Returns:
        JSON: List of supported symbols
    """
    return api_response(data={
        "symbols": SUPPORTED_SYMBOLS,
        "count": len(SUPPORTED_SYMBOLS)
    }, lang=get_lang())


@app.route('/api/history', methods=['GET'])
def api_history():
    """
    Get analysis history
    
    Returns:
        JSON: List of recent analyses
    """
    return api_response(data={
        "history": list(reversed(analysis_history)),
        "count": len(analysis_history)
    }, lang=get_lang())


# ==================== ERROR HANDLERS ====================

@app.errorhandler(Exception)
def handle_exception(e):
    """
    Global exception handler for unhandled errors
    """
    print(f"[ERROR] Unhandled exception: {str(e)}")
    return api_response(error="Internal server error", status_code=500, lang=get_lang())


@app.errorhandler(404)
def not_found(e):
    """
    Handle 404 errors
    """
    return api_response(error="Endpoint not found", status_code=404, lang=get_lang())


@app.errorhandler(500)
def internal_error(e):
    """
    Handle 500 errors
    """
    print(f"[ERROR] Internal server error: {str(e)}")
    return api_response(error="Internal server error", status_code=500, lang=get_lang())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"[INFO] Starting Stock Analytics API on port {port}")
    print(f"[INFO] Supported symbols: {', '.join(SUPPORTED_SYMBOLS)}")
    app.run(host="0.0.0.0", port=port)