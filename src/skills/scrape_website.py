import urllib.request
from bs4 import BeautifulSoup
import re

def scrape_website(url: str) -> str:
    """Extracts raw, readable text content from a specified URL."""
    try:
        # Basic User-Agent to prevent simple 403s
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read()
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove noisy tags
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.extract()
            
        text = soup.get_text(separator=' ')
        
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Prevent context window overflow
        if len(text) > 20000:
            text = text[:20000] + "... [TRUNCATED DUE TO LENGTH]"
            
        return f"--- Content from {url} ---\n{text}"
    except Exception as e:
        return f"Error scraping {url}: {e}"
