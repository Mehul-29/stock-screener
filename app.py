import yfinance as yf
import pandas as pd
import streamlit as st
import ta

@st.cache_data
def load_symbols():
    df = pd.read_csv("nifty500.csv")
    return [s + ".NS" for s in df['Symbol']]

def check_conditions(symbol):
    try:
        # Download 5 min data (last 5 days)
        df_5m = yf.download(symbol, interval="5m", period="5d", progress=False)
        if df_5m.empty:
            return False
        
        df_5m.dropna(inplace=True)

        # Calculate VWAP
        df_5m["vwap"] = ta.volume.VolumeWeightedAveragePrice(
            high=df_5m["High"], low=df_5m["Low"], close=df_5m["Close"], volume=df_5m["Volume"]
        ).vwap()

        # Calculate RSI
        df_5m["rsi"] = ta.momentum.RSIIndicator(close=df_5m["Close"]).rsi()

        # Get latest row
        latest = df_5m.iloc[-1]
        
        # Get Daily data
        df_daily = yf.download(symbol, interval="1d", period="100d", progress=False)
        df_daily.dropna(inplace=True)

        df_daily["ema10"] = ta.trend.ema_indicator(df_daily["Close"], window=10)
        df_daily["ema20"] = ta.trend.ema_indicator(df_daily["Close"], window=20)
        df_daily["ema50"] = ta.trend.ema_indicator(df_daily["Close"], window=50)
        df_daily["ema200"] = ta.trend.ema_indicator(df_daily["Close"], window=200)

        latest_daily = df_daily.iloc[-1]

        # Condition checks
        conditions = [
            latest_daily["Close"] > latest_daily["ema10"],
            latest_daily["Close"] > latest_daily["ema20"],
            latest_daily["Close"] > latest_daily["ema50"],
            latest_daily["Close"] > latest_daily["ema200"],
            latest["Close"] > latest["vwap"],
            latest["rsi"] > 60,
        ]

        return all(conditions)

    except Exception as e:
        print(f"Error checking {symbol}: {e}")
        return False


st.title("NSE Stock Screener")

symbols = load_symbols()
passed = []

st.text("Scanning stocks... This may take a few minutes ⏳")

for symbol in symbols:
    if check_conditions(symbol):
        passed.append(symbol)

st.success(f"{len(passed)} stocks passed the filters ✅")
st.write(passed)
