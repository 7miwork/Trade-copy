# Trade Copy – Stock Analytics & Forecasting Platform

A web-based stock market analytics and forecasting platform built with Flask and machine learning.

## Features

- **Stock Analysis**: Analyze stocks and ETFs (AAPL, TSLA, SPY, QQQ, MSFT, GOOGL, AMZN, META)
- **Price Prediction**: Machine learning-based price forecasting using RandomForest
- **Trading Signals**: BUY/SELL/HOLD signals with confidence levels
- **Technical Indicators**: SMA, EMA, RSI, Momentum, MACD, Bollinger Bands
- **AI Analysis**: AI-powered market insights (placeholder for Claude API)
- **Risk Assessment**: Automated risk level evaluation
- **Excel Export**: Export analysis results to Excel
- **Web Dashboard**: Interactive dark-themed dashboard with charts
- **REST API**: Full API for mobile app integration

## Tech Stack

- **Backend**: Python, Flask
- **ML**: scikit-learn (RandomForestRegressor)
- **Data**: pandas, numpy
- **Frontend**: HTML, CSS, Chart.js
- **Export**: openpyxl

## Project Structure

```
Roya Copy/
├── app.py              # Flask application with REST API
├── config.py           # Configuration settings
├── data_loader.py      # Stock data loader with mock data
├── analytics.py        # Technical indicators calculation
├── model.py            # ML models (RandomForest + LSTM placeholder)
├── strategy.py         # Trading signal generation
├── ai_placeholder.py   # Claude API placeholder
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Dashboard template
└── static/
    └── style.css       # Dark theme styles
```

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/7miwork/Trade-copy.git
cd Trade-copy
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Run Instructions

Start the Flask server:
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web Dashboard |
| `/api/analyze?symbol=AAPL` | GET | Analyze single stock |
| `/api/batch?symbols=AAPL,TSLA` | GET | Batch analysis |
| `/api/export` | GET | Export to Excel |
| `/api/symbols` | GET | List supported symbols |
| `/api/history` | GET | Get analysis history |

## Supported Symbols

- AAPL (Apple)
- TSLA (Tesla)
- SPY (S&P 500 ETF)
- QQQ (Nasdaq 100 ETF)
- MSFT (Microsoft)
- GOOGL (Google)
- AMZN (Amazon)
- META (Meta)

## API Placeholders

The system includes placeholders for future API integration:

- **Sinotrade API**: Stock data provider (https://sinotrade.github.io/)
- **Claude API**: AI-powered analysis (Anthropic)

## Mobile Ready

The REST API is designed for future Android and iOS app integration.

## License

MIT