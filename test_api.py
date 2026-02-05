#!/usr/bin/env python3
"""
Quick API test for the running application
"""

import requests
import json

def test_api():
    try:
        print('🧪 Testing analysis endpoint...')
        response = requests.post('http://localhost:5000/api/analysis/start', 
                               json={'query': 'gold', 'category': 'commodity'}, 
                               timeout=30)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print('✅ Analysis successful!')
            print(f'Market Signal: {data.get("market_signal", "N/A")}')
            print(f'Articles Analyzed: {data.get("total_articles", 0)}')
            print(f'Processing Time: {data.get("processing_time", 0):.2f}s')
            print(f'Net Sentiment Score: {data.get("net_sentiment_score", 0):.3f}')
        else:
            print(f'❌ Error: {response.text}')
    except Exception as e:
        print(f'❌ Request failed: {e}')

if __name__ == '__main__':
    test_api()