import time
from data.odds_monitor import OddsMonitor
from data.telegram_bot import TelegramBot

# =============== FILL THIS ===============
API_KEY  = "5e2e8dc7af2c06f6b6504b0155577bb6"
BOT_TOKEN = "8254665550:AAHMbn_MJTp8hQY7LDOXWeetoptOAnZV7xA"
CHAT_ID   = "6699568955"
# =========================================

monitor = OddsMonitor(API_KEY)
bot = TelegramBot(BOT_TOKEN, CHAT_ID)

POLL_INTERVAL = 60 * 3  # check every 3 minutes

print("🚀 Hummingbird Auto-Monitoring Started...\n")

while True:
    print("🔄 Checking odds...")
    monitor.monitor_once(bot)
    print(f"⏳ Waiting {POLL_INTERVAL} seconds...\n")
    time.sleep(POLL_INTERVAL)

