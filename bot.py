import requests
import time
from datetime import datetime, timedelta

# ================= الإعدادات =================
BOT_TOKEN = "8716379649:AAGPM6wjXyuu1zqvQyjWf9ZxqA2tbb-9_A8"
ADMIN_ID = 8883517436
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

BINANCE_ADDRESS = "0x0d55f41d0859febc41a55dc3ddeae77443837b8c"
TRX_ADDRESS = "TPTzMmk1ZD8g4z7H6CiqCpYWb9xPRbpgbj"

# ================= الدوال الأساسية =================
def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(f"{API_URL}/sendMessage", json=payload, timeout=5)
    except:
        pass

def main_keyboard():
    return {
        "keyboard": [
            ["📊 الاشتراكات", "💼 محفظتي"],
            ["📈 اشتراكاتي", "💰 رصيدي"]
        ],
        "resize_keyboard": True
    }

# ================= حلقة التشغيل =================
def main():
    print("🚀 البوت يعمل الآن...")
    offset = 0
    while True:
        try:
            r = requests.get(f"{API_URL}/getUpdates", json={"offset": offset, "timeout": 20}, timeout=25).json()
            if not r.get("ok"):
                time.sleep(2)
                continue
            
            for upd in r.get("result", []):
                offset = upd["update_id"] + 1
                if "message" in upd:
                    msg = upd["message"]
                    chat_id = msg["chat"]["id"]
                    user_id = msg["from"]["id"]
                    text = msg.get("text", "")
                    
                    if text == "/start":
                        send_message(chat_id, "💎 *مرحباً بك في منصة TRX TRADING*", main_keyboard())
                    elif text == "📊 الاشتراكات":
                        send_message(chat_id, "📦 *الاشتراكات متاحة قريباً*", main_keyboard())
                    else:
                        send_message(chat_id, "اختر من الأزرار 👇", main_keyboard())
            time.sleep(0.5)
        except Exception as e:
            print(f"خطأ: {e}")
            time.sleep(2)

if name == "main":
    main()
