import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator
from ta.volatility import BollingerBands
import json

def calculate_technical_indicators(json_prices: str) -> str:
    """Calculates advanced technical indicators (RSI, MACD, Bollinger Bands) given a JSON array of chronological closing prices [100.5, 102.3, ...]."""
    try:
        # Parse the raw array
        try:
             prices = json.loads(json_prices)
             if not isinstance(prices, list) or len(prices) < 30:
                  return "Error: Input must be a JSON array of at least 30 numerical closing prices to calculate indicators accurately."
        except json.JSONDecodeError:
             return "Error: Invalid JSON format. Expected an array of numbers like '[1.5, 2.0, 3.1]'."
             
        # Convert to pandas series
        df = pd.DataFrame(prices, columns=['close'])
        df['close'] = pd.to_numeric(df['close'])
        
        # Calculate RSI (14 period)
        rsi = RSIIndicator(close=df['close'], window=14).rsi()
        df['rsi'] = round(rsi, 2)
        
        # Calculate MACD
        macd = MACD(close=df['close'])
        df['macd'] = round(macd.macd(), 4)
        df['macd_signal'] = round(macd.macd_signal(), 4)
        df['macd_histogram'] = round(macd.macd_diff(), 4)
        
        # Calculate Bollinger Bands
        indicator_bb = BollingerBands(close=df['close'], window=20, window_dev=2)
        df['bb_upper'] = round(indicator_bb.bollinger_hband(), 2)
        df['bb_lower'] = round(indicator_bb.bollinger_lband(), 2)
        
        # Moving Averages
        df['sma_20'] = round(SMAIndicator(close=df['close'], window=20).sma_indicator(), 2)
        
        # We only care about the most recent/current indicator state
        current = df.iloc[-1]
        prev = df.iloc[-2]
        
        output = f"📊 --- ADVANCED TECHNICAL ANALYSIS ---\n"
        output += f"Current Closing Price Analyzer Input: {current['close']}\n\n"
        
        # RSI Analysis
        rsi_val = current['rsi']
        rsi_state = "Overbought (Bearish)" if rsi_val > 70 else "Oversold (Bullish)" if rsi_val < 30 else "Neutral"
        output += f"[RSI (14)]\n- Value: {rsi_val} ({rsi_state})\n\n"
        
        # MACD Analysis
        macd_val = current['macd']
        sig_val = current['macd_signal']
        hist_val = current['macd_histogram']
        macd_cross = "BULLISH CROSSOVER" if macd_val > sig_val and prev['macd'] <= prev['macd_signal'] else "BEARISH CROSSOVER" if macd_val < sig_val and prev['macd'] >= prev['macd_signal'] else "No cross"
        output += f"[MACD (12,26,9)]\n- MACD Line: {macd_val}\n- Signal Line: {sig_val}\n- Histogram: {hist_val}\n- Status: {macd_cross}\n\n"
        
        # Bollinger Bands Analysis
        output += f"[BOLLINGER BANDS (20,2)]\n- Upper Band: {current['bb_upper']}\n- Lower Band: {current['bb_lower']}\n- SMA 20: {current['sma_20']}\n"
        
        p = current['close']
        if p > current['bb_upper']:
             output += "- Price Action: Breaking UPPER band (Strong momentum / Over-extension).\n"
        elif p < current['bb_lower']:
             output += "- Price Action: Breaking LOWER band (Severe drop / Reversal possible).\n"
        else:
             output += "- Price Action: Containing within bands.\n"
             
        return output
        
    except Exception as e:
         return f"Failed to compute technical indicators. Make sure pandas and ta are installed. Error: {e}"
