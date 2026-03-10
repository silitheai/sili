import requests

def get_forex_rates(base_currency: str = "USD") -> str:
    """Fetches real-time, global foreign exchange (Forex) grid rates against a base currency."""
    base_currency = base_currency.upper()
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        
        res = requests.get(url, timeout=10)
        
        if res.status_code == 404:
             return f"Error: Base currency '{base_currency}' is invalid."
        res.raise_for_status()
        
        data = res.json()
        rates = data.get('rates', {})
        last_updated = data.get('time_last_updated', 'Unknown')
        
        # Key Global Pairs to always show
        major_pairs = ['EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'CNY', 'INR']
        
        output = f"🌍 --- GLOBAL FOREX GRID (Base: {base_currency}) ---\n"
        output += f"Last Updated: {last_updated}\n\n"
        
        output += "Major Pairs:\n"
        for p in major_pairs:
             if p in rates:
                  output += f"- {base_currency}/{p}: {rates[p]:.4f}\n"
                  
        output += "\nOther notable rates:\n"
        count = 0
        for currency, rate in rates.items():
             if currency not in major_pairs and currency != base_currency:
                  output += f"- {base_currency}/{currency}: {rate:.4f}\n"
                  count += 1
             if count > 10: # Limit spam
                  output += "... [Additional pairs available but truncated]"
                  break
                  
        return output
        
    except Exception as e:
        return f"Error fetching Forex grid: {e}"
