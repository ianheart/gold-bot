import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_telegram(msg):
    if not TOKEN or not CHAT_ID:
        print("Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID secret")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": msg}).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=20) as r:
        print("Telegram sent:", r.status)

def get_price(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=15m"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        j = json.loads(r.read().decode())
    result = j["chart"]["result"][0]
    closes = [c for c in result["indicators"]["quote"][0]["close"] if c is not None]
    return closes

def check(symbol, name):
    try:
        closes = get_price(symbol)
        if len(closes) < 15:
            print(f"{name}: not enough data")
            return
        last = closes[-1]
        gains = 0
        losses = 0
        for i in range(-14, 0):
            diff = closes[i] - closes[i-1]
            if diff > 0:
                gains += diff
            else:
                losses += -diff
        avg_gain = gains / 14
        avg_loss = losses / 14
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        print(f"{name}: price={last:.2f} RSI={rsi:.1f}")
        if rsi < 30:
            send_telegram(f"🟢 BUY {name}\nPrice: {last:.2f}\nRSI: {rsi:.1f} (Oversold)\nTime: {datetime.now().strftime('%H:%M')}")
        elif rsi > 70:
            send_telegram(f"🔴 SELL {name}\nPrice: {last:.2f}\nRSI: {rsi:.1f} (Overbought)\nTime: {datetime.now().strftime('%H:%M')}")
        else:
            print(f"{name}: No setup, RSI in middle")
    except Exception as e:
        print(f"{name} error: {e}")

print("Bot starting...")
send_telegram("Bot is alive ✅ Test message - BTC check running")
check("BTC-USD", "BTC/USD")
check("XAUUSD=X", "GOLD")
check("EURUSD=X", "EUR/USD")
print("Bot finished check")
