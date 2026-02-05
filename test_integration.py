#!/usr/bin/env python3
"""
Integration test for the Universal Market Sentiment Analysis system.
"""

import sys
import os
sys.path.append('backend')

from models import Article, HeadlineSentiment, ContentSentiment, AnalyzedArticle, AnalysisReport
from services import NewsAggregator, SentimentEngine
from datetime import datetime

def test_data_models():
    """Test that all data models work correctly."""
    print("Testing data models...")
    
    # Test Article
    article = Article(
        title="Gold prices surge amid market uncertainty",
        url="https://example.com/gold-news",
        published="2024-01-01",
        content="Gold prices have increased significantly due to market volatility...",
        source_type="Full Article"
    )
    assert article.validate(), "Article validation failed"
    
    # Test HeadlineSentiment
    headline_sentiment = HeadlineSentiment(score=0.65, label="Positive")
    assert headline_sentiment.validate(), "HeadlineSentiment validation failed"
    
    # Test ContentSentiment
    content_sentiment = ContentSentiment(
        confidence=0.85,
        label="Positive",
        probabilities={"Positive": 0.85, "Negative": 0.10, "Neutral": 0.05}
    )
    assert content_sentiment.validate(), "ContentSentiment validation failed"
    
    # Test AnalyzedArticle
    analyzed_article = AnalyzedArticle(
        article=article,
        headline_sentiment=headline_sentiment,
        content_sentiment=content_sentiment
    )
    assert analyzed_article.validate(), "AnalyzedArticle validation failed"
    
    # Test AnalysisReport
    report = AnalysisReport.create_from_articles(
        query="Gold",
        category="commodity",
        articles=[analyzed_article],
        processing_time=5.2
    )
    assert report.validate(), "AnalysisReport validation failed"
    
    print("✅ Data models test passed")

def test_services():
    """Test that services work correctly."""
    print("Testing services...")
    
    # Test NewsAggregator
    aggregator = NewsAggregator()
    
    # Test URL resolution
    test_urls = ["https://example.com/test"]
    resolved = aggregator.resolve_google_urls(test_urls)
    assert len(resolved) == 1, "URL resolution failed"
    
    # Test query generation
    queries = aggregator.get_queries_for_category("commodity", "gold")
    assert len(queries) > 0, "Query generation failed"
    assert "gold" in queries[0].lower(), "Generated queries don't contain search term"
    
    # Test SentimentEngine
    engine = SentimentEngine()
    
    # Test headline analysis
    headline_result = engine.analyze_headline("Gold prices surge to new highs")
    assert headline_result.validate(), "Headline sentiment analysis failed"
    
    # Test content analysis
    content_result = engine.analyze_content("Gold market shows strong bullish momentum.")
    assert content_result.validate(), "Content sentiment analysis failed"
    
    print("✅ Services test passed")

def test_end_to_end_pipeline():
    """Test a simplified end-to-end pipeline."""
    print("Testing end-to-end pipeline...")
    
    # Create test article
    test_article = Article(
        title="Gold hits record highs as investors seek safe haven",
        url="https://example.com/gold-record",
        published="2024-01-01T12:00:00Z",
        content="Gold prices reached record levels today as global economic uncertainty drives investors toward safe-haven assets. The precious metal's rally reflects growing concerns about inflation and geopolitical tensions.",
        source_type="Full Article"
    )
    
    # Analyze with sentiment engine
    engine = SentimentEngine()
    analyzed_article = engine.analyze_article(test_article)
    
    assert analyzed_article.validate(), "End-to-end analysis failed"
    
    # Create report
    report = AnalysisReport.create_from_articles(
        query="Gold",
        category="commodity",
        articles=[analyzed_article],
        processing_time=1.0
    )
    
    assert report.validate(), "End-to-end report creation failed"
    assert report.market_signal in ["BULLISH", "BEARISH", "NEUTRAL"], "Invalid market signal"
    
    print("✅ End-to-end pipeline test passed")
    print(f"   Market Signal: {report.market_signal}")
    print(f"   Net Sentiment: {report.net_sentiment_score:.3f}")
    print(f"   Articles: {report.total_articles}")

def main():
    """Run all tests."""
    print("🧪 Running Universal Market Sentiment Analysis Tests")
    print("=" * 60)
    
    try:
        test_data_models()
        test_services()
        test_end_to_end_pipeline()
        
        print("\n" + "=" * 60)
        print("🎉 All tests passed! The system is working correctly.")
        print("✅ Data models: Working")
        print("✅ Services: Working") 
        print("✅ End-to-end pipeline: Working")
        print("\n🚀 Ready to start the application!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("Please check the error and fix any issues.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)