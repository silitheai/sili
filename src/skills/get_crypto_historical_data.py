import requests
from datetime import datetime

def get_crypto_historical_data(coin_id: str, days: int = 30) -> str:
    """Fetches high-density historical OHLCV (Open, High, Low, Close, Volume) data for a given cryptocurrency via CoinGecko."""
    try:
        # CoinGecko's market_chart API returns daily granularity for days > 1 up to 90
        # For OHLC, they have a specific endpoint Returns: [ [time, open, high, low, close] ]
        
        # We need mapping. Ensure coin_id is lowercase. e.g., 'bitcoin', 'ethereum'
        coin_id = coin_id.lower().replace(" ", "-")
        
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
        
        headers = {"Accept": "application/json"}
        res = requests.get(url, headers=headers, timeout=15)
        
        if res.status_code == 404:
             return f"Error: Cryptocurrency '{coin_id}' not found. Please use the full name (e.g., 'bitcoin', 'ethereum', 'solana')."
        res.raise_for_status()
        
        data = res.json()
        if not data:
             return f"No historical OHLC data found for {coin_id} over the last {days} days."
             
        output = f"📉 --- {coin_id.upper()} HISTORICAL OHLC DATA (Past {days} Days) ---\n"
        output += "Format: Date | Open | High | Low | Close\n"
        output += "-" * 55 + "\n"
        
        # Limit the output matrix to avoid blowing out context memory
        limit = min(50, len(data))
        # Take the most recent data points (tail)
        data = data[-limit:]
        
        for row in data:
            timestamp, open_p, high_p, low_p, close_p = row
            date_str = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
            
            # Format nicely
            output += f"{date_str} | O: ${open_p:,.2f} | H: ${high_p:,.2f} | L: ${low_p:,.2f} | C: ${close_p:,.2f}\n"
            
        return output
        
    except Exception as e:
        return f"Failed to retrieve crypto historical data: {e}"
