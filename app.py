"""
Stock Market Analytics Platform - Flask Application
REST API designed for future mobile app integration
"""

from flask import Flask, render_template, jsonify, request, send_file
from datetime import datetime
import json
import os
import pandas as pd
import threading
import time
from functools import wraps
from werkzeug.utils import secure_filename

from data_loader import get_stock_data, get_multiple_stocks
from analytics import add_all_indicators, get_indicator_summary
from model import train_random_forest, predict_next_price, get_feature_importance
from strategy import generate_signal, get_signal_color, get_signal_description, analyze_indicators, get_combined_signal
from ai_placeholder import get_ai_analysis, get_risk_assessment
from config import SUPPORTED_SYMBOLS, EXPORT_PATH, DEFAULT_SYMBOL
from translations import t, get_all_translations

app = Flask(__name__)
app.secret_key = 'stock-analytics-secret-key-2024'
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20MB max file size

# Store analysis history
analysis_history = []

# Cache for analysis results (symbol -> {result, timestamp})
analysis_cache = {}
CACHE_DURATION = 300  # 5 minutes cache


def get_lang():
    """Get language from request parameter or default to English"""
    lang = request.args.get('lang', 'en').lower()
    if lang not in ['en', 'zh']:
        lang = 'en'
    return lang


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


# ==================== EXCEL UPLOAD & BATCH PROCESSING ====================

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_stock_batch(df):
    """
    Process batch of stocks from Excel file
    
    Args:
        df (pd.DataFrame): DataFrame with columns [code, name]
    
    Returns:
        tuple: (processed_df, report)
    """
    total = len(df)
    successful = 0
    failed = 0
    up_count = 0
    down_count = 0
    hold_count = 0
    top_picks = []
    
    # Initialize result columns
    df['Prediction'] = ''
    df['Confidence'] = ''
    df['Signal'] = ''
    df['Current_Price'] = ''
    df['Predicted_Price'] = ''
    df['Price_Change_Pct'] = ''
    df['Reason'] = ''
    df['Status'] = ''
    
    for index, row in df.iterrows():
        try:
            code = str(row.iloc[0]).strip().upper() if pd.notna(row.iloc[0]) else ''
            name = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
            
            print(f"[INFO] Processing {index + 1}/{total}: {code} ({name})")
            
            if not code:
                df.at[index, 'Status'] = 'Error'
                df.at[index, 'Reason'] = 'Empty stock code'
                failed += 1
                continue
            
            # Run analysis pipeline
            result = run_analysis_pipeline(code, timeout=10)
            
            if result and result.get('success', False):
                # Determine prediction direction
                price_change_pct = result.get('price_change_pct', 0)
                signal = result.get('signal', 'HOLD')
                
                if signal == 'BUY':
                    prediction = 'UP'
                    up_count += 1
                elif signal == 'SELL':
                    prediction = 'DOWN'
                    down_count += 1
                else:
                    prediction = 'HOLD'
                    hold_count += 1
                
                # Fill in results
                df.at[index, 'Prediction'] = prediction
                df.at[index, 'Confidence'] = result.get('confidence', 'MEDIUM')
                df.at[index, 'Signal'] = signal
                df.at[index, 'Current_Price'] = round(result.get('current_price', 0), 2)
                df.at[index, 'Predicted_Price'] = round(result.get('predicted_price', 0), 2)
                df.at[index, 'Price_Change_Pct'] = round(price_change_pct, 2)
                df.at[index, 'Reason'] = result.get('signal_description', '')
                df.at[index, 'Status'] = 'Success'
                
                # Add to top picks if BUY signal with high confidence
                if signal == 'BUY' and result.get('confidence') == 'HIGH':
                    top_picks.append({
                        'code': code,
                        'name': name,
                        'price_change_pct': round(price_change_pct, 2),
                        'confidence': result.get('confidence', 'MEDIUM')
                    })
                
                successful += 1
                print(f"[INFO] Completed {code}: {prediction} ({price_change_pct:.2f}%)")
            else:
                error_msg = result.get('error', 'Analysis failed') if result else 'Analysis failed'
                df.at[index, 'Status'] = 'Error'
                df.at[index, 'Reason'] = error_msg
                failed += 1
                print(f"[ERROR] Failed {code}: {error_msg}")
                
        except Exception as e:
            df.at[index, 'Status'] = 'Error'
            df.at[index, 'Reason'] = str(e)
            failed += 1
            print(f"[ERROR] Exception processing row {index}: {str(e)}")
    
    # Sort top picks by price change percentage
    top_picks = sorted(top_picks, key=lambda x: x['price_change_pct'], reverse=True)[:10]
    
    # Generate report
    report = {
        "total": total,
        "successful": successful,
        "failed": failed,
        "up": up_count,
        "down": down_count,
        "hold": hold_count,
        "top_picks": top_picks,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return df, report


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Upload Excel file for batch stock analysis
    
    Expects:
        - file: Excel file (.xlsx or .xls)
        - Columns: A=code, B=name
    
    Returns:
        JSON: Processing results with download URL
    """
    lang = get_lang()
    
    print("[INFO] Upload endpoint called")
    
    try:
        # Check if file is present
        if 'file' not in request.files:
            print("[ERROR] No file in request.files")
            return api_response(error="No file provided", status_code=400, lang=lang)
        
        file = request.files['file']
        print(f"[INFO] File received: {file.filename}")
        
        # Check if file was selected
        if file.filename == '':
            print("[ERROR] Empty filename")
            return api_response(error="No file selected", status_code=400, lang=lang)
        
        # Validate file type
        if not allowed_file(file.filename):
            print(f"[ERROR] Invalid file type: {file.filename}")
            return api_response(
                error="Invalid file type. Please upload .xlsx or .xls file",
                status_code=400,
                lang=lang
            )
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        upload_filename = f"{timestamp}_{filename}"
        upload_path = os.path.join(UPLOAD_FOLDER, upload_filename)
        file.save(upload_path)
        print(f"[INFO] File saved: {upload_path}")
        
        # Read Excel file
        try:
            df = pd.read_excel(upload_path)
            print(f"[INFO] Loaded Excel with {len(df)} rows")
        except Exception as e:
            print(f"[ERROR] Failed to read Excel: {str(e)}")
            return api_response(
                error=f"Failed to read Excel file: {str(e)}",
                status_code=400,
                lang=lang
            )
        
        # Validate Excel format
        if df.empty:
            print("[ERROR] Excel file is empty")
            return api_response(error="Excel file is empty", status_code=400, lang=lang)
        
        if len(df.columns) < 2:
            print(f"[ERROR] Excel has only {len(df.columns)} columns")
            return api_response(
                error="Excel must have at least 2 columns (code, name)",
                status_code=400,
                lang=lang
            )
        
        # Check row limit
        if len(df) > 1000:
            print(f"[ERROR] Excel has {len(df)} rows (max 1000)")
            return api_response(
                error="Maximum 1000 rows allowed per upload",
                status_code=400,
                lang=lang
            )
        
        print(f"[INFO] Starting batch processing for {len(df)} stocks")
        
        # Process batch
        processed_df, report = process_stock_batch(df)
        print(f"[INFO] Batch processing complete. Report: {report}")
        
        # Save output Excel
        output_filename = f"analysis_{timestamp}.xlsx"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        try:
            processed_df.to_excel(output_path, index=False, sheet_name='Stock Analysis')
            print(f"[INFO] Output saved: {output_path}")
        except Exception as e:
            print(f"[ERROR] Failed to save output: {str(e)}")
            return api_response(
                error=f"Failed to save output file: {str(e)}",
                status_code=500,
                lang=lang
            )
        
        # Clean up uploaded file
        try:
            os.remove(upload_path)
            print(f"[INFO] Cleaned up upload file: {upload_path}")
        except Exception as e:
            print(f"[WARNING] Failed to clean up upload file: {str(e)}")
        
        response_data = {
            "report": report,
            "download_url": f"/download/{output_filename}",
            "output_file": output_filename
        }
        print(f"[INFO] Returning success response: {response_data}")
        
        return api_response(data=response_data, lang=lang)
    
    except Exception as e:
        print(f"[ERROR] Unexpected error in /api/upload: {str(e)}")
        import traceback
        traceback.print_exc()
        return api_response(error=f"Internal server error: {str(e)}", status_code=500, lang=lang)


@app.route('/download/<filename>')
def download_file(filename):
    """
    Download processed Excel file
    
    Args:
        filename (str): Name of the file to download
    
    Returns:
        File: Excel file as attachment
    """
    try:
        # Validate filename
        if not filename.endswith('.xlsx'):
            return api_response(error="Invalid file type", status_code=400, lang=get_lang())
        
        # Secure the filename
        filename = secure_filename(filename)
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return api_response(error="File not found", status_code=404, lang=get_lang())
        
        print(f"[INFO] Downloading file: {file_path}")
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    except Exception as e:
        print(f"[ERROR] Download failed: {str(e)}")
        return api_response(error=f"Download failed: {str(e)}", status_code=500, lang=get_lang())


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