import requests
import json

def get_stock_price(ticker: str) -> str:
    """Fetches the current stock price via Yahoo Finance API."""
    try:
        # User-Agent is required to bypass simple blocking
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker.upper()}?interval=1m"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        result = data.get('chart', {}).get('result', [])
        if not result:
            return f"Stock {ticker} not found."
            
        meta = result[0].get('meta', {})
        price = meta.get('regularMarketPrice', 'Unknown')
        currency = meta.get('currency', 'USD')
        
        return f"The current price for {ticker.upper()} is {price} {currency}."
    except Exception as e:
        return f"Error fetching stock price: {str(e)}"
