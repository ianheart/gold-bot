import os, requests

TOKEN = os.getenv("9287774486:AAGlkZmUhj3KndwaOaRakeLNpFn4EIi911E")
CHAT_ID = os.getenv("8803846659")

PAIRS = {
    "XAUUSD": "GC=F",
    "USDJPY": "USDJPY=X",
    "BTCUSD": "BTC-USD",
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "AUDUSD": "AUDUSD=X",
}

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def get_data(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5d&interval=1h"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=15).json()
    closes = r["chart"]["result"][0]["indicators"]["quote"][0]["close"]
    closes = [c for c in closes if c is not None]
    return closes

def rsi(closes, period=14):
    gains, losses = 0, 0
    for i in range(1, period+1):
        diff = closes[-i] - closes[-i-1]
        if diff > 0:
            gains += diff
        else:
            losses += -diff
    rs = (gains/period) / (losses/period + 0.000001)
    return 100 - (100 / (1 + rs))

for name, symbol in PAIRS.items():
    try:
        closes = get_data(symbol)
        price = closes[-1]
        sma20 = sum(closes[-20:]) / 20
        sma50 = sum(closes[-50:]) / 50
        r = rsi(closes)
        
        signal = None
        tp = sl = 0
        if price > sma20 and price > sma50 and r < 68:
            signal = "🟢 BUY"
            tp = price * 1.002
            sl = price * 0.998
        elif price < sma20 and price < sma50 and r > 32:
            signal = "🔴 SELL"
            tp = price * 0.998
            sl = price * 1.002
        
        if signal:
            style = "SCALP" if 35 < r < 65 else "SWING"
            msg = f"📊 *{name} {signal} - {style}*\n\nPrice: `{price:.2f}`\nRSI: `{r:.1f}`\nTP: `{tp:.2f}`\nSL: `{sl:.2f}`\n\n⚠️ Not financial advice. Manage risk."
            send(msg)
            print(f"Sent {name} {signal}")
        else:
            print(f"No setup {name} RSI {r:.1f}")
    except Exception as e:
        print(f"Error {name}: {e}")

print("Done check")
