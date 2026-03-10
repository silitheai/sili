import feedparser

def read_rss_feed(feed_url: str, limit: int = 5) -> str:
    """Reads an RSS/Atom feed and returns the most recent post headlines and summaries."""
    try:
        feed = feedparser.parse(feed_url)
        
        if feed.bozo:
             return f"Error parsing RSS feed stream (Bozo flag set): {feed.bozo_exception}"
             
        title = feed.feed.get('title', 'Unknown Feed Title')
        output = f"--- RSS FEED: {title} ---\n\n"
        
        entries = feed.entries[:limit]
        if not entries:
            return f"No entries found in RSS feed '{feed_url}'"
            
        for i, entry in enumerate(entries):
            entry_title = entry.get('title', 'No Title')
            entry_link = entry.get('link', 'No Link')
            
            # Use raw description if plain text summary is missing
            try:
                summary = entry.get('summary', '')[:200]
            except Exception:
                summary = entry.get('description', '')[:200]
                
            output += f"{i+1}. {entry_title}\n"
            output += f"Link: {entry_link}\n"
            if summary:
                output += f"Summary snippet: {summary}...\n"
            output += "-" * 20 + "\n"
            
        return output
    except Exception as e:
        return f"Error reading RSS feed '{feed_url}': {str(e)}"
