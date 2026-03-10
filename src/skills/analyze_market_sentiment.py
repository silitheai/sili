import requests
from bs4 import BeautifulSoup
import re

def analyze_market_sentiment() -> str:
    """Aggregates the Crypto Fear & Greed index and general financial sentiment from rapid headline scanning."""
    try:
        output = "🧠 --- GLOBAL MARKET SENTIMENT ANALYSIS ---\n\n"
        
        # 1. Fetch Crypto Fear & Greed
        fn_url = "https://api.alternative.me/fng/"
        res = requests.get(fn_url, timeout=10)
        
        if res.status_code == 200:
            data = res.json().get('data', [])[0]
            val = data.get('value')
            classification = data.get('value_classification')
            output += f"[1] Crypto Fear & Greed Index:\n- Score: {val}/100\n- Status: {classification}\n\n"
        else:
            output += "[1] Crypto Fear & Greed Index: Failed to retrieve.\n\n"
            
        # 2. Fetch Rapid Macro Headlines (CNBC/Yahoo/Reuters proxy via simple RSS/Scrape)
        # Using a reliable free RSS or generalized HTML to avoid massive captchas
        news_url = "https://finance.yahoo.com/rss/topstories"
        try:
             import xml.etree.ElementTree as ET
             news_res = requests.get(news_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
             root = ET.fromstring(news_res.content)
             
             items = root.findall('.//item')
             
             output += "[2] Top Macro Financial Headlines (Yahoo Finance):\n"
             
             # Very basic zero-dep word matching for sentiment
             bullish_words = ['surge', 'jump', 'rally', 'record', 'gain', 'buy', 'up', 'growth', 'beat']
             bearish_words = ['drop', 'fall', 'plunge', 'crash', 'sell', 'down', 'loss', 'miss', 'fear']
             
             bull_score = 0
             bear_score = 0
             
             for i, item in enumerate(items[:7], 1): # Top 7 headlines
                  title = item.find('title').text
                  output += f"- {title}\n"
                  
                  t_lower = title.lower()
                  for w in bullish_words:
                       if re.search(r'\b' + w + r'\b', t_lower): bull_score += 1
                  for w in bearish_words:
                       if re.search(r'\b' + w + r'\b', t_lower): bear_score += 1
                       
             # Macro Verdict
             output += f"\nHeadline Sentiment Parser (Bullish Keywords: {bull_score} | Bearish Keywords: {bear_score})\n"
             if bull_score > bear_score + 1:
                  output += "- Macro Verdict: Short-term Bullish Lean 🟢\n"
             elif bear_score > bull_score + 1:
                  output += "- Macro Verdict: Short-term Bearish Lean 🔴\n"
             else:
                  output += "- Macro Verdict: Neutral / Mixed 🟡\n"
                  
        except Exception as e:
             output += f"[2] Failed to fetch macro headlines: {e}"
             
        return output
        
    except Exception as e:
         return f"Critical error calculating market sentiment: {e}"
