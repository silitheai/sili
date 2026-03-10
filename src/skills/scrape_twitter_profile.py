import requests
from bs4 import BeautifulSoup
import re

def scrape_twitter_profile(username: str) -> str:
    """Scrapes a Twitter profile's bio, follower count, and recent tweets without an API key using Nitter (or similar public frontend)."""
    # Note: Twitter heavily blocks raw requests. We use a public Nitter instance as a proxy.
    # Nitter instances go down frequently, so we provide a few fallbacks.
    instances = [
        "https://nitter.net",
        "https://nitter.cz",
        "https://nitter.host",
        "https://nitter.poast.org"
    ]
    
    username = username.lstrip("@")
    
    for instance in instances:
        url = f"{instance}/{username}"
        try:
             res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}, timeout=8)
             if res.status_code == 200:
                  soup = BeautifulSoup(res.content, 'html.parser')
                  
                  # Get Profile Info
                  fullname = soup.find('a', class_='profile-card-fullname')
                  fullname = fullname.text.strip() if fullname else username
                  
                  bio = soup.find('div', class_='profile-bio')
                  bio = bio.text.strip() if bio else "No bio"
                  
                  stats = soup.find_all('span', class_='profile-stat-num')
                  tweets, following, followers, likes = "0", "0", "0", "0"
                  if len(stats) >= 4:
                       tweets = stats[0].text.strip()
                       following = stats[1].text.strip()
                       followers = stats[2].text.strip()
                       likes = stats[3].text.strip()
                       
                  output = f"🐦 --- TWITTER PROFILE: @{username} ---\n"
                  output += f"Name: {fullname}\nBio: {bio}\n"
                  output += f"Stats: {followers} Followers | {following} Following | {tweets} Tweets\n\n"
                  
                  # Get Recent Tweets
                  timeline = soup.find_all('div', class_='timeline-item')
                  output += "[Recent Tweets]\n"
                  
                  count = 0
                  for item in timeline:
                       if count >= 5: break
                       tweet_text_div = item.find('div', class_='tweet-content')
                       if tweet_text_div:
                            text = tweet_text_div.text.strip()
                            # Clean up
                            text = re.sub(r'\n+', ' ', text)
                            
                            stats_div = item.find_all('div', class_='tweet-stat')
                            engagement = ""
                            if len(stats_div) >= 4:
                                 eng_rtc = stats_div[1].text.strip()
                                 eng_likes = stats_div[2].text.strip()
                                 engagement = f" [❤️ {eng_likes} | 🔁 {eng_rtc}]"
                                 
                            output += f"- {text}{engagement}\n"
                            count += 1
                            
                  return output
        except Exception:
             continue # Try next instance
             
    return f"Failed to scrape Twitter profile for @{username}. All public proxy instances may be blocked or down."
