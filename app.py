import streamlit as st
import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from ta.volume import VolumeWeightedAveragePrice
import datetime

st.set_page_config(page_title="Bullish Stock Screener", layout="wide")
st.title("📈 Bullish Stock Screener (NIFTY 500)")
st.markdown("""
Scans stocks with:
- Close > EMA 10, 20, 50, 200  
- Close > VWAP  
- RSI > 60  
""")

@st.cache_data
def load_symbols():
    df = pd.read_csv("https://raw.githubusercontent.com/Mehul-29/stock_screener/main/nifty500.csv")
    return [s + ".NS" for s in df['Symbol']]

symbols = load_symbols()
end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=20)
bullish = []

with st.spinner("🔍 Scanning NIFTY 500 stocks..."):
    for symbol in symbols:
        try:
            df = yf.download(symbol, start=start_date, end=end_date, interval='1d', progress=False)

            if len(df) < 15:
                continue  # Skip stocks with insufficient data

            # Indicators
            df['ema10'] = EMAIndicator(close=df['Close'], window=10).ema_indicator()
            df['ema20'] = EMAIndicator(close=df['Close'], window=20).ema_indicator()
            df['ema50'] = EMAIndicator(close=df['Close'], window=50).ema_indicator()
            df['ema200'] = EMAIndicator(close=df['Close'], window=200).ema_indicator()
            df['rsi'] = RSIIndicator(close=df['Close']).rsi()

            vwap = VolumeWeightedAveragePrice(
                high=df['High'], low=df['Low'], close=df['Close'], volume=df['Volume']
            )
            df['vwap'] = vwap.vwap()

            last = df.iloc[-1]

            if (
                last['Close'] > last['ema10'] and
                last['Close'] > last['ema20'] and
                last['Close'] > last['ema50'] and
                last['Close'] > last['ema200'] and
                last['Close'] > last['vwap'] and
                last['rsi'] > 60
            ):
                bullish.append({
                    'Stock': symbol.replace(".NS", ""),
                    'Close': round(last['Close'], 2),
                    'EMA10': round(last['ema10'], 2),
                    'EMA20': round(last['ema20'], 2),
                    'EMA50': round(last['ema50'], 2),
                    'EMA200': round(last['ema200'], 2),
                    'VWAP': round(last['vwap'], 2),
                    'RSI': round(last['rsi'], 2)
                })

        except Exception as e:
            continue

if bullish:
    st.success(f"✅ Found {len(bullish)} bullish stocks")
    st.dataframe(pd.DataFrame(bullish))
else:
    st.warning("⚠️ No bullish stocks found today.")
