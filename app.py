import streamlit as st
import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
import datetime

st.set_page_config(page_title="Bullish Stock Screener", layout="wide")
st.title("📈 Bullish Stock Screener (NIFTY 500)")
st.markdown("Scans stocks where **Close > EMA 10 & 20** and **RSI > 60**")

@st.cache_data
def load_symbols():
    url = "https://raw.githubusercontent.com/Mehul-29/stock-screener/main/nifty500.csv"
    df = pd.read_csv(url)
    return [symbol + ".NS" for symbol in df["Symbol"]]

symbols = load_symbols()
end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=15)

bullish = []

with st.spinner("🔍 Scanning NIFTY stocks..."):
    for symbol in symbols:
        try:
            df = yf.download(symbol, start=start_date, end=end_date, interval='1d', progress=False)
            df['rsi'] = RSIIndicator(close=df['Close']).rsi()
            df['ema10'] = EMAIndicator(close=df['Close'], window=10).ema_indicator()
            df['ema20'] = EMAIndicator(close=df['Close'], window=20).ema_indicator()
            last = df.iloc[-1]

            if last['Close'] > last['ema10'] and last['Close'] > last['ema20'] and last['rsi'] > 60:
                bullish.append({
                    'Stock': symbol.replace(".NS", ""),
                    'Close': round(last['Close'], 2),
                    'EMA10': round(last['ema10'], 2),
                    'EMA20': round(last['ema20'], 2),
                    'RSI': round(last['rsi'], 2)
                })
        except:
            continue

if bullish:
    st.success(f"✅ Found {len(bullish)} bullish stocks")
    st.dataframe(pd.DataFrame(bullish))
else:
    st.warning("⚠️ No bullish stocks found today.")
