import requests

def fetch_hacker_news_user(username: str) -> str:
    """Retrieves karma, creation date, and recent submissions for a specific Hacker News user."""
    try:
        url = f"https://hacker-news.firebaseio.com/v0/user/{username}.json"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        
        data = res.json()
        if not data:
             return f"Hacker News user '{username}' not found."
             
        from datetime import datetime
        created_time = datetime.fromtimestamp(data.get('created', 0)).strftime('%Y-%m-%d')
        
        output = f"--- HACKER NEWS PROFILE: {username} ---\n"
        output += f"Karma / Points: {data.get('karma', 0):,}\n"
        output += f"Account Created: {created_time}\n"
        
        about = data.get('about')
        if about:
            # Strip simple HTML from about
            import re
            about_clean = re.sub('<[^<]+>', '', about)
            output += f"Bio: {about_clean}\n"
            
        # Recent submissions (IDs only, to prevent massive lag)
        subs = data.get('submitted', [])
        output += f"Total Actions/Submissions: {len(subs):,}\n"
        
        return output
        
    except Exception as e:
        return f"Failed to fetch Hacker News user {username}: {e}"
