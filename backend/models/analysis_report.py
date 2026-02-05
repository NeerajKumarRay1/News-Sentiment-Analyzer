"""
Analysis report model for aggregating sentiment analysis results.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
from .article import AnalyzedArticle


@dataclass
class AnalysisReport:
    """
    Comprehensive analysis report containing aggregated sentiment results.
    """
    timestamp: datetime
    query: str  # The search query that was analyzed
    category: str  # Financial instrument category
    total_articles: int
    sentiment_distribution: Dict[str, int]  # Count of Positive/Negative/Neutral
    net_sentiment_score: float  # Weighted average sentiment (-1 to 1)
    market_signal: str  # "BULLISH", "BEARISH", "NEUTRAL"
    articles: List[AnalyzedArticle]
    processing_time: float  # Time taken for analysis in seconds
    
    def __post_init__(self):
        """Validate and calculate derived fields after initialization."""
        if not self.sentiment_distribution:
            self.sentiment_distribution = self._calculate_sentiment_distribution()
        if self.net_sentiment_score is None:
            self.net_sentiment_score = self._calculate_net_sentiment_score()
        if not self.market_signal:
            self.market_signal = self._determine_market_signal()
    
    def _calculate_sentiment_distribution(self) -> Dict[str, int]:
        """Calculate sentiment distribution from analyzed articles."""
        distribution = {"Positive": 0, "Negative": 0, "Neutral": 0}
        
        for analyzed_article in self.articles:
            sentiment_label = analyzed_article.content_sentiment.label
            if sentiment_label in distribution:
                distribution[sentiment_label] += 1
        
        return distribution
    
    def _calculate_net_sentiment_score(self) -> float:
        """
        Calculate weighted net sentiment score using confidence-weighted scoring.
        Higher confidence predictions have greater influence on the final score.
        """
        if not self.articles:
            return 0.0
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for analyzed_article in self.articles:
            content_sentiment = analyzed_article.content_sentiment
            confidence = content_sentiment.confidence
            
            # Convert sentiment label to numeric value
            if content_sentiment.label == "Positive":
                direction = 1.0
            elif content_sentiment.label == "Negative":
                direction = -1.0
            else:  # Neutral
                direction = 0.0
            
            weighted_score += direction * confidence
            total_weight += confidence
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_market_signal(self) -> str:
        """
        Determine market signal based on net sentiment score.
        Uses thresholds for bullish/bearish/neutral classification.
        """
        if self.net_sentiment_score > 0.15:
            return "BULLISH"
        elif self.net_sentiment_score < -0.15:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def get_sentiment_percentages(self) -> Dict[str, float]:
        """Get sentiment distribution as percentages."""
        if self.total_articles == 0:
            return {"Positive": 0.0, "Negative": 0.0, "Neutral": 0.0}
        
        return {
            sentiment: (count / self.total_articles) * 100
            for sentiment, count in self.sentiment_distribution.items()
        }
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics for the analysis."""
        return {
            "total_articles": self.total_articles,
            "net_sentiment_score": round(self.net_sentiment_score, 4),
            "market_signal": self.market_signal,
            "sentiment_percentages": self.get_sentiment_percentages(),
            "processing_time": round(self.processing_time, 2),
            "analysis_timestamp": self.timestamp.isoformat()
        }
    
    def validate(self) -> bool:
        """Validate analysis report data integrity."""
        # Check basic fields
        if not isinstance(self.total_articles, int) or self.total_articles < 0:
            return False
        if not isinstance(self.net_sentiment_score, (int, float)):
            return False
        if self.net_sentiment_score < -1.0 or self.net_sentiment_score > 1.0:
            return False
        if self.market_signal not in ["BULLISH", "BEARISH", "NEUTRAL"]:
            return False
        if not isinstance(self.processing_time, (int, float)) or self.processing_time < 0:
            return False
        
        # Check sentiment distribution
        expected_sentiments = {"Positive", "Negative", "Neutral"}
        if set(self.sentiment_distribution.keys()) != expected_sentiments:
            return False
        
        # Validate that article count matches
        if len(self.articles) != self.total_articles:
            return False
        
        # Validate all articles
        for article in self.articles:
            if not article.validate():
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "query": self.query,
            "category": self.category,
            "total_articles": self.total_articles,
            "sentiment_distribution": self.sentiment_distribution,
            "net_sentiment_score": self.net_sentiment_score,
            "market_signal": self.market_signal,
            "articles": [article.to_dict() for article in self.articles],
            "processing_time": self.processing_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisReport':
        """Create from dictionary."""
        # Parse timestamp
        timestamp = datetime.fromisoformat(data['timestamp'])
        
        # Parse articles
        articles = [AnalyzedArticle.from_dict(article_data) 
                   for article_data in data['articles']]
        
        return cls(
            timestamp=timestamp,
            query=data['query'],
            category=data['category'],
            total_articles=data['total_articles'],
            sentiment_distribution=data['sentiment_distribution'],
            net_sentiment_score=data['net_sentiment_score'],
            market_signal=data['market_signal'],
            articles=articles,
            processing_time=data['processing_time']
        )
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AnalysisReport':
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def create_from_articles(cls, 
                           query: str,
                           category: str,
                           articles: List[AnalyzedArticle], 
                           processing_time: float) -> 'AnalysisReport':
        """
        Factory method to create an AnalysisReport from a list of analyzed articles.
        Automatically calculates all derived fields.
        """
        return cls(
            timestamp=datetime.utcnow(),
            query=query,
            category=category,
            total_articles=len(articles),
            sentiment_distribution={},  # Will be calculated in __post_init__
            net_sentiment_score=None,   # Will be calculated in __post_init__
            market_signal="",           # Will be calculated in __post_init__
            articles=articles,
            processing_time=processing_time
        )