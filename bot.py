import requests
import time

BOT_TOKEN = "8716379649:AAGPM6wjXyuu1zqvQyjWf9ZxqA2tbb-9_A8"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

print("Bot started...")
offset = 0
while True:
    try:
        r = requests.get(f"{API_URL}/getUpdates", json={"offset": offset, "timeout": 20}).json()
        for upd in r.get("result", []):
            offset = upd["update_id"] + 1
            if "message" in upd:
                chat_id = upd["message"]["chat"]["id"]
                requests.post(f"{API_URL}/sendMessage", json={"chat_id": chat_id, "text": "البوت يعمل بنجاح!"})
        time.sleep(1)
    except:
        time.sleep(2)
