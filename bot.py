import requests
import json
import time

BOT_TOKEN = "8716379649:AAGPM6wjXyuu1zqvQyjWf9ZxqA2tbb-9_A8"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text, keyboard=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if keyboard:
        payload["reply_markup"] = json.dumps(keyboard)
    try:
        requests.post(f"{API_URL}/sendMessage", json=payload, timeout=5)
    except:
        pass

def get_keyboard():
    return {
        "keyboard": [["📊 الاشتراكات", "💼 محفظتي"], ["📈 اشتراكاتي"]],
        "resize_keyboard": True
    }

print("🚀 البوت يعمل الآن...")
offset = 0
while True:
    try:
        r = requests.get(f"{API_URL}/getUpdates", json={"offset": offset, "timeout": 20}, timeout=25).json()
        for upd in r.get("result", []):
            offset = upd["update_id"] + 1
            if "message" in upd:
                chat_id = upd["message"]["chat"]["id"]
                text = upd["message"].get("text", "")
                
                if text == "/start":
                    send_message(chat_id, "💎 *مرحباً بك في منصة التداول*\n\nاختر من الأزرار أدناه:", get_keyboard())
                elif text == "📊 الاشتراكات":
                    send_message(chat_id, "📦 *الاشتراكات متاحة قريباً*", get_keyboard())
                elif text == "💼 محفظتي":
                    send_message(chat_id, "💼 *محفظتك فارغة حالياً*", get_keyboard())
        time.sleep(0.5)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)
