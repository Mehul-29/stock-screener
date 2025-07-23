import streamlit as st
import pandas as pd
import yfinance as yf
import ta

st.set_page_config(page_title="Debug Bullish Screener", layout="wide")
st.title("🛠️ Debug Bullish Stock Screener (NIFTY 500)")

@st.cache_data
def load_symbols():
    df = pd.read_csv("https://raw.githubusercontent.com/Mehul-29/stock-screener/main/nifty500.csv")
    return [s + '.NS' for s in df['Symbol']]

symbols = load_symbols()[:50]  # Testing with first 50 symbols
st.write(f"✅ Loaded {len(symbols)} symbols")

bullish = []
debug = []

for symbol in symbols:
   try:
    df = yf.download(symbol, interval="5m", period="5d", progress=False)
    if df.empty or "Close" not in df.columns or df["Close"].isnull().all():
        debug.append({"Stock": symbol.replace(".NS", ""), "Failed": "No 5-min data"})
        continue

    df["vwap"] = (df["High"] + df["Low"] + df["Close"]) / 3

    close_series = df["Close"].dropna()
    if close_series.shape[0] < 15:
        debug.append({"Stock": symbol.replace(".NS", ""), "Failed": "Insufficient 5-min candles for RSI"})
        continue

   close_series = df["Close"].dropna()

if len(close_series) < 15:
    debug.append({"Stock": symbol.replace(".NS", ""), "Failed": "Not enough Close data for RSI"})
    continue

try:
    rsi = ta.momentum.RSIIndicator(close_series).rsi()
    df = df.loc[rsi.index]  # align to valid index
    df["rsi"] = rsi
except Exception as e:
    debug.append({"Stock": symbol.replace(".NS", ""), "Failed": f"RSI Error: {str(e)}"})
    continue

    latest = df.iloc[-1]

    df_daily = yf.download(symbol, interval="1d", period="1y", progress=False)
    if df_daily.empty or "Close" not in df_daily.columns or df_daily["Close"].isnull().all():
        debug.append({"Stock": symbol.replace(".NS", ""), "Failed": "No daily data"})
        continue

    daily_close = df_daily["Close"].fillna(method="ffill")
    df_daily["ema10"] = ta.trend.ema_indicator(daily_close, window=10)
    df_daily["ema20"] = ta.trend.ema_indicator(daily_close, window=20)
    df_daily["ema50"] = ta.trend.ema_indicator(daily_close, window=50)
    df_daily["ema200"] = ta.trend.ema_indicator(daily_close, window=200)

    latest_daily = df_daily.iloc[-1]

    # Screening Conditions
    reasons = []
    if latest_daily["Close"] <= latest_daily["ema10"]:
        reasons.append("Close < EMA10")
    if latest_daily["Close"] <= latest_daily["ema20"]:
        reasons.append("Close < EMA20")
    if latest_daily["Close"] <= latest_daily["ema50"]:
        reasons.append("Close < EMA50")
    if latest_daily["Close"] <= latest_daily["ema200"]:
        reasons.append("Close < EMA200")
    if latest["Close"] <= latest["vwap"]:
        reasons.append("Close < VWAP")
    if latest["rsi"] <= 60 or pd.isna(latest["rsi"]):
        reasons.append("RSI ≤ 60 or NaN")

    if not reasons:
        bullish.append({
            "Stock": symbol.replace(".NS", ""),
            "Close": round(latest["Close"], 2),
            "VWAP": round(latest["vwap"], 2),
            "RSI": round(latest["rsi"], 2)
        })
    else:
        debug.append({"Stock": symbol.replace(".NS", ""), "Failed": ", ".join(reasons)})

except Exception as e:
    debug.append({"Stock": symbol.replace(".NS", ""), "Failed": str(e)})
        

# Show results
if bullish:
    st.success(f"✅ Found {len(bullish)} bullish stocks")
    st.dataframe(pd.DataFrame(bullish))
else:
    st.warning("⚠️ No bullish stocks found")

st.markdown("---")
st.subheader("🔎 Debug Details")
st.dataframe(pd.DataFrame(debug))
