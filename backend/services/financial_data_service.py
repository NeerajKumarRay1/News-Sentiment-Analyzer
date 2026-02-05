    cd"""
Financial data service for retrieving stock market data using yfinance.
"""
import asyncio
import logging
import yfinance as yf
import redis
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import time

from ..models.financial_data import (
    TickerInfo, PriceHistory, PricePoint, FundamentalMetrics, 
    DerivedMetrics, DetailedAnalysisReport
)
from ..utils.error_handling import (
    with_retry, with_circuit_breaker, with_timeout, RetryConfig, 
    CircuitBreakerConfig, log_error_with_context, GracefulDegradation
)

logger = logging.getLogger(__name__)


class FinancialDataService:
    """Service for retrieving and processing financial data."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """Initialize the financial data service."""
        self.redis_client = redis_client
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.cache_ttl = 300  # 5 minutes cache TTL
        
    def _get_cache_key(self, ticker: str, data_type: str) -> str:
        """Generate cache key for ticker data."""
        return f"financial:{ticker}:{data_type}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from Redis cache."""
        if not self.redis_client:
            return None
            
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
        return None
    
    def _set_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Store data in Redis cache."""
        if not self.redis_client:
            return
            
        try:
            self.redis_client.setex(
                cache_key, 
                self.cache_ttl, 
                json.dumps(data, default=str)
            )
        except Exception as e:
            logger.warning(f"Cache storage error: {e}")
    
    @with_timeout(30.0)  # 30 second timeout
    @with_circuit_breaker(CircuitBreakerConfig(failure_threshold=3, recovery_timeout=300))
    @with_retry(RetryConfig(max_retries=2, base_delay=1.0, max_delay=10.0))
    def _fetch_ticker_data(self, ticker: str) -> Optional[yf.Ticker]:
        """Fetch ticker data from yfinance (synchronous) with error handling."""
        try:
            logger.info(f"Fetching data for ticker: {ticker}")
            ticker_obj = yf.Ticker(ticker)
            
            # Test if ticker is valid by trying to get info with timeout
            info = ticker_obj.info
            if not info or 'symbol' not in info:
                logger.warning(f"No data found for ticker: {ticker}")
                return None
                
            logger.info(f"Successfully fetched data for ticker: {ticker}")
            return ticker_obj
            
        except Exception as e:
            log_error_with_context(e, {
                'ticker': ticker,
                'operation': 'fetch_ticker_data'
            })
            return None
    
    async def get_ticker_info(self, ticker: str) -> Optional[TickerInfo]:
        """Get basic ticker information with comprehensive error handling."""
        if not self.validate_ticker(ticker):
            logger.warning(f"Invalid ticker format: {ticker}")
            return None
            
        cache_key = self._get_cache_key(ticker, "info")
        cached_data = self._get_from_cache(cache_key)
        
        if cached_data:
            logger.info(f"Using cached data for ticker: {ticker}")
            return TickerInfo(**cached_data)
        
        try:
            # Fetch from yfinance in thread pool with timeout
            loop = asyncio.get_event_loop()
            ticker_obj = await asyncio.wait_for(
                loop.run_in_executor(self.executor, self._fetch_ticker_data, ticker),
                timeout=30.0
            )
            
            if not ticker_obj:
                logger.warning(f"No ticker data available for: {ticker}")
                return None
            
            info = ticker_obj.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0.0)
            
            if current_price == 0.0:
                logger.warning(f"No current price available for ticker: {ticker}")
                # Try alternative price fields
                current_price = (info.get('previousClose') or 
                               info.get('open') or 
                               info.get('dayHigh') or 0.0)
            
            ticker_info = TickerInfo(
                symbol=ticker.upper(),
                current_price=float(current_price),
                market_cap=info.get('marketCap'),
                pe_ratio=info.get('trailingPE'),
                fifty_two_week_high=info.get('fiftyTwoWeekHigh'),
                fifty_two_week_low=info.get('fiftyTwoWeekLow'),
                sector=info.get('sector'),
                industry=info.get('industry'),
                volume=info.get('volume')
            )
            
            # Cache the result
            self._set_cache(cache_key, ticker_info.to_dict())
            logger.info(f"Successfully processed ticker info for: {ticker}")
            return ticker_info
            
        except asyncio.TimeoutError:
            log_error_with_context(
                Exception("Timeout fetching ticker info"), 
                {'ticker': ticker, 'operation': 'get_ticker_info'}
            )
            return None
        except Exception as e:
            log_error_with_context(e, {
                'ticker': ticker,
                'operation': 'get_ticker_info'
            })
            return None
    
    async def get_price_history(self, ticker: str, period: str = "1mo") -> Optional[PriceHistory]:
        """Get price history for a ticker."""
        cache_key = self._get_cache_key(ticker, f"history_{period}")
        cached_data = self._get_from_cache(cache_key)
        
        if cached_data:
            # Reconstruct PriceHistory from cached data
            prices = [
                PricePoint(
                    date=datetime.fromisoformat(p['date']),
                    open=p['open'],
                    high=p['high'],
                    low=p['low'],
                    close=p['close'],
                    volume=p['volume']
                ) for p in cached_data['prices']
            ]
            return PriceHistory(
                ticker=cached_data['ticker'],
                period=cached_data['period'],
                prices=prices
            )
        
        # Fetch from yfinance
        loop = asyncio.get_event_loop()
        ticker_obj = await loop.run_in_executor(
            self.executor, self._fetch_ticker_data, ticker
        )
        
        if not ticker_obj:
            return None
        
        try:
            hist = ticker_obj.history(period=period)
            if hist.empty:
                return None
            
            prices = []
            for date, row in hist.iterrows():
                prices.append(PricePoint(
                    date=date.to_pydatetime(),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=int(row['Volume'])
                ))
            
            price_history = PriceHistory(
                ticker=ticker.upper(),
                period=period,
                prices=prices
            )
            
            # Cache the result
            self._set_cache(cache_key, price_history.to_dict())
            return price_history
            
        except Exception as e:
            logger.error(f"Error fetching price history for {ticker}: {e}")
            return None
    
    async def get_fundamental_metrics(self, ticker: str) -> Optional[FundamentalMetrics]:
        """Get fundamental metrics for a ticker."""
        cache_key = self._get_cache_key(ticker, "fundamentals")
        cached_data = self._get_from_cache(cache_key)
        
        if cached_data:
            return FundamentalMetrics(**cached_data)
        
        # Fetch from yfinance
        loop = asyncio.get_event_loop()
        ticker_obj = await loop.run_in_executor(
            self.executor, self._fetch_ticker_data, ticker
        )
        
        if not ticker_obj:
            return None
        
        try:
            info = ticker_obj.info
            
            fundamentals = FundamentalMetrics(
                pe_ratio=info.get('trailingPE'),
                market_cap=info.get('marketCap'),
                revenue_growth=info.get('revenueGrowth'),
                profit_margin=info.get('profitMargins'),
                debt_to_equity=info.get('debtToEquity'),
                return_on_equity=info.get('returnOnEquity'),
                fifty_two_week_high=info.get('fiftyTwoWeekHigh'),
                fifty_two_week_low=info.get('fiftyTwoWeekLow')
            )
            
            # Cache the result
            self._set_cache(cache_key, fundamentals.to_dict())
            return fundamentals
            
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {ticker}: {e}")
            return None
    
    async def get_multi_ticker_data(self, tickers: List[str]) -> Dict[str, Optional[TickerInfo]]:
        """Get ticker info for multiple tickers concurrently with partial success handling."""
        if not tickers:
            return {}
        
        # Validate all tickers first
        valid_tickers = [t for t in tickers if self.validate_ticker(t)]
        if not valid_tickers:
            logger.warning("No valid tickers provided for multi-ticker request")
            return {ticker: None for ticker in tickers}
        
        logger.info(f"Processing multi-ticker request for {len(valid_tickers)} tickers")
        
        # Create tasks with individual error handling
        tasks = []
        for ticker in valid_tickers:
            task = asyncio.create_task(
                self._get_ticker_with_fallback(ticker),
                name=f"ticker_{ticker}"
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results with partial success handling
        ticker_data = {}
        successful_count = 0
        
        for ticker, result in zip(valid_tickers, results):
            if isinstance(result, Exception):
                log_error_with_context(result, {
                    'ticker': ticker,
                    'operation': 'multi_ticker_data'
                })
                ticker_data[ticker] = None
            else:
                ticker_data[ticker] = result
                if result is not None:
                    successful_count += 1
        
        # Add any invalid tickers as None
        for ticker in tickers:
            if ticker not in ticker_data:
                ticker_data[ticker] = None
        
        logger.info(f"Multi-ticker request completed: {successful_count}/{len(tickers)} successful")
        return ticker_data
    
    async def _get_ticker_with_fallback(self, ticker: str) -> Optional[TickerInfo]:
        """Get ticker info with graceful fallback for individual ticker failures."""
        try:
            return await self.get_ticker_info(ticker)
        except Exception as e:
            logger.warning(f"Failed to get data for {ticker}, attempting fallback: {e}")
            # Fallback: return minimal ticker info if possible
            try:
                return TickerInfo(
                    symbol=ticker.upper(),
                    current_price=0.0,  # Will be marked as unavailable
                    market_cap=None,
                    pe_ratio=None,
                    fifty_two_week_high=None,
                    fifty_two_week_low=None,
                    sector=None,
                    industry=None,
                    volume=None
                )
            except Exception:
                return None
    
    def calculate_derived_metrics(self, ticker_info: TickerInfo, 
                                news_count: int = 0) -> DerivedMetrics:
        """Calculate derived metrics for radar chart display with improved normalization."""
        
        # Growth score from P/E ratio (lower P/E = higher growth potential)
        # Scale: 0.0 (poor) to 1.0 (excellent)
        growth_score = 0.5  # Default neutral
        if ticker_info.pe_ratio and ticker_info.pe_ratio > 0:
            # Inverse relationship: lower P/E = higher growth score
            if ticker_info.pe_ratio < 10:
                growth_score = 0.95  # Excellent value
            elif ticker_info.pe_ratio < 15:
                growth_score = 0.8   # Very good value
            elif ticker_info.pe_ratio < 20:
                growth_score = 0.65  # Good value
            elif ticker_info.pe_ratio < 25:
                growth_score = 0.5   # Fair value
            elif ticker_info.pe_ratio < 35:
                growth_score = 0.35  # Expensive
            else:
                growth_score = 0.2   # Very expensive
        
        # Safety score from market cap (larger = safer)
        # Scale: 0.0 (very risky) to 1.0 (very safe)
        safety_score = 0.5  # Default neutral
        if ticker_info.market_cap and ticker_info.market_cap > 0:
            market_cap_billions = ticker_info.market_cap / 1_000_000_000
            
            if market_cap_billions > 500:      # Mega cap (>500B)
                safety_score = 1.0
            elif market_cap_billions > 200:    # Large cap (200-500B)
                safety_score = 0.9
            elif market_cap_billions > 50:     # Large cap (50-200B)
                safety_score = 0.75
            elif market_cap_billions > 10:     # Mid cap (10-50B)
                safety_score = 0.6
            elif market_cap_billions > 2:      # Small cap (2-10B)
                safety_score = 0.4
            elif market_cap_billions > 0.3:    # Micro cap (300M-2B)
                safety_score = 0.25
            else:                              # Nano cap (<300M)
                safety_score = 0.1
        
        # Hype score from volume and news count
        # Scale: 0.0 (no hype) to 1.0 (maximum hype)
        hype_score = 0.5  # Default neutral
        
        # Volume component (0-0.7 weight)
        volume_factor = 0.3  # Default low volume
        if ticker_info.volume and ticker_info.volume > 0:
            # Logarithmic scaling for volume
            if ticker_info.volume > 100_000_000:    # Very high volume
                volume_factor = 0.7
            elif ticker_info.volume > 50_000_000:   # High volume
                volume_factor = 0.6
            elif ticker_info.volume > 10_000_000:   # Above average volume
                volume_factor = 0.5
            elif ticker_info.volume > 1_000_000:    # Average volume
                volume_factor = 0.4
            elif ticker_info.volume > 100_000:      # Low volume
                volume_factor = 0.3
            else:                                   # Very low volume
                volume_factor = 0.2
        
        # News component (0-0.3 weight)
        news_factor = min(news_count / 20.0, 0.3)  # Cap at 0.3, normalize by 20 articles
        
        hype_score = min(volume_factor + news_factor, 1.0)
        
        # Sentiment score will be filled in by sentiment analysis
        # Default to neutral (0.5) - will be updated by enhanced analysis engine
        sentiment_score = 0.5
        
        return DerivedMetrics(
            growth_score=round(growth_score, 3),
            safety_score=round(safety_score, 3),
            hype_score=round(hype_score, 3),
            sentiment_score=round(sentiment_score, 3)
        )
    
    def validate_ticker(self, ticker: str) -> bool:
        """Validate if a ticker symbol is properly formatted."""
        if not ticker or not isinstance(ticker, str):
            return False
        
        ticker = ticker.strip().upper()
        
        # Basic validation - alphanumeric, 1-5 characters
        if not ticker.isalnum() or len(ticker) < 1 or len(ticker) > 5:
            return False
        
        return True
    
    def suggest_tickers(self, invalid_ticker: str) -> List[str]:
        """Suggest alternative ticker symbols for invalid input with enhanced suggestions."""
        if not invalid_ticker:
            return []
        
        # Enhanced common tickers database
        common_tickers = {
            # Tech giants
            'A': ['AAPL', 'AMZN', 'AMD', 'ADBE'],
            'B': ['BABA', 'BIDU', 'BA'],
            'C': ['CRM', 'CSCO', 'COP'],
            'D': ['DIS', 'DOCU'],
            'E': ['EBAY'],
            'F': ['FB', 'F'],  # FB is now META but people still search for it
            'G': ['GOOGL', 'GOOG', 'GM', 'GE'],
            'H': ['HD', 'HPQ'],
            'I': ['INTC', 'IBM', 'INTU'],
            'J': ['JNJ', 'JPM'],
            'K': ['KO'],
            'L': ['LMT'],
            'M': ['MSFT', 'META', 'MCD', 'MA'],
            'N': ['NVDA', 'NFLX', 'NKE', 'NOW'],
            'O': ['ORCL', 'OKTA'],
            'P': ['PYPL', 'PFE', 'PG'],
            'Q': ['QCOM'],
            'R': ['ROKU'],
            'S': ['SNOW', 'SHOP', 'SQ', 'SNAP'],
            'T': ['TSLA', 'TWTR', 'TMO', 'TXN'],
            'U': ['UBER', 'UNH'],
            'V': ['V', 'VZ', 'VMW'],
            'W': ['WMT', 'WFC'],
            'X': ['XOM'],
            'Y': ['YELP'],
            'Z': ['ZM', 'ZNGA']
        }
        
        suggestions = []
        invalid_upper = invalid_ticker.upper().strip()
        
        # Exact match check (in case it's actually valid)
        if len(invalid_upper) >= 1 and len(invalid_upper) <= 5:
            suggestions.append(invalid_upper)
        
        # Find tickers that start with the same letter(s)
        if invalid_upper and invalid_upper[0] in common_tickers:
            for ticker in common_tickers[invalid_upper[0]]:
                if ticker.startswith(invalid_upper[:min(2, len(invalid_upper))]):
                    suggestions.append(ticker)
        
        # If no good matches, provide popular suggestions
        if len(suggestions) <= 1:
            popular_suggestions = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META']
            suggestions.extend(popular_suggestions)
        
        # Remove duplicates and limit to 5 suggestions
        unique_suggestions = list(dict.fromkeys(suggestions))
        return unique_suggestions[:5]