import requests
import json
from datetime import datetime

def trend_analyzer(topic: str) -> str:
    """Aggregates data from multiple sources (HackerNews, Reddit, Google News) to identify if a topic is emerging or viral."""
    try:
        output = f"🔥 --- VIRAL TREND ANALYSIS: '{topic.upper()}' ---\n"
        output += f"Analyzed At: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        # 1. Check HackerNews (via Algolia API for search)
        hn_url = f"https://hn.algolia.com/api/v1/search?query={topic}&tags=story&numericFilters=created_at_i>{int(datetime.now().timestamp()) - 86400*7}"
        hn_res = requests.get(hn_url, timeout=10)
        hn_count = 0
        if hn_res.status_code == 200:
            hn_count = hn_res.json().get('nbHits', 0)
            output += f"[1] HackerNews Activity (Last 7 Days): {hn_count} mentions/stories.\n"
        
        # 2. Check Reddit
        headers = {'User-Agent': 'Mozilla/5.0'}
        reddit_url = f"https://www.reddit.com/search.json?q={topic}&sort=relevance&t=week"
        reddit_res = requests.get(reddit_url, headers=headers, timeout=10)
        reddit_hits = 0
        if reddit_res.status_code == 200:
            data = reddit_res.json()
            reddit_hits = len(data.get('data', {}).get('children', []))
            output += f"[2] Reddit Recent Hits: {reddit_hits} significant threads/mentions.\n"
            
        # 3. Google News RSS check
        gn_url = f"https://news.google.com/rss/search?q={topic}&hl=en-US&gl=US&ceid=US:en"
        gn_res = requests.get(gn_url, timeout=10)
        gn_count = 0
        if gn_res.status_code == 200:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(gn_res.content)
            gn_count = len(root.findall('.//item'))
            output += f"[3] Google News Visibility: {gn_count} recent global headlines.\n"

        # Logic for Viral Verdict
        total_score = hn_count + (reddit_hits * 10) + (gn_count * 5)
        
        output += "\n--- VERDICT ---\n"
        if total_score > 500:
            output += "🚀 STATUS: HYPER-VIRAL. This topic is dominating the current global zeitgeist.\n"
        elif total_score > 100:
            output += "📈 STATUS: EMERGING TREND. High growth in mentions and community engagement.\n"
        elif total_score > 20:
            output += "🔍 STATUS: NICHE TOPIC. Consistent activity within specific communities.\n"
        else:
            output += "💤 STATUS: QUIET. Minimal public discourse or news coverage.\n"
            
        return output
        
    except Exception as e:
        return f"Trend analysis failed: {e}"
