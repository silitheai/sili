import requests

def currency_converter(amount: float, from_currency: str, to_currency: str) -> str:
    """Converts an amount of fiat currency using real-time open exchange rates."""
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    # Public, no-key free tier exchange rate API
    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    
    try:
        res = requests.get(url, timeout=10)
        
        if res.status_code == 404:
             return f"Error: Base currency '{from_currency}' is not supported or invalid."
        res.raise_for_status()
        
        data = res.json()
        rates = data.get('rates', {})
        
        if to_currency not in rates:
             return f"Error: Target currency '{to_currency}' is not supported."
             
        rate = rates[to_currency]
        converted_amount = amount * rate
        last_updated = data.get('time_last_updated', 'Unknown')
        
        output = f"💱 {amount:,.2f} {from_currency} = {converted_amount:,.2f} {to_currency}\n"
        output += f"(Exchange Rate: 1 {from_currency} = {rate} {to_currency} | Last Updated: {last_updated})"
        
        return output
        
    except Exception as e:
        return f"Error fetching exchange rate data: {e}"
