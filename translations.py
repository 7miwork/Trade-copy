"""
Internationalization (i18n) translations for Stock Analytics Platform
Supports: English (en) and Chinese Simplified (zh)
"""

TRANSLATIONS = {
    # Header
    "title": {
        "en": "📈 Stock Analytics Platform",
        "zh": "📈 股票分析平台"
    },
    "subtitle": {
        "en": "AI-Powered Stock Market Analysis & Forecasting",
        "zh": "AI驱动的股票市场分析与预测"
    },
    
    # Stock Selector
    "select_stock": {
        "en": "Select Stock:",
        "zh": "选择股票:"
    },
    "analyze": {
        "en": "Analyze",
        "zh": "分析"
    },
    "analyzing": {
        "en": "Analyzing...",
        "zh": "分析中..."
    },
    
    # Main Stats
    "current_price": {
        "en": "Current Price",
        "zh": "当前价格"
    },
    "predicted_price": {
        "en": "Predicted Price",
        "zh": "预测价格"
    },
    "price_change": {
        "en": "Price Change",
        "zh": "价格变化"
    },
    "confidence": {
        "en": "Confidence",
        "zh": "置信度"
    },
    
    # Signals
    "buy": {
        "en": "BUY",
        "zh": "买入"
    },
    "sell": {
        "en": "SELL",
        "zh": "卖出"
    },
    "hold": {
        "en": "HOLD",
        "zh": "持有"
    },
    
    # Confidence Levels
    "high": {
        "en": "HIGH",
        "zh": "高"
    },
    "medium": {
        "en": "MEDIUM",
        "zh": "中"
    },
    "low": {
        "en": "LOW",
        "zh": "低"
    },
    
    # Technical Indicators
    "technical_indicators": {
        "en": "Technical Indicators",
        "zh": "技术指标"
    },
    "rsi": {
        "en": "RSI",
        "zh": "RSI"
    },
    "sma": {
        "en": "SMA (20)",
        "zh": "SMA (20)"
    },
    "ema": {
        "en": "EMA (20)",
        "zh": "EMA (20)"
    },
    "macd": {
        "en": "MACD",
        "zh": "MACD"
    },
    "momentum": {
        "en": "Momentum",
        "zh": "动量"
    },
    "bollinger": {
        "en": "Bollinger Bands",
        "zh": "布林带"
    },
    
    # Indicator Signals
    "oversold": {
        "en": "OVERSOLD",
        "zh": "超卖"
    },
    "overbought": {
        "en": "OVERBOUGHT",
        "zh": "超买"
    },
    "neutral": {
        "en": "NEUTRAL",
        "zh": "中性"
    },
    "bullish": {
        "en": "BULLISH",
        "zh": "看涨"
    },
    "bearish": {
        "en": "BEARISH",
        "zh": "看跌"
    },
    
    # AI Analysis
    "ai_analysis": {
        "en": "🤖 AI Analysis",
        "zh": "🤖 AI分析"
    },
    "model": {
        "en": "Model:",
        "zh": "模型:"
    },
    
    # Risk Assessment
    "risk_assessment": {
        "en": "⚠️ Risk Assessment",
        "zh": "⚠️ 风险评估"
    },
    "risk_level": {
        "en": "Risk Level:",
        "zh": "风险等级:"
    },
    "risk_recommendation": {
        "en": "Standard position sizing with stop-loss",
        "zh": "标准仓位管理，设置止损"
    },
    
    # Chart
    "price_history": {
        "en": "Price History (Last 30 Days)",
        "zh": "价格历史 (最近30天)"
    },
    "predicted": {
        "en": "Predicted",
        "zh": "预测"
    },
    "price_label": {
        "en": "Price",
        "zh": "价格"
    },
    
    # History Table
    "analysis_history": {
        "en": "Analysis History",
        "zh": "分析历史"
    },
    "time": {
        "en": "Time",
        "zh": "时间"
    },
    "symbol": {
        "en": "Symbol",
        "zh": "股票"
    },
    "current": {
        "en": "Current",
        "zh": "当前"
    },
    "signal": {
        "en": "Signal",
        "zh": "信号"
    },
    "no_history": {
        "en": "No analysis history yet. Select a stock to begin.",
        "zh": "暂无分析历史。选择股票开始分析。"
    },
    
    # Errors
    "error": {
        "en": "⚠️ Error",
        "zh": "⚠️ 错误"
    },
    "loading": {
        "en": "Loading analysis...",
        "zh": "加载分析中..."
    },
    "analysis_complete": {
        "en": "Analysis complete",
        "zh": "分析完成"
    },
    "analysis_timeout": {
        "en": "Analysis timeout",
        "zh": "分析超时"
    },
    "analysis_failed": {
        "en": "Analysis failed",
        "zh": "分析失败"
    },
    "symbol_required": {
        "en": "Symbol parameter is required",
        "zh": "需要股票代码参数"
    },
    "symbol_not_supported": {
        "en": "Symbol not supported",
        "zh": "不支持的股票代码"
    },
    "supported_symbols": {
        "en": "Supported symbols",
        "zh": "支持的股票代码"
    },
    "internal_error": {
        "en": "Internal server error",
        "zh": "服务器内部错误"
    },
    "endpoint_not_found": {
        "en": "Endpoint not found",
        "zh": "未找到端点"
    },
    "data_loading_failed": {
        "en": "Data loading failed",
        "zh": "数据加载失败"
    },
    "indicator_calculation_failed": {
        "en": "Indicator calculation failed",
        "zh": "指标计算失败"
    },
    "model_training_failed": {
        "en": "Model training failed",
        "zh": "模型训练失败"
    },
    "price_prediction_failed": {
        "en": "Price prediction failed",
        "zh": "价格预测失败"
    },
    "signal_generation_failed": {
        "en": "Signal generation failed",
        "zh": "信号生成失败"
    },
    "pipeline_failed": {
        "en": "Pipeline failed",
        "zh": "流水线失败"
    },
    "no_data_returned": {
        "en": "No data returned",
        "zh": "未返回数据"
    },
    "indicator_empty_data": {
        "en": "Indicator calculation returned empty data",
        "zh": "指标计算返回空数据"
    },
    "model_none": {
        "en": "Model training returned None",
        "zh": "模型训练返回空值"
    },
    "prediction_invalid": {
        "en": "Prediction returned invalid value",
        "zh": "预测返回无效值"
    },
    
    # Export
    "no_symbols_provided": {
        "en": "No symbols provided",
        "zh": "未提供股票代码"
    },
    "no_data_to_export": {
        "en": "No data to export",
        "zh": "没有数据可导出"
    },
    "export_directory_failed": {
        "en": "Failed to create export directory",
        "zh": "创建导出目录失败"
    },
    "export_failed": {
        "en": "Failed to export data",
        "zh": "导出数据失败"
    },
    "export_success": {
        "en": "Export successful",
        "zh": "导出成功"
    },
    "records": {
        "en": "records",
        "zh": "条记录"
    },
    
    # Footer
    "footer": {
        "en": "Stock Analytics Platform | REST API available for mobile integration",
        "zh": "股票分析平台 | REST API可用于移动应用集成"
    },
    "api_endpoints": {
        "en": "API: /api/analyze | /api/batch | /api/export",
        "zh": "API: /api/analyze | /api/batch | /api/export"
    },
    
    # Language Switch
    "lang_en": {
        "en": "🇬🇧 English",
        "zh": "🇬🇧 English"
    },
    "lang_zh": {
        "en": "🇨🇳 中文",
        "zh": "🇨🇳 中文"
    }
}


def t(key, lang="en"):
    """
    Translate a key to the specified language
    
    Args:
        key (str): Translation key
        lang (str): Language code (en/zh)
    
    Returns:
        str: Translated text or key if not found
    """
    if lang not in ["en", "zh"]:
        lang = "en"
    
    translation = TRANSLATIONS.get(key, {}).get(lang)
    if translation:
        return translation
    
    # Fallback to English
    fallback = TRANSLATIONS.get(key, {}).get("en")
    if fallback:
        return fallback
    
    # Return key if no translation found
    return key


def get_all_translations(lang="en"):
    """
    Get all translations for a specific language
    
    Args:
        lang (str): Language code (en/zh)
    
    Returns:
        dict: Dictionary of all translations for the language
    """
    if lang not in ["en", "zh"]:
        lang = "en"
    
    return {key: translations.get(lang, translations.get("en", key)) 
            for key, translations in TRANSLATIONS.items()}