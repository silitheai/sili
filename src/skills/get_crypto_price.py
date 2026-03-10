import requests

def get_crypto_price(coin_id: str = "bitcoin") -> str:
    """Fetches the current USD price of a cryptocurrency (e.g., 'bitcoin', 'ethereum') from CoinGecko."""
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id.lower()}&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if coin_id.lower() in data:
            price = data[coin_id.lower()]['usd']
            return f"The current price of {coin_id.capitalize()} is ${price:,.2f} USD."
        else:
            return f"Price for {coin_id} not found."
    except Exception as e:
        return f"Error fetching crypto price: {str(e)}"
