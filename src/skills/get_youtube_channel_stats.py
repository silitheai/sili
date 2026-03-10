import requests
import re

def get_youtube_channel_stats(channel_id_or_handle: str) -> str:
    """Retrieves subscriber count, total views, and video count for a YouTube channel using public metadata."""
    try:
        # We try to use a public endpoint or scrape the channel page
        # YouTube is aggressive with scraping, but channel about pages often have metadata in the source
        if not channel_id_or_handle.startswith("@") and not channel_id_or_handle.startswith("UC"):
            channel_id_or_handle = "@" + channel_id_or_handle
            
        url = f"https://www.youtube.com/{channel_id_or_handle}/about"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        
        # YouTube stores data in a large JSON object 'ytInitialData' in the script tag
        content = res.text
        
        # Extract subscriber count
        sub_match = re.search(r'"subscriberCountText":\{"simpleText":"(.*?)"\}', content)
        subs = sub_match.group(1) if sub_match else "Unknown"
        
        # Extract video count
        video_match = re.search(r'"videoCountText":\{"runs":\[\{"text":"(.*?)"\}', content)
        videos = video_match.group(1) if video_match else "Unknown"
        
        # Extract views
        view_match = re.search(r'"viewCountText":"(.*?)"', content)
        views = view_match.group(1) if view_match else "Unknown"
        
        # Extract title
        title_match = re.search(r'<meta property="og:title" content="(.*?)">', content)
        title = title_match.group(1) if title_match else channel_id_or_handle

        output = f"📺 --- YOUTUBE CHANNEL STATS: {title} ---\n"
        output += f"Subscribers: {subs}\n"
        output += f"Total Videos: {videos}\n"
        output += f"Total Views: {views}\n"
        output += f"URL: https://www.youtube.com/{channel_id_or_handle}\n"
        
        return output
        
    except Exception as e:
        return f"Failed to retrieve YouTube stats for {channel_id_or_handle}: {e}"
