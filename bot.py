import requests
import os
import time

TOKEN = os.environ.get("9287774486:AAGlkZmUhj3KndwaOaRakeLNpFn4EIi911E
")
CHAT_ID = os.environ.get("8803846659")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    print("Sent:", msg)

# Test message
send("✅ Gold Bot is now on Telegram! You will get alerts here.")

# Your gold logic goes here...
# When signal happens, just call send("BUY GOLD NOW...")
