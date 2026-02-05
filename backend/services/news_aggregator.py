"""
News Aggregator service for fetching and processing news articles.
"""

import feedparser
import requests
import trafilatura
from urllib.parse import quote, urlparse, parse_qs
import time
import concurrent.futures
import logging
from typing import List, Set, Optional, Dict, Any
import sys
import os

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models import Article
from config import Config

# Configure logging
logger = logging.getLogger(__name__)


class NewsAggregator:
    """
    Service for aggregating news articles from RSS feeds with intelligent content extraction.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the news aggregator with configuration."""
        self.config = config or Config()
        self.request_timeout = self.config.REQUEST_TIMEOUT
        self.max_workers = self.config.MAX_WORKERS
        self.articles_per_query = self.config.ARTICLES_PER_QUERY
        self.min_content_length = self.config.MIN_CONTENT_LENGTH
        
        # Set up session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_articles(self, queries: List[str]) -> List[Article]:
        """
        Fetch articles from multiple search queries with concurrent processing.
        Includes deduplication logic to prevent duplicate articles.
        
        Args:
            queries: List of search terms to fetch news for
            
        Returns:
            List of unique Article objects
        """
        logger.info(f"Fetching articles for {len(queries)} queries: {queries}")
        
        unique_links = set()
        raw_entries = []
        
        # 1. Gather all RSS entries first
        for query in queries:
            try:
                rss_url = f"https://news.google.com/rss/search?q={quote(query)}"
                logger.debug(f"Fetching RSS feed: {rss_url}")
                
                feed = feedparser.parse(rss_url)
                
                if feed.bozo:
                    logger.warning(f"RSS feed parsing warning for query '{query}': {feed.bozo_exception}")
                
                for entry in feed.entries[:self.articles_per_query]:
                    if entry.link not in unique_links:
                        unique_links.add(entry.link)
                        raw_entries.append(entry)
                        
            except Exception as e:
                logger.error(f"Error fetching RSS feed for query '{query}': {e}")
                continue
        
        logger.info(f"Found {len(raw_entries)} unique RSS entries")
        
        # 2. Process entries in parallel
        articles = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_entry = {
                executor.submit(self._process_rss_entry, entry): entry 
                for entry in raw_entries
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_entry):
                try:
                    article = future.result()
                    if article:
                        articles.append(article)
                        logger.debug(f"Processed article: {article.title[:50]}...")
                except Exception as e:
                    entry = future_to_entry[future]
                    logger.error(f"Error processing entry '{entry.title}': {e}")
        
        logger.info(f"Successfully processed {len(articles)} articles")
        return articles
    
    def _process_rss_entry(self, entry) -> Optional[Article]:
        """
        Process a single RSS entry into an Article object.
        
        Args:
            entry: RSS feed entry from feedparser
            
        Returns:
            Article object or None if processing failed
        """
        try:
            # 1. Resolve URL
            real_url = self.resolve_google_urls([entry.link])[0]
            
            # 2. Extract content
            content = self.extract_content(real_url)
            
            # Determine source type and fallback if needed
            if content and len(content) >= self.min_content_length:
                source_type = "Full Article"
            else:
                content = entry.title  # Fallback to headline
                source_type = "Headline Only"
            
            # 3. Create Article object
            article = Article(
                title=entry.title,
                url=real_url,
                published=entry.get('published', ''),
                content=content,
                source_type=source_type
            )
            
            # Validate article before returning
            if article.validate():
                return article
            else:
                logger.warning(f"Article validation failed: {entry.title}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing RSS entry: {e}")
            return None
    
    def resolve_google_urls(self, urls: List[str]) -> List[str]:
        """
        Resolve Google News redirect URLs to actual publisher URLs.
        
        Args:
            urls: List of URLs to resolve
            
        Returns:
            List of resolved URLs
        """
        resolved_urls = []
        
        for url in urls:
            try:
                resolved_url = self._resolve_single_url(url)
                resolved_urls.append(resolved_url)
            except Exception as e:
                logger.warning(f"Failed to resolve URL {url}: {e}")
                resolved_urls.append(url)  # Use original URL as fallback
        
        return resolved_urls
    
    def _resolve_single_url(self, url: str) -> str:
        """
        Resolve a single Google News URL to the actual publisher URL.
        
        Args:
            url: URL to resolve
            
        Returns:
            Resolved URL
        """
        try:
            # First try fast text parsing
            parsed = urlparse(url)
            if "news.google.com" in parsed.netloc:
                potential_url = parse_qs(parsed.query).get("url", [None])[0]
                if potential_url:
                    return potential_url
            
            # If text parsing fails, follow the redirect chain
            response = self.session.head(url, allow_redirects=True, timeout=5)
            return response.url
            
        except Exception as e:
            logger.debug(f"URL resolution failed for {url}: {e}")
            return url
    
    def extract_content(self, url: str) -> str:
        """
        Extract article content from webpage using intelligent extraction.
        
        Args:
            url: URL to extract content from
            
        Returns:
            Extracted content text or empty string if extraction failed
        """
        try:
            # Use trafilatura for intelligent content extraction
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                content = trafilatura.extract(downloaded)
                if content:
                    return content.strip()
            
            # Fallback to basic requests + BeautifulSoup if trafilatura fails
            logger.debug(f"Trafilatura failed for {url}, trying fallback method")
            return self._extract_content_fallback(url)
            
        except Exception as e:
            logger.warning(f"Content extraction failed for {url}: {e}")
            return ""
    
    def _extract_content_fallback(self, url: str) -> str:
        """
        Fallback content extraction using requests and BeautifulSoup.
        
        Args:
            url: URL to extract content from
            
        Returns:
            Extracted content or empty string
        """
        try:
            from bs4 import BeautifulSoup
            
            response = self.session.get(url, timeout=self.request_timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text from paragraphs
            paragraphs = soup.find_all("p")
            text = " ".join(p.get_text() for p in paragraphs)
            
            return text.strip()
            
        except Exception as e:
            logger.warning(f"Fallback content extraction failed for {url}: {e}")
            return ""
    
    def deduplicate_articles(self, articles: List[Article]) -> List[Article]:
        """
        Remove duplicate articles based on URL and title similarity.
        
        Args:
            articles: List of articles to deduplicate
            
        Returns:
            List of unique articles
        """
        seen_urls = set()
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            # Check URL uniqueness
            if article.url in seen_urls:
                continue
            
            # Check title similarity (simple approach - exact match)
            title_normalized = article.title.lower().strip()
            if title_normalized in seen_titles:
                continue
            
            # Add to unique set
            seen_urls.add(article.url)
            seen_titles.add(title_normalized)
            unique_articles.append(article)
        
        logger.info(f"Deduplicated {len(articles)} articles to {len(unique_articles)} unique articles")
        return unique_articles
    
    def get_queries_for_category(self, category: str, custom_query: Optional[str] = None) -> List[str]:
        """
        Generate search queries based on financial instrument category.
        
        Args:
            category: Financial instrument category
            custom_query: Optional custom search query
            
        Returns:
            List of search queries
        """
        if custom_query:
            # If custom query provided, create variations
            base_queries = [custom_query]
            
            # Add category-specific modifiers
            if category == 'stock':
                base_queries.extend([f"{custom_query} stock", f"{custom_query} shares"])
            elif category == 'crypto':
                base_queries.extend([f"{custom_query} crypto", f"{custom_query} cryptocurrency"])
            elif category == 'commodity':
                base_queries.extend([f"{custom_query} price", f"{custom_query} market"])
            elif category == 'real_estate':
                base_queries.extend([f"{custom_query} real estate", f"{custom_query} property"])
            elif category == 'exchange':
                base_queries.extend([f"{custom_query} exchange", f"{custom_query} trading"])
            
            return base_queries[:3]  # Limit to 3 queries
        
        # Default queries by category
        category_queries = {
            'stock': ['stock market news', 'equity market', 'stock prices'],
            'crypto': ['cryptocurrency news', 'bitcoin market', 'crypto prices'],
            'commodity': ['commodity prices', 'gold market', 'oil prices'],
            'real_estate': ['real estate market', 'housing market', 'property prices'],
            'exchange': ['stock exchange news', 'trading market', 'financial markets'],
            'all': ['financial news', 'market news', 'economic news']
        }
        
        return category_queries.get(category, category_queries['all'])
    
    def close(self):
        """Close the session and clean up resources."""
        if hasattr(self, 'session'):
            self.session.close()