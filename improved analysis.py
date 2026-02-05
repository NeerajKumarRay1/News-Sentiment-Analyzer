import feedparser
import requests
import trafilatura
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from urllib.parse import quote, urlparse, parse_qs
import time
import concurrent.futures
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import logging

# =========================
# CONFIGURATION
# =========================
QUERIES = [
    "gold market",
    "gold price",
    "gold news",
    "gold trends",
    "gold forecast",
    "gold investment"
]

ARTICLES_PER_QUERY = 5     # Reduced slightly since we are deeper scraping
MAX_WORKERS = 5            # Number of parallel downloads
REQUEST_TIMEOUT = 10

# Configure logging to keep console clean
logging.getLogger("trafilatura").setLevel(logging.WARNING)

# =========================
# LOAD MODELS
# =========================
print("⏳ Loading AI models (FinBERT & VADER)...")

vader = SentimentIntensityAnalyzer()

# specific finance-trained BERT model
finbert_tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
finbert_model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
finbert_model.eval()

FINBERT_LABELS = ["Negative", "Neutral", "Positive"]

# =========================
# HELPER FUNCTIONS
# =========================

def get_real_url(google_url):
    """
    Follows the Google News redirect to find the actual publisher URL.
    Uses a HEAD request to be fast.
    """
    try:
        # First try fast text parsing
        parsed = urlparse(google_url)
        if "news.google.com" in parsed.netloc:
            potential_url = parse_qs(parsed.query).get("url", [None])[0]
            if potential_url:
                return potential_url
        
        # If text parsing fails, follow the redirect network chain
        response = requests.head(google_url, allow_redirects=True, timeout=5)
        return response.url
    except:
        return google_url

def fetch_and_process_article(entry):
    """
    Worker function to process a single RSS entry.
    Returns a dict with sentiment data or None if failed.
    """
    try:
        # 1. Resolve URL
        real_url = get_real_url(entry.link)
        
        # 2. Smart Extraction (Trafilatura)
        # This downloads and extracts ONLY the main body text
        downloaded = trafilatura.fetch_url(real_url)
        content = trafilatura.extract(downloaded)

        # Fallback to title if content extraction fails or is too short
        if content is None or len(content) < 100:
            content = entry.title
            source_type = "Headline Only"
        else:
            source_type = "Full Article"

        # 3. Analyze Sentiment
        # VADER (Headline)
        h_score = vader.polarity_scores(entry.title)["compound"]
        if h_score > 0.05: h_sent = "Positive"
        elif h_score < -0.05: h_sent = "Negative"
        else: h_sent = "Neutral"

        # FinBERT (Content)
        # We truncate to 512 tokens for BERT
        inputs = finbert_tokenizer(content, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = finbert_model(**inputs)
        
        probs = torch.softmax(outputs.logits, dim=1).numpy()[0]
        idx = np.argmax(probs)
        c_sent = FINBERT_LABELS[idx]
        c_conf = probs[idx]

        return {
            "title": entry.title,
            "url": real_url,
            "source_type": source_type,
            "h_sent": h_sent,
            "h_score": h_score,
            "c_sent": c_sent,
            "c_conf": c_conf
        }

    except Exception as e:
        # Silently fail on bad links to keep the loop moving
        return None

# =========================
# MAIN DATA PIPELINE
# =========================
def fetch_news_parallel():
    unique_links = set()
    raw_entries = []

    # 1. Gather all RSS entries first
    print(f"📡 Scanning RSS Feeds for: {', '.join(QUERIES)}...")
    for query in QUERIES:
        rss_url = f"https://news.google.com/rss/search?q={quote(query)}"
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:ARTICLES_PER_QUERY]:
            if entry.link not in unique_links:
                unique_links.add(entry.link)
                raw_entries.append(entry)

    print(f"✅ Found {len(raw_entries)} unique articles. Starting parallel analysis...")

    # 2. Process in parallel
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        future_to_entry = {executor.submit(fetch_and_process_article, entry): entry for entry in raw_entries}
        
        # Collect results as they finish
        for i, future in enumerate(concurrent.futures.as_completed(future_to_entry)):
            data = future.result()
            if data:
                results.append(data)
                # Simple progress indicator
                print(f"   Processed {len(results)}/{len(raw_entries)}: {data['title'][:40]}...")

    return results

# =========================
# ANALYTICS & REPORTING
# =========================
def main():
    articles = fetch_news_parallel()

    if not articles:
        print("❌ No valid articles found.")
        return

    summary = {"Positive": 0, "Negative": 0, "Neutral": 0}
    weighted_score = 0.0
    total_weight = 0.0

    print("\n" + "="*60)
    print(f"Detailed Analysis Report ({len(articles)} articles)")
    print("="*60)

    for idx, art in enumerate(articles, 1):
        # Update Stats
        summary[art['c_sent']] += 1
        
        # Weight Calculation: 
        # Positive = +1, Negative = -1, Neutral = 0
        # Multiplied by confidence of the model
        direction = 1 if art['c_sent'] == "Positive" else -1 if art['c_sent'] == "Negative" else 0
        weighted_score += direction * art['c_conf']
        total_weight += art['c_conf']

        # Print Entry
        icon = "🟢" if art['c_sent'] == "Positive" else "🔴" if art['c_sent'] == "Negative" else "⚪"
        print(f"{idx}. {icon} [{art['c_sent']} - {art['c_conf']:.2f}] {art['title']}")
        print(f"   Source: {art['source_type']} | Link: {art['url'][:60]}...")
        print("-" * 60)

    # Final Calculation
    print("\n" + "="*30)
    print("MARKET SENTIMENT CONCLUSION")
    print("="*30)

    total = len(articles)
    for k, v in summary.items():
        print(f"{k:<10}: {v} ({v/total:.1%})")

    # Avoid division by zero
    net_bias = weighted_score / total_weight if total_weight > 0 else 0
    
    print(f"\nNet Sentiment Score: {net_bias:.4f} (Scale: -1.0 to +1.0)")
    
    # Thresholds for decision
    if net_bias > 0.15:
        print("🚀 SIGNAL: BULLISH (Buy)")
    elif net_bias < -0.15:
        print("🐻 SIGNAL: BEARISH (Sell)")
    else:
        print("⚖️ SIGNAL: NEUTRAL (Wait/Sideways)")

if __name__ == "__main__":
    main()