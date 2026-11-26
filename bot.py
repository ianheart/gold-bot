import os, requests
import yfinance as yf

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

PAIRS = {
    "XAUUSD": "GC=F",
    "USDJPY": "USDJPY=X",
    "BTC": "BTC-USD",
    "EUR/USD": "EURUSD=X"
}

def get_signal(symbol):
    df = yf.download(symbol, period="5d", interval="1h", progress=False)
    if df.empty or len(df) < 30:
        return None
    close = df['Close'].flatten()
    ema9 = close.ewm(span=9).mean().iloc[-1]
    ema21 = close.ewm(span=21).mean().iloc[-1]
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
    loss = -delta.where(delta < 0, 0).rolling(14).mean().iloc[-1]
    rsi = 100 - (100 / (1 + gain / loss)) if loss != 0 else 50
    price = float(close.iloc[-1])
    
    if ema9 > ema21 and rsi < 70:
        signal, sl, tp = "🟢 BUY", price * 0.997, price * 1.006
    elif ema9 < ema21 and rsi > 30:
        signal, sl, tp = "🔴 SELL", price * 1.003, price * 0.994
    else:
        signal, sl, tp = "⚪ HOLD / WAIT", price * 0.997, price * 1.006
    return f"{signal}\nPrice: {price:.2f}\nRSI: {rsi:.1f} | EMA9: {ema9:.2f} | EMA21: {ema21:.2f}\nSL: {sl:.2f} | TP: {tp:.2f}"

msg = "📊 TRADING SIGNALS (1H)\n\n"
for name, sym in PAIRS.items():
    try:
        s = get_signal(sym)
        msg += f"--- {name} ---\n{s}\n\n" if s else f"--- {name} ---\nNo data\n\n"
    except Exception as e:
        msg += f"--- {name} ---\nError: {e}\n\n"

requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    json={"chat_id": CHAT_ID, "text": msg})
print("Sent signals")
