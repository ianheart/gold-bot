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

def get_new_signal(symbol):
    df = yf.download(symbol, period="5d", interval="1h", progress=False)
    if df.empty or len(df) < 30:
        return None
    close = df['Close'].flatten()
    ema9 = close.ewm(span=9).mean()
    ema21 = close.ewm(span=21).mean()
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
    loss = -delta.where(delta < 0, 0).rolling(14).mean().iloc[-1]
    rsi = 100 - (100 / (1 + gain / loss)) if loss != 0 else 50
    price = float(close.iloc[-1])

    prev_bull = ema9.iloc[-2] < ema21.iloc[-2] and ema9.iloc[-1] > ema21.iloc[-1]
    prev_bear = ema9.iloc[-2] > ema21.iloc[-2] and ema9.iloc[-1] < ema21.iloc[-1]

    if prev_bull and rsi < 70:
        return f"🟢 NEW BUY\nEntry: {price:.2f}\nRSI: {rsi:.1f}\nSL: {price*0.997:.2f}\nTP1: {price*1.003:.2f}\nTP2: {price*1.006:.2f}\nTP3: {price*1.010:.2f}\nTP4: {price*1.015:.2f}"
    if prev_bear and rsi > 30:
        return f"🔴 NEW SELL\nEntry: {price:.2f}\nRSI: {rsi:.1f}\nSL: {price*1.003:.2f}\nTP1: {price*0.997:.2f}\nTP2: {price*0.994:.2f}\nTP3: {price*0.990:.2f}\nTP4: {price*0.985:.2f}"
    return None

new_signals = []
for name, sym in PAIRS.items():
    try:
        s = get_new_signal(sym)
        if s:
            new_signals.append(f"--- {name} ---\n{s}")
    except Exception as e:
        print(f"{name} error: {e}")

if new_signals:
    msg = "🚨 NEW SIGNAL (1H Crossover)\n\n" + "\n\n".join(new_signals)
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg})
    print("Sent new signals")
else:
    print("No new signal - staying quiet")
