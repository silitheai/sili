import requests

def hackernews_top(limit: int = 5) -> str:
    """Retrieves the top stories currently trending on Hacker News (Y Combinator)."""
    try:
        # Get IDs of the top stories
        top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        res = requests.get(top_url, timeout=10)
        res.raise_for_status()
        top_ids = res.json()
        
        if not top_ids:
             return "Failed to fetch top story IDs from Hacker News."
             
        output = "--- Top Hacker News Stories Trending Right Now ---\n"
        limit = min(limit, len(top_ids))
        
        for i in range(limit):
            story_id = top_ids[i]
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            
            story_res = requests.get(story_url, timeout=5)
            story_res.raise_for_status()
            story_data = story_res.json()
            
            title = story_data.get('title', 'No Title')
            url = story_data.get('url', f"https://news.ycombinator.com/item?id={story_id}")
            score = story_data.get('score', 0)
            author = story_data.get('by', 'Unknown')
            
            output += f"{i+1}. {title} ({score} points by {author})\n"
            output += f"Link: {url}\n\n"
            
        return output
            
    except Exception as e:
        return f"Error fetching Hacker News data: {str(e)}"
