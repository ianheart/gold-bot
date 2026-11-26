import os
import requests
import yfinance as yf
import pandas as pd

TOKEN = (os.environ.get("TELEGRAM_TOKEN") or "").strip()
CHAT_ID = (os.environ.get("TELEGRAM_CHAT_ID") or "").strip()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.get(url, params={"chat_id": CHAT_ID, "text": msg}, timeout=20)

def check(symbol, name):
    try:
        df = yf.download(symbol, period="1d", interval="15m", progress=False)
        if df.empty:
            return
        price = float(df["Close"].iloc[-1])
        send_telegram(f"📊 {name}: ${price:.2f}")
    except Exception as e:
        print(f"Error {name}: {e}")

print("Bot starting...")
send_telegram("Bot is alive ✅ Test message — BTC, GOLD, EUR/USD")
check("BTC-USD", "BTC/USD")
check("XAUUSD=X", "GOLD")
check("EURUSD=X", "EUR/USD")
print("Bot finished check")
