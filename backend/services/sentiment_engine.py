"""
Sentiment Analysis Engine for analyzing news article sentiment using AI models.
"""

import torch
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import logging
from typing import List, Dict, Any, Optional
import sys
import os

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models import Article, HeadlineSentiment, ContentSentiment, AnalyzedArticle
from config import Config

# Configure logging
logger = logging.getLogger(__name__)


class SentimentEngine:
    """
    AI-powered sentiment analysis engine using VADER and FinBERT models.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the sentiment analysis engine with AI models."""
        self.config = config or Config()
        self.max_text_length = self.config.MAX_TEXT_LENGTH
        
        # Model labels for FinBERT
        self.finbert_labels = ["Negative", "Neutral", "Positive"]
        
        # Initialize models
        self._load_models()
    
    def _load_models(self):
        """Load VADER and FinBERT models with proper error handling."""
        try:
            logger.info("Loading sentiment analysis models...")
            
            # Load VADER sentiment analyzer
            self.vader = SentimentIntensityAnalyzer()
            logger.info("VADER model loaded successfully")
            
            # Load FinBERT model and tokenizer
            model_name = self.config.FINBERT_MODEL
            logger.info(f"Loading FinBERT model: {model_name}")
            
            self.finbert_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.finbert_model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            # Set model to evaluation mode
            self.finbert_model.eval()
            
            # Check for GPU availability and move model if possible
            if torch.cuda.is_available():
                try:
                    self.finbert_model = self.finbert_model.cuda()
                    self.device = 'cuda'
                    logger.info("FinBERT model loaded on GPU")
                except Exception as e:
                    logger.warning(f"Failed to move model to GPU: {e}")
                    self.device = 'cpu'
            else:
                self.device = 'cpu'
                logger.info("FinBERT model loaded on CPU")
            
            logger.info("All sentiment models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading sentiment models: {e}")
            raise RuntimeError(f"Failed to initialize sentiment models: {e}")
    
    def analyze_headline(self, text: str) -> HeadlineSentiment:
        """
        Analyze headline sentiment using VADER for quick processing.
        
        Args:
            text: Headline text to analyze
            
        Returns:
            HeadlineSentiment object with score and label
        """
        try:
            if not text or not text.strip():
                return HeadlineSentiment(score=0.0, label="Neutral")
            
            # Get VADER sentiment scores
            scores = self.vader.polarity_scores(text)
            compound_score = scores['compound']
            
            # Classify sentiment based on compound score
            if compound_score > 0.05:
                label = "Positive"
            elif compound_score < -0.05:
                label = "Negative"
            else:
                label = "Neutral"
            
            return HeadlineSentiment(score=compound_score, label=label)
            
        except Exception as e:
            logger.error(f"Error analyzing headline sentiment: {e}")
            return HeadlineSentiment(score=0.0, label="Neutral")
    
    def analyze_content(self, text: str) -> ContentSentiment:
        """
        Analyze content sentiment using FinBERT for finance-specific analysis.
        
        Args:
            text: Article content to analyze
            
        Returns:
            ContentSentiment object with confidence, label, and probabilities
        """
        try:
            if not text or not text.strip():
                return ContentSentiment(
                    confidence=0.33,
                    label="Neutral",
                    probabilities={"Negative": 0.33, "Neutral": 0.34, "Positive": 0.33}
                )
            
            # Handle text truncation for model input limits
            truncated_text = self._truncate_text(text)
            
            # Tokenize input
            inputs = self.finbert_tokenizer(
                truncated_text,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_text_length,
                padding=True
            )
            
            # Move inputs to the same device as model
            if self.device == 'cuda':
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Get model predictions
            with torch.no_grad():
                outputs = self.finbert_model(**inputs)
            
            # Convert logits to probabilities
            probabilities = torch.softmax(outputs.logits, dim=1).cpu().numpy()[0]
            
            # Get the predicted class and confidence
            predicted_idx = np.argmax(probabilities)
            predicted_label = self.finbert_labels[predicted_idx]
            confidence = float(probabilities[predicted_idx])
            
            # Create probabilities dictionary
            prob_dict = {
                label: float(prob) 
                for label, prob in zip(self.finbert_labels, probabilities)
            }
            
            return ContentSentiment(
                confidence=confidence,
                label=predicted_label,
                probabilities=prob_dict
            )
            
        except Exception as e:
            logger.error(f"Error analyzing content sentiment: {e}")
            # Return neutral sentiment as fallback
            return ContentSentiment(
                confidence=0.33,
                label="Neutral",
                probabilities={"Negative": 0.33, "Neutral": 0.34, "Positive": 0.33}
            )
    
    def _truncate_text(self, text: str) -> str:
        """
        Truncate text appropriately for model input limits without losing essential meaning.
        
        Args:
            text: Text to truncate
            
        Returns:
            Truncated text
        """
        if len(text) <= self.max_text_length:
            return text
        
        # Try to truncate at sentence boundaries
        sentences = text.split('. ')
        truncated = ""
        
        for sentence in sentences:
            if len(truncated + sentence + '. ') <= self.max_text_length:
                truncated += sentence + '. '
            else:
                break
        
        # If no complete sentences fit, truncate at word boundaries
        if not truncated:
            words = text.split()
            truncated = ""
            for word in words:
                if len(truncated + word + ' ') <= self.max_text_length:
                    truncated += word + ' '
                else:
                    break
        
        # Final fallback - character truncation
        if not truncated:
            truncated = text[:self.max_text_length]
        
        return truncated.strip()
    
    def analyze_article(self, article: Article) -> AnalyzedArticle:
        """
        Analyze both headline and content sentiment for a complete article.
        
        Args:
            article: Article object to analyze
            
        Returns:
            AnalyzedArticle with both headline and content sentiment
        """
        try:
            # Analyze headline sentiment
            headline_sentiment = self.analyze_headline(article.title)
            
            # Analyze content sentiment
            content_sentiment = self.analyze_content(article.content)
            
            return AnalyzedArticle(
                article=article,
                headline_sentiment=headline_sentiment,
                content_sentiment=content_sentiment
            )
            
        except Exception as e:
            logger.error(f"Error analyzing article: {e}")
            # Return neutral sentiments as fallback
            return AnalyzedArticle(
                article=article,
                headline_sentiment=HeadlineSentiment(score=0.0, label="Neutral"),
                content_sentiment=ContentSentiment(
                    confidence=0.33,
                    label="Neutral",
                    probabilities={"Negative": 0.33, "Neutral": 0.34, "Positive": 0.33}
                )
            )
    
    def analyze_articles_batch(self, articles: List[Article]) -> List[AnalyzedArticle]:
        """
        Analyze sentiment for a batch of articles.
        
        Args:
            articles: List of articles to analyze
            
        Returns:
            List of analyzed articles
        """
        analyzed_articles = []
        
        for i, article in enumerate(articles):
            try:
                analyzed_article = self.analyze_article(article)
                analyzed_articles.append(analyzed_article)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Analyzed {i + 1}/{len(articles)} articles")
                    
            except Exception as e:
                logger.error(f"Error analyzing article {i}: {e}")
                continue
        
        logger.info(f"Completed analysis of {len(analyzed_articles)}/{len(articles)} articles")
        return analyzed_articles
    
    def calculate_market_signal(self, analyzed_articles: List[AnalyzedArticle]) -> Dict[str, Any]:
        """
        Calculate market signal and statistics from analyzed articles.
        
        Args:
            analyzed_articles: List of analyzed articles
            
        Returns:
            Dictionary with market signal and statistics
        """
        if not analyzed_articles:
            return {
                "market_signal": "NEUTRAL",
                "net_sentiment_score": 0.0,
                "sentiment_distribution": {"Positive": 0, "Negative": 0, "Neutral": 0},
                "confidence_weighted_score": 0.0
            }
        
        # Calculate sentiment distribution
        sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
        weighted_score = 0.0
        total_weight = 0.0
        
        for analyzed_article in analyzed_articles:
            content_sentiment = analyzed_article.content_sentiment
            
            # Count sentiment distribution
            sentiment_counts[content_sentiment.label] += 1
            
            # Calculate weighted score
            confidence = content_sentiment.confidence
            if content_sentiment.label == "Positive":
                direction = 1.0
            elif content_sentiment.label == "Negative":
                direction = -1.0
            else:  # Neutral
                direction = 0.0
            
            weighted_score += direction * confidence
            total_weight += confidence
        
        # Calculate net sentiment score
        net_sentiment_score = weighted_score / total_weight if total_weight > 0 else 0.0
        
        # Determine market signal
        if net_sentiment_score > 0.15:
            market_signal = "BULLISH"
        elif net_sentiment_score < -0.15:
            market_signal = "BEARISH"
        else:
            market_signal = "NEUTRAL"
        
        return {
            "market_signal": market_signal,
            "net_sentiment_score": net_sentiment_score,
            "sentiment_distribution": sentiment_counts,
            "confidence_weighted_score": weighted_score,
            "total_articles": len(analyzed_articles)
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models."""
        return {
            "vader_loaded": hasattr(self, 'vader'),
            "finbert_loaded": hasattr(self, 'finbert_model'),
            "finbert_model": self.config.FINBERT_MODEL,
            "device": self.device,
            "max_text_length": self.max_text_length
        }