<div align="center">

# 📊 Universal Market Sentiment Analysis

### AI-Powered Financial News Sentiment Analyzer

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-000000.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

*Analyze market sentiment for any financial instrument using cutting-edge AI models*

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [API](#-api-documentation) • [Contributing](#-contributing)

</div>

---

## 🎯 Overview

Universal Market Sentiment Analysis is a comprehensive web application that leverages artificial intelligence to analyze market sentiment from real-time news articles. Whether you're tracking stocks, cryptocurrencies, commodities, or real estate, this tool provides actionable insights through advanced natural language processing.

### Why This Project?

- **Universal Coverage**: Analyze any financial instrument - from Bitcoin to Gold to Tesla stock
- **AI-Powered**: Combines VADER and FinBERT models for superior accuracy
- **Real-Time**: Fetches and analyzes current news articles on-demand
- **Actionable Insights**: Clear bullish/bearish/neutral signals with confidence scores
- **Modern Stack**: Built with React and Flask for a seamless user experience

---

## ✨ Features

### 🔍 Universal Search
Search and analyze sentiment for any financial instrument:
- **Stocks**: Individual equities, indices (S&P 500, NASDAQ), ETFs
- **Cryptocurrencies**: Bitcoin, Ethereum, altcoins, DeFi tokens
- **Commodities**: Gold, Silver, Oil, Natural Gas, Agricultural products
- **Real Estate**: Housing markets, REITs, property trends
- **Exchanges**: NYSE, NASDAQ, Binance, Coinbase

### 🤖 Advanced AI Analysis
- **Dual-Model Approach**: VADER for headlines + FinBERT for deep content analysis
- **Sentiment Scoring**: Precise sentiment scores from -1.0 (bearish) to +1.0 (bullish)
- **Confidence Metrics**: Know how reliable each prediction is
- **Smart Categorization**: Automatically identifies asset types

### 📈 Comprehensive Results
- **Market Signals**: Clear BULLISH, BEARISH, or NEUTRAL recommendations
- **Sentiment Distribution**: Visual breakdown of positive/negative/neutral articles
- **Article Details**: Individual article analysis with sources and timestamps
- **Processing Metrics**: Transparency with processing time and article counts

### 🎨 Modern Interface
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Real-Time Updates**: Live progress tracking during analysis
- **Intuitive UX**: Clean, professional interface built with Tailwind CSS
- **Quick Access**: Popular searches and category filters

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend                          │
│  (Tailwind CSS, Modern UI Components)                      │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Flask Backend                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ News         │  │ Sentiment    │  │ Financial    │     │
│  │ Aggregator   │─▶│ Engine       │◀─│ Data Service │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                  │                                │
│         ▼                  ▼                                │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │ News APIs    │  │ AI Models    │                       │
│  │ (GNews, etc) │  │ VADER+FinBERT│                       │
│  └──────────────┘  └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- Python 3.8+ with Flask
- VADER Sentiment Analysis
- FinBERT (yiyanghkust/finbert-tone)
- Concurrent processing with ThreadPoolExecutor
- RESTful API design

**Frontend:**
- React 18+
- Tailwind CSS for styling
- Axios for API communication
- Modern ES6+ JavaScript

**AI/ML:**
- NLTK VADER for headline sentiment
- Hugging Face Transformers (FinBERT)
- PyTorch backend
- Smart text preprocessing and tokenization

---

## 🚀 Installation

### Prerequisites

Ensure you have the following installed:
- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Node.js 16+** and npm ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))

### Clone the Repository

```bash
git clone https://github.com/NeerajKumarRay1/News-Sentiment-Analyzer.git
cd News-Sentiment-Analyzer
```

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the Flask server
python app.py
```

The backend will start at `http://localhost:5000`

### Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will start at `http://localhost:3000`

### Quick Start (Alternative)

Use the development runner script to start both services:

```bash
python run_dev.py
```

---

## 💻 Usage

### Basic Workflow

1. **Open the Application**: Navigate to `http://localhost:3000`
2. **Enter a Search Query**: Type any financial instrument (e.g., "Gold", "Bitcoin", "Tesla")
3. **Start Analysis**: Click the "Analyze Sentiment" button
4. **View Results**: See market signals, sentiment scores, and article details

### Example Queries

```
✓ "Gold" - Analyze precious metal sentiment
✓ "Bitcoin" - Cryptocurrency market sentiment
✓ "Apple Stock" - Individual stock analysis
✓ "Housing Market" - Real estate trends
✓ "NASDAQ" - Exchange sentiment
✓ "Crude Oil" - Commodity analysis
```

### Understanding Results

**Market Signal:**
- 🟢 **BULLISH**: Positive sentiment (score > 0.15)
- 🔴 **BEARISH**: Negative sentiment (score < -0.15)
- 🟡 **NEUTRAL**: Mixed or neutral sentiment (-0.15 to 0.15)

**Sentiment Score:**
- Range: -1.0 (extremely bearish) to +1.0 (extremely bullish)
- Calculated as weighted average of all analyzed articles

**Confidence:**
- Shows how certain the AI model is about its prediction
- Higher confidence = more reliable signal

---

## 📁 Project Structure

```
News-Sentiment-Analyzer/
├── backend/
│   ├── app.py                      # Flask application entry point
│   ├── config.py                   # Configuration settings
│   ├── requirements.txt            # Python dependencies
│   ├── models/
│   │   ├── __init__.py
│   │   ├── article.py              # Article data model
│   │   └── analysis_report.py     # Analysis report model
│   ├── services/
│   │   ├── __init__.py
│   │   ├── news_aggregator.py     # News fetching service
│   │   ├── sentiment_engine.py    # AI sentiment analysis
│   │   └── financial_data_service.py
│   └── api/
│       └── __init__.py
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.js       # Main dashboard
│   │   │   ├── SearchBar.js       # Search interface
│   │   │   ├── ResultsDisplay.js  # Results visualization
│   │   │   ├── ArticleList.js     # Article details
│   │   │   └── ControlPanel.js    # Control interface
│   │   ├── App.js                 # Main React component
│   │   ├── App.css                # Styles
│   │   └── index.js               # Entry point
│   ├── package.json               # Node dependencies
│   └── tailwind.config.js         # Tailwind configuration
├── run_dev.py                      # Development runner script
├── test_integration.py             # Integration tests
├── README.md                       # This file
└── .gitignore
```

---

## 🔌 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "models_loaded": true
}
```

#### Start Analysis
```http
POST /api/analysis/start
Content-Type: application/json

{
  "query": "Gold",
  "category": "commodity"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "query": "Gold",
    "category": "commodity",
    "market_signal": "BULLISH",
    "net_sentiment": 0.45,
    "sentiment_distribution": {
      "positive": 8,
      "negative": 2,
      "neutral": 0
    },
    "articles": [...],
    "processing_time": 3.2,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

#### Get Search Suggestions
```http
GET /api/search/suggestions?q=bit
```

**Response:**
```json
{
  "suggestions": ["Bitcoin", "Bitfinex", "BitMEX"]
}
```

---

## 🧪 Testing

### Run Integration Tests

```bash
python test_integration.py
```

### Run Backend Tests

```bash
cd backend
pytest
```

### Run Frontend Tests

```bash
cd frontend
npm test
```

---

## ⚙️ Configuration

### Backend Configuration (`backend/config.py`)

```python
# News aggregation settings
ARTICLES_PER_QUERY = 5
MAX_WORKERS = 5
REQUEST_TIMEOUT = 10

# AI model settings
FINBERT_MODEL = "yiyanghkust/finbert-tone"
MAX_TEXT_LENGTH = 512

# API settings
FLASK_DEBUG = True
PORT = 5000
```

### Environment Variables

Create a `.env` file in the backend directory:

```env
FLASK_DEBUG=True
GNEWS_API_KEY=your_api_key_here
ARTICLES_PER_QUERY=5
MAX_WORKERS=5
```

---

## 🚢 Deployment

### Docker Deployment (Coming Soon)

```bash
docker-compose up -d
```

### Manual Deployment

1. **Backend**: Deploy to Heroku, AWS, or any Python hosting service
2. **Frontend**: Deploy to Vercel, Netlify, or AWS S3 + CloudFront
3. **Environment**: Set production environment variables
4. **CORS**: Configure CORS settings for production domains

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/AmazingFeature`
3. **Commit your changes**: `git commit -m 'Add some AmazingFeature'`
4. **Push to the branch**: `git push origin feature/AmazingFeature`
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Write tests for new features
- Update documentation as needed

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Neeraj Kumar Ray**

- GitHub: [@NeerajKumarRay1](https://github.com/NeerajKumarRay1)
- Project: [News-Sentiment-Analyzer](https://github.com/NeerajKumarRay1/News-Sentiment-Analyzer)

---

## 🙏 Acknowledgments

- **VADER Sentiment**: NLTK's VADER sentiment analysis tool
- **FinBERT**: Financial sentiment analysis model by yiyanghkust
- **Hugging Face**: Transformers library and model hosting
- **GNews API**: News article aggregation
- **React Community**: Amazing frontend framework and ecosystem

---

## 📧 Support

If you have any questions or run into issues, please:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the documentation

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ by Neeraj Kumar Ray

</div>