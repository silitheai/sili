import yfinance as yf
from datetime import datetime

def stock_options_chain(ticker_symbol: str) -> str:
    """Fetches the nearest expiration Options Chain (Calls & Puts) for a given stock ticker."""
    try:
        ticker = yf.Ticker(ticker_symbol.upper())
        # Try to fetch fundamental info just to check if valid
        try:
             name = ticker.info.get('shortName', ticker_symbol.upper())
        except:
             return f"Error: '{ticker_symbol}' does not appear to be a valid stock ticker or Yahoo Finance blocked the request."
             
        expirations = ticker.options
        if not expirations:
            return f"No options chain data available for {name} ({ticker_symbol.upper()})."
            
        # Get the very next expiration date
        nearest_exp = expirations[0]
        chain = ticker.option_chain(nearest_exp)
        
        calls = chain.calls
        puts = chain.puts
        
        output = f"📈 --- OPTIONS CHAIN FOR {name} ({ticker_symbol.upper()}) ---\n"
        output += f"Expiration Date: {nearest_exp}\n"
        
        # Get Current Price roughly
        current_price = ticker.history(period='1d')['Close'].iloc[-1] if not ticker.history(period='1d').empty else 'Unknown'
        output += f"Current Underlying Price: ${current_price:.2f}\n\n"
        
        # Helper to format a mini table
        def format_options(df_opts, title, limit=5):
            # Sort by Open Interest to find where the action is
            df_opts = df_opts.sort_values(by='openInterest', ascending=False)
            res = f"[{title} - Top {limit} by Open Interest]\n"
            res += "Strike | Last Price | Volume | Open Interest | Implied Volatility\n"
            res += "-" * 60 + "\n"
            for _, row in df_opts.head(limit).iterrows():
                iv_pct = row.get('impliedVolatility', 0) * 100
                res += f"${row['strike']:<5} | ${row['lastPrice']:<8.2f} | {row.get('volume', 0):<6} | {row.get('openInterest', 0):<13} | {iv_pct:.1f}%\n"
            return res + "\n"
            
        output += format_options(calls, "CALLS (Bullish)")
        output += format_options(puts, "PUTS (Bearish)")
        
        return output
        
    except Exception as e:
        return f"Failed to retrieve options chain for {ticker_symbol}: {e}"
