"""
Universal Market Sentiment Analysis Web Application
Flask backend with comprehensive sentiment analysis support
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
import time
from datetime import datetime
from typing import Optional

# Import our services and models
from services import NewsAggregator, SentimentEngine
from models import AnalysisReport
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Enable CORS for frontend communication
CORS(app, origins=["http://localhost:3000"])

# Initialize services
config = Config()
news_aggregator = NewsAggregator(config)
sentiment_engine = SentimentEngine(config)

# Health check endpoint
@app.route('/api/health')
def health_check():
    """System health check endpoint"""
    try:
        model_info = sentiment_engine.get_model_info()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'universal-market-sentiment-api',
            'models': model_info
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500

# Analysis endpoints
@app.route('/api/analysis/start', methods=['POST'])
def start_analysis():
    """Trigger new sentiment analysis for any financial instrument"""
    try:
        data = request.get_json()
        search_query = data.get('query', 'gold') if data else 'gold'
        category = data.get('category', 'commodity') if data else 'commodity'
        
        logger.info(f'Analysis requested for: {search_query} (category: {category})')
        
        # Start timing
        start_time = time.time()
        
        # 1. Generate search queries based on category and user input
        queries = news_aggregator.get_queries_for_category(category, search_query)
        logger.info(f'Generated queries: {queries}')
        
        # 2. Fetch articles
        logger.info('Fetching articles...')
        articles = news_aggregator.fetch_articles(queries)
        
        if not articles:
            return jsonify({
                'error': 'No articles found for the given query',
                'query': search_query,
                'category': category,
                'timestamp': datetime.utcnow().isoformat()
            }), 404
        
        # 3. Deduplicate articles
        unique_articles = news_aggregator.deduplicate_articles(articles)
        logger.info(f'Found {len(unique_articles)} unique articles')
        
        # 4. Analyze sentiment
        logger.info('Analyzing sentiment...')
        analyzed_articles = sentiment_engine.analyze_articles_batch(unique_articles)
        
        # 5. Calculate processing time
        processing_time = time.time() - start_time
        
        # 6. Create analysis report
        report = AnalysisReport.create_from_articles(
            query=search_query,
            category=category,
            articles=analyzed_articles,
            processing_time=processing_time
        )
        
        # 7. Validate report
        if not report.validate():
            logger.error('Generated report failed validation')
            return jsonify({
                'error': 'Analysis report validation failed',
                'timestamp': datetime.utcnow().isoformat()
            }), 500
        
        logger.info(f'Analysis completed in {processing_time:.2f}s - Signal: {report.market_signal}')
        
        # Return the complete analysis report
        return jsonify({
            'status': 'completed',
            'query': search_query,
            'category': category,
            'market_signal': report.market_signal,
            'net_sentiment_score': report.net_sentiment_score,
            'total_articles': report.total_articles,
            'sentiment_distribution': report.sentiment_distribution,
            'processing_time': report.processing_time,
            'articles': [article.to_dict() for article in analyzed_articles],
            'timestamp': report.timestamp.isoformat()
        })
        
    except Exception as e:
        logger.error(f'Analysis error: {e}')
        return jsonify({
            'error': f'Analysis failed: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

def categorize_financial_instrument(query):
    """Categorize the financial instrument based on the search query"""
    query_lower = query.lower()
    
    # Cryptocurrency keywords
    crypto_keywords = ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency', 
                      'dogecoin', 'doge', 'litecoin', 'ltc', 'ripple', 'xrp', 'cardano', 'ada']
    
    # Stock keywords
    stock_keywords = ['stock', 'shares', 'equity', 'aapl', 'apple', 'tesla', 'tsla', 
                     'microsoft', 'msft', 'google', 'googl', 'amazon', 'amzn']
    
    # Commodity keywords
    commodity_keywords = ['gold', 'silver', 'oil', 'crude', 'copper', 'platinum', 
                         'natural gas', 'wheat', 'corn', 'commodity']
    
    # Real estate keywords
    real_estate_keywords = ['real estate', 'property', 'housing', 'reit', 'mortgage', 
                           'residential', 'commercial property']
    
    # Exchange keywords
    exchange_keywords = ['exchange', 'nasdaq', 'nyse', 'binance', 'coinbase', 'forex']
    
    if any(keyword in query_lower for keyword in crypto_keywords):
        return 'crypto'
    elif any(keyword in query_lower for keyword in stock_keywords):
        return 'stock'
    elif any(keyword in query_lower for keyword in commodity_keywords):
        return 'commodity'
    elif any(keyword in query_lower for keyword in real_estate_keywords):
        return 'real_estate'
    elif any(keyword in query_lower for keyword in exchange_keywords):
        return 'exchange'
    else:
        return 'all'

@app.route('/api/analysis/latest')
def get_latest_analysis():
    """Get cached latest analysis results"""
    # TODO: Implement Redis caching for results
    return jsonify({
        'message': 'Latest analysis endpoint - caching to be implemented',
        'timestamp': datetime.utcnow().isoformat()
    })

# Test endpoint for frontend connectivity
@app.route('/api/test')
def test_endpoint():
    """Test endpoint for frontend connectivity"""
    return jsonify({
        'message': 'Backend is running!',
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'success'
    })

# Search suggestions endpoint
@app.route('/api/search/suggestions')
def get_search_suggestions():
    """Get popular search suggestions for different categories"""
    suggestions = {
        'stock': [
            'Apple (AAPL)', 'Tesla (TSLA)', 'Microsoft (MSFT)', 'Amazon (AMZN)',
            'Google (GOOGL)', 'Meta (META)', 'Netflix (NFLX)', 'NVIDIA (NVDA)'
        ],
        'crypto': [
            'Bitcoin (BTC)', 'Ethereum (ETH)', 'Dogecoin (DOGE)', 'Cardano (ADA)',
            'Solana (SOL)', 'Polygon (MATIC)', 'Chainlink (LINK)', 'Litecoin (LTC)'
        ],
        'commodity': [
            'Gold', 'Silver', 'Crude Oil', 'Natural Gas',
            'Copper', 'Platinum', 'Wheat', 'Corn'
        ],
        'real_estate': [
            'Housing Market', 'Real Estate Investment Trusts (REITs)', 
            'Commercial Property', 'Residential Market', 'Mortgage Rates'
        ],
        'exchange': [
            'NASDAQ', 'NYSE', 'Binance', 'Coinbase',
            'CME Group', 'London Stock Exchange', 'Tokyo Stock Exchange'
        ]
    }
    
    return jsonify({
        'suggestions': suggestions,
        'timestamp': datetime.utcnow().isoformat()
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'timestamp': datetime.utcnow().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f'Internal server error: {error}')
    return jsonify({
        'error': 'Internal server error',
        'timestamp': datetime.utcnow().isoformat()
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Universal Market Sentiment Analysis Backend...")
    print("📍 Server running at: http://localhost:5000")
    print("🔗 Health check: http://localhost:5000/api/health")
    print("🤖 AI Models: VADER + FinBERT")
    
    try:
        # Test model loading on startup
        logger.info("Testing model initialization...")
        model_info = sentiment_engine.get_model_info()
        logger.info(f"Models loaded successfully: {model_info}")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"❌ Server startup failed: {e}")
    finally:
        # Clean up resources
        if 'news_aggregator' in globals():
            news_aggregator.close()