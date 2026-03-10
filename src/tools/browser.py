import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))

def brave_web_search(query: str) -> str:
    """Performs a web search using the Brave Search API.
    
    Args:
        query: The search term or question to look up on the web.
    """
    api_key = os.getenv("BRAVE_SEARCH_API_KEY")
    if not api_key:
        return "Error: BRAVE_SEARCH_API_KEY is not set in the .env file. Please run setup.py or configure it manually."

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key
    }
    
    try:
        url = f"https://api.search.brave.com/res/v1/web/search?q={requests.utils.quote(query)}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return f"Search API Error: Status {response.status_code} - {response.text}"
            
        data = response.json()
        results = data.get("web", {}).get("results", [])
        
        if not results:
            return f"No results found for query: {query}"
            
        formatted_results = f"Search Results for '{query}':\n\n"
        # Only return top 5 results to save context space
        for idx, item in enumerate(results[:5]):
            formatted_results += f"{idx+1}. Title: {item.get('title')}\n"
            formatted_results += f"   URL: {item.get('url')}\n"
            formatted_results += f"   Snippet: {item.get('description')}\n\n"
            
        return formatted_results.strip()
        
    except Exception as e:
        return f"Error executing web search: {str(e)}"
