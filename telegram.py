import requests
import time

BOT_TOKEN = "8254665550:AAHMbn_MJTp8hQY7LDOXWeetoptOAnZV7xA"
CHAT_ID = "6699568955"

last_sent_time = 0

def send_telegram(msg):
    global last_sent_time

    # 1) Ratelimit protection (1.1 sec)
    now = time.time()
    if now - last_sent_time < 1.1:
        time.sleep(1.1 - (now - last_sent_time))

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}

    r = requests.post(url, json=payload)

    # 2) If Telegram returns error
    if r.status_code != 200:
        try:
            data = r.json()
            if data.get("error_code") == 429:
                retry_after = data["parameters"]["retry_after"]
                print(f"⚠️ Telegram rate limit. Waiting {retry_after}s...")

                time.sleep(retry_after + 1)
                return send_telegram(msg)  # Retry only ONCE
        except:
            pass

        print("❌ Telegram send failed:", r.text)
        return False

    # 3) Success
    last_sent_time = time.time()
    return True
