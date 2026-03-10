import requests

def analyze_reddit_subreddit(subreddit: str, limit: int = 5) -> str:
    """Extracts the top/hot trending posts from a specific Reddit community without requiring API keys."""
    # Reddit provides a .json endpoint for public subreddits
    try:
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
        
        res = requests.get(url, headers=headers, timeout=10)
        
        if res.status_code == 404:
            return f"Subreddit 'r/{subreddit}' not found or is private."
        elif res.status_code == 429:
            return "Reddit is rate-limiting the agent. Please try again later."
            
        res.raise_for_status()
        data = res.json()
        
        children = data.get('data', {}).get('children', [])
        if not children:
             return f"No posts found in r/{subreddit}."
             
        output = f"👾 --- REDDIT FRONTPAGE: r/{subreddit} ---\n\n"
        
        for i, post in enumerate(children, 1):
            p = post['data']
            title = p.get('title', 'No Title')
            author = p.get('author', 'Unknown')
            ups = p.get('score', 0)
            comments = p.get('num_comments', 0)
            url = p.get('url', '')
            text = p.get('selftext', '')
            
            output += f"{i}. {title}\n"
            output += f"   By: u/{author} | ⬆️ {ups:,} Upvotes | 💬 {comments:,} Comments\n"
            
            if text:
                 # Clean and truncate selftext
                 clean_text = text.replace('\n', ' ')
                 output += f"   Snippet: {clean_text[:150]}...\n"
            else:
                 output += f"   Link: {url}\n"
            output += "\n"
            
        return output
        
    except Exception as e:
        return f"Failed to analyze subreddit r/{subreddit}: {e}"
