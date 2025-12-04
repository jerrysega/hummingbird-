import requests

class TelegramBot:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_message(self, text):
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,

        }

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            print("❌ Telegram Error:", response.text)
        else:
            print("📩 Telegram alert sent.")
