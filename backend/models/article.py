"""
Article and sentiment analysis data models for the Gold Sentiment System.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Optional, Any
import json


@dataclass
class Article:
    """Represents a news article with metadata."""
    title: str
    url: str
    published: str
    content: str
    source_type: str  # "Full Article" or "Headline Only"
    
    def validate(self) -> bool:
        """Validate article data integrity."""
        if not self.title or not self.title.strip():
            return False
        if not self.url or not self.url.startswith(('http://', 'https://')):
            return False
        if not self.content or not self.content.strip():
            return False
        if self.source_type not in ["Full Article", "Headline Only"]:
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert article to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Article':
        """Create article from dictionary."""
        return cls(**data)


@dataclass
class HeadlineSentiment:
    """Represents sentiment analysis results for article headlines using VADER."""
    score: float  # VADER compound score (-1 to 1)
    label: str   # "Positive", "Negative", "Neutral"
    
    def validate(self) -> bool:
        """Validate headline sentiment data."""
        if not isinstance(self.score, (int, float)):
            return False
        if self.score < -1.0 or self.score > 1.0:
            return False
        if self.label not in ["Positive", "Negative", "Neutral"]:
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HeadlineSentiment':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ContentSentiment:
    """Represents sentiment analysis results for article content using FinBERT."""
    confidence: float  # Model confidence (0 to 1)
    label: str        # "Positive", "Negative", "Neutral"
    probabilities: Dict[str, float]  # Raw probabilities for each class
    
    def validate(self) -> bool:
        """Validate content sentiment data."""
        if not isinstance(self.confidence, (int, float)):
            return False
        if self.confidence < 0.0 or self.confidence > 1.0:
            return False
        if self.label not in ["Positive", "Negative", "Neutral"]:
            return False
        if not isinstance(self.probabilities, dict):
            return False
        # Check that probabilities sum to approximately 1.0
        prob_sum = sum(self.probabilities.values())
        if abs(prob_sum - 1.0) > 0.01:  # Allow small floating point errors
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentSentiment':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class AnalyzedArticle:
    """Represents a complete analyzed article with both headline and content sentiment."""
    article: Article
    headline_sentiment: HeadlineSentiment
    content_sentiment: ContentSentiment
    
    def validate(self) -> bool:
        """Validate the complete analyzed article."""
        return (self.article.validate() and 
                self.headline_sentiment.validate() and 
                self.content_sentiment.validate())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'article': self.article.to_dict(),
            'headline_sentiment': self.headline_sentiment.to_dict(),
            'content_sentiment': self.content_sentiment.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalyzedArticle':
        """Create from dictionary."""
        return cls(
            article=Article.from_dict(data['article']),
            headline_sentiment=HeadlineSentiment.from_dict(data['headline_sentiment']),
            content_sentiment=ContentSentiment.from_dict(data['content_sentiment'])
        )
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AnalyzedArticle':
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)