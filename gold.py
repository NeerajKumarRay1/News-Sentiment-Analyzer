import feedparser
import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from urllib.parse import quote, urlparse, parse_qs
from datetime import datetime
import time

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

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

ARTICLES_PER_QUERY = 8
MIN_CONTENT_LENGTH = 120   # characters
REQUEST_TIMEOUT = 10

# =========================
# LOAD MODELS
# =========================
print("Loading sentiment models...")

vader = SentimentIntensityAnalyzer()

finbert_tokenizer = AutoTokenizer.from_pretrained(
    "yiyanghkust/finbert-tone"
)
finbert_model = AutoModelForSequenceClassification.from_pretrained(
    "yiyanghkust/finbert-tone"
)
finbert_model.eval()

FINBERT_LABELS = ["Negative", "Neutral", "Positive"]

# =========================
# HELPER FUNCTIONS
# =========================
def resolve_google_news_url(url):
    """Extract real article URL from Google News redirect."""
    try:
        parsed = urlparse(url)
        if "news.google.com" in parsed.netloc:
            return parse_qs(parsed.query).get("url", [url])[0]
        return url
    except:
        return url


def fetch_article_content(url):
    """Scrape article text from webpage."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs)

        return text.strip()
    except:
        return ""


def analyze_headline_sentiment(text):
    """Fast VADER sentiment for headlines."""
    score = vader.polarity_scores(text)["compound"]

    if score > 0.05:
        return score, "Positive"
    elif score < -0.05:
        return score, "Negative"
    else:
        return score, "Neutral"


def analyze_finbert_sentiment(text):
    """Finance-specific sentiment using FinBERT."""
    inputs = finbert_tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    with torch.no_grad():
        outputs = finbert_model(**inputs)

    probs = torch.softmax(outputs.logits, dim=1).numpy()[0]
    idx = np.argmax(probs)

    return probs[idx], FINBERT_LABELS[idx]


# =========================
# FETCH NEWS
# =========================
def fetch_news():
    seen_urls = set()
    articles = []

    for query in QUERIES:
        print(f"\nFetching news for: {query}")
        rss_url = f"https://news.google.com/rss/search?q={quote(query)}"
        feed = feedparser.parse(rss_url)

        for entry in feed.entries[:ARTICLES_PER_QUERY]:
            url = resolve_google_news_url(entry.link)

            if url in seen_urls:
                continue

            seen_urls.add(url)

            content = fetch_article_content(url)

            # DEBUG (remove later)
            print("Content length:", len(content))

            if len(content) < MIN_CONTENT_LENGTH:
                content = entry.title  # fallback

            articles.append({
                "title": entry.title,
                "url": url,
                "published": entry.get("published", ""),
                "content": content
            })

            time.sleep(0.3)

    return articles



# =========================
# MAIN ANALYSIS
# =========================
def main():
    articles = fetch_news()

    if not articles:
        print("No valid articles found.")
        return

    summary = {
        "Positive": 0,
        "Negative": 0,
        "Neutral": 0
    }

    weighted_score = 0.0
    total_weight = 0.0

    print("\n==============================")
    print("ARTICLE-WISE SENTIMENT")
    print("==============================\n")

    for idx, article in enumerate(articles, 1):
        h_score, h_sent = analyze_headline_sentiment(article["title"])
        c_conf, c_sent = analyze_finbert_sentiment(article["content"])

        summary[c_sent] += 1
        weighted_score += c_conf * (1 if c_sent == "Positive" else -1 if c_sent == "Negative" else 0)
        total_weight += c_conf

        print(f"{idx}. {article['title']}")
        print(f"   Headline Sentiment : {h_sent} ({h_score:.2f})")
        print(f"   Content Sentiment  : {c_sent} (confidence {c_conf:.2f})")
        print(f"   Link: {article['url']}\n")

    # =========================
    # FINAL MARKET BIAS
    # =========================
    print("==============================")
    print("MARKET SENTIMENT SUMMARY")
    print("==============================")

    total_articles = len(articles)

    for k, v in summary.items():
        print(f"{k}: {v} ({(v/total_articles)*100:.2f}%)")

    net_bias = weighted_score / total_weight if total_weight else 0

    print("\nNet Sentiment Score:", round(net_bias, 3))

    if net_bias > 0.15:
        print("📈 Overall Market Bias: BULLISH")
    elif net_bias < -0.15:
        print("📉 Overall Market Bias: BEARISH")
    else:
        print("⚖ Overall Market Bias: NEUTRAL / SIDEWAYS")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()
