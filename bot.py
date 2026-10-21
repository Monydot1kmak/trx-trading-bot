import requests
import json
import time
from datetime import datetime

# ================= الإعدادات =================
BOT_TOKEN = "8716379649:AAGPM6wjXyuu1zqvQyjWf9ZxqA2tbb-9_A8"
ADMIN_ID = 8883517436
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

BINANCE_ADDRESS = "0x0d55f41d0859febc41a55dc3ddeae77443837b8c"
TRX_ADDRESS = "TPTzMmk1ZD8g4z7H6CiqCpYWb9xPRbpgbj"

PLANS = {
    "p15": {"name": "🥉 برونزية", "price": 15, "daily": 5, "days": 15},
    "p30": {"name": "🥈 فضية", "price": 30, "daily": 8, "days": 15},
    "p50": {"name": "🥇 ذهبية", "price": 50, "daily": 10, "days": 30},
    "p100": {"name": "💎 بلاتينية", "price": 100, "daily": 18, "days": 30},
    "p200": {"name": "👑 ماسية", "price": 200, "daily": 30, "days": 30}
}

# ================= الأزرار =================
def main_keyboard():
    return {"keyboard": [["📊 الاشتراكات", "💼 محفظتي"], ["📞 الدعم"]], "resize_keyboard": True}

def plans_keyboard():
    buttons = [[f"{p['name']} - ${p['price']}"] for p in PLANS.values()]
    buttons.append(["🔙 رجوع"])
    return {"keyboard": buttons, "resize_keyboard": True}

def pay_keyboard(plan_key):
    return {
        "inline_keyboard": [
            [{"text": "🔗 Binance (BEP-20)", "callback_data": f"binance_{plan_key}"}],
            [{"text": "🟢 TRX (TRC-20)", "callback_data": f"trx_{plan_key}"}],
            [{"text": "🔙 رجوع", "callback_data": "back_plans"}]
        ]
    }

# ================= الدوال =================
def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup: payload["reply_markup"] = json.dumps(reply_markup)
    try: requests.post(f"{API_URL}/sendMessage", json=payload, timeout=5)
    except: pass

def edit_message(chat_id, msg_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup: payload["reply_markup"] = json.dumps(reply_markup)
    try: requests.post(f"{API_URL}/editMessageText", json=payload, timeout=5)
    except: pass

def answer_cb(cb_id):
    try: requests.post(f"{API_URL}/answerCallbackQuery", json={"callback_query_id": cb_id}, timeout=5)
    except: pass

# ================= التشغيل =================
print("🚀 البوت يعمل الآن...")
offset = 0
user_states = {}

while True:
    try:
        r = requests.get(f"{API_URL}/getUpdates", json={"offset": offset, "timeout": 20}, timeout=25).json()
        for upd in r.get("result", []):
            offset = upd["update_id"] + 1
            
            # معالجة الرسائل النصية
            if "message" in upd:
                chat_id = upd["message"]["chat"]["id"]
                uid = upd["message"]["from"]["id"]
                text = upd["message"].get("text", "")
                
                if uid in user_states:
                    del user_states[uid]
                    send_message(chat_id, "✅ تم استلام إثبات الدفع، سيتم التفعيل بعد المراجعة.", main_keyboard())
                    send_message(ADMIN_ID, f"🔔 *إيداع جديد*\n👤 `{uid}`\n🔖 {text}")
                    continue
                
                if text == "/start":
                    send_message(chat_id, "💎 *مرحباً بك في منصة TRX TRADING*\n\nاختر من الأزرار:", main_keyboard())
                elif text == "📊 الاشتراكات":
                    send_message(chat_id, "📦 *اختر خطة الاشتراك:*", plans_keyboard())
                elif text in [f"{p['name']} - ${p['price']}" for p in PLANS.values()]:
                    p_key = next(k for k, p in PLANS.items() if text == f"{p['name']} - ${p['price']}")
                    p = PLANS[p_key]
                    msg_text = f"*{p['name']}*\n💰 السعر: ${p['price']}\n📈 ربح يومي: ${p['daily']}\n📅 المدة: {p['days']} يوم\n\n💳 *اختر طريقة الدفع:*"
                    send_message(chat_id, msg_text, pay_keyboard(p_key))
                elif text == "🔙 رجوع":
                    send_message(chat_id, "🔙 القائمة الرئيسية", main_keyboard())
                elif text == "💼 محفظتي":
                    send_message(chat_id, "💼 *محفظتك*\n💰 الرصيد: $0.00", main_keyboard())
            
            # معالجة الأزرار المضمنة
            elif "callback_query" in upd:
                cb = upd["callback_query"]
                cb_id = cb["id"]
                chat_id = cb["message"]["chat"]["id"]
                msg_id = cb["message"]["message_id"]
                data = cb["data"]
                uid = cb["from"]["id"]
                
                if data == "back_plans":
                    edit_message(chat_id, msg_id, "📦 *اختر خطة الاشتراك:*", plans_keyboard())
                elif data.startswith("binance_") or data.startswith("trx_"):
                    method, plan = data.split("_")
                    addr = BINANCE_ADDRESS if method == "binance" else TRX_ADDRESS
                    net = "BEP-20" if method == "binance" else "TRC-20"
                    edit_message(chat_id, msg_id, f"🔗 *إيداع {method.capitalize()}*\n\n📌 أرسل ${PLANS[plan]['price']} إلى:\n`{addr}`\n\n🌐 الشبكة: {net}\n\n⚠️ بعد التحويل أرسل *TxID* هنا:")
                    user_states[uid] = plan
                answer_cb(cb_id)
                
        time.sleep(0.5)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)
