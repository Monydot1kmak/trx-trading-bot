import requests
import time
import threading
from datetime import datetime, timedelta

# ================= الإعدادات الأساسية =================
BOT_TOKEN = "8716379649:AAGPM6wjXyuu1zqvQyjWf9ZxqA2tbb-9_A8"
ADMIN_ID = 8883517436
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

BINANCE_ADDRESS = "0x0d55f41d0859febc41a55dc3ddeae77443837b8c"
TRX_ADDRESS = "TPTzMmk1ZD8g4z7H6CiqCpYWb9xPRbpgbj"
STARS_RATE = 77 # 1 دولار = 77 نجمة

# ================= خطط الاشتراك =================
PLANS = {
    "p15": {"name": "🥉 برونزية", "price": 15, "daily": 5, "days": 15, "bonus": 0},
    "p30": {"name": "🥈 فضية", "price": 30, "daily": 8, "days": 15, "bonus": 5},
    "p50": {"name": "🥇 ذهبية", "price": 50, "daily": 10, "days": 30, "bonus": 10},
    "p100": {"name": "💎 بلاتينية", "price": 100, "daily": 18, "days": 30, "bonus": 20},
    "p200": {"name": "👑 ماسية", "price": 200, "daily": 30, "days": 30, "bonus": 50}
}

# ================= قاعدة البيانات المؤقتة (في الذاكرة) =================
# ملاحظة: عند إعادة تشغيل السيرفر يتم تصفير البيانات (لحين ربط قاعدة بيانات حقيقية)
users_db = {} # {user_id: {"balance": 0, "subs": []}}
user_states = {} # {user_id: "action"}

# ================= لوحات المفاتيح =================
def main_keyboard():
    return {"keyboard": [["📊 الاشتراكات", "💼 محفظتي"], ["📈 اشتراكاتي", "📞 الدعم"]], "resize_keyboard": True}

def plans_keyboard():
    buttons = []
    for key, p in PLANS.items():
        buttons.append([f"{p['name']} - ${p['price']}"])
    buttons.append(["🔙 رجوع"])
    return {"keyboard": buttons, "resize_keyboard": True}

def pay_keyboard(plan_key):
    p = PLANS[plan_key]
    stars = p["price"] * STARS_RATE
    return {
        "inline_keyboard": [
            [{"text": f"⭐ دفع {stars} نجمة (فوري)", "callback_data": f"stars_{plan_key}"}],
            [{"text": "🔗 Binance", "callback_data": f"binance_{plan_key}"}],
            [{"text": "🟢 TRX", "callback_data": f"trx_{plan_key}"}],
            [{"text": "🔙 رجوع", "callback_data": "back_plans"}]
        ]
    }

def admin_keyboard(dep_id):
    return {"inline_keyboard": [[{"text": "✅ قبول", "callback_data": f"app_{dep_id}"}, {"text": "❌ رفض", "callback_data": f"rej_{dep_id}"}]]}

# ================= دوال مساعدة =================
def send_message(chat_id, text, reply_markup=None, parse_mode="Markdown"):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_markup: payload["reply_markup"] = json.dumps(reply_markup) if isinstance(reply_markup, dict) else reply_markup
    try: requests.post(f"{API_URL}/sendMessage", json=payload, timeout=5)
    except: pass

def edit_message(chat_id, msg_id, text, reply_markup=None, parse_mode="Markdown"):
    payload = {"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": parse_mode}
    if reply_markup: payload["reply_markup"] = json.dumps(reply_markup) if isinstance(reply_markup, dict) else reply_markup
    try: requests.post(f"{API_URL}/editMessageText", json=payload, timeout=5)
    except: pass

def answer_cb(cb_id, text=""):
    try: requests.post(f"{API_URL}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": text}, timeout=5)
    except: pass

# ================= خدمة الأرباح اليومية =================
def daily_payout_worker():
    while True:
        now = datetime.now()
        for uid, data in list(users_db.items()):
            for sub in list(data.get("subs", [])):
                if sub["status"] == "active":
                    end_date = datetime.fromisoformat(sub["end_date"])
                    if now >= end_date:
                        sub["status"] = "finished"
                        send_message(uid, f"🎉 *انتهى اشتراكك* في خطة {PLANS[sub['plan']]['name']}\n💰 إجمالي أرباحك: ${sub['daily'] * sub['days']}")
                    elif (now - datetime.fromisoformat(sub["last_payout"])).total_seconds() >= 86400:
                        data["balance"] = data.get("balance", 0) + sub["daily"]
                        sub["last_payout"] = now.isoformat()
                        send_message(uid, f"💰 *ربح يومي جديد!*\n➕ +${sub['daily']} أضيفت لمحفظتك.")
        time.sleep(300) # فحص كل 5 دقائق

# ================= معالجة التحديثات =================
def handle_message(msg):
    chat_id = msg["chat"]["id"]
    uid = msg["from"]["id"]
    text = msg.get("text", "")
    name = msg["from"].get("first_name", "مستخدم")
    
    if uid not in users_db: users_db[uid] = {"balance": 0, "subs": []}

    # التحقق من حالة الانتظار (TxID)
    if uid in user_states and user_states[uid].startswith("await_"):
        plan = user_states[uid].split("_")[1]
        del user_states[uid]
        
        # إرسال إشعار للمشرف
        send_message(ADMIN_ID, f"🔔 *إيداع جديد (مراجعة)*\n👤 {name} | `{uid}`\n📦 {PLANS[plan]['name']} | ${PLANS[plan]['price']}\n🔖 {text}", admin_keyboard(f"{uid}|{plan}"))
        send_message(chat_id, "✅ تم استلام إثبات الدفع، سيتم التفعيل بعد المراجعة.", main_keyboard())
        return

    # الأزرار الرئيسية
    if text == "/start":
        send_message(chat_id, f"💎 *مرحباً {name} في منصة TRX TRADING*\n💰 رصيدك: ${users_db[uid]['balance']:.2f}\n\nاختر من الأزرار:", main_keyboard())
    elif text == "📊 الاشتراكات":
        send_message(chat_id, "📦 *اختر خطة الاشتراك:*", plans_keyboard())
    elif text in [f"{p['name']} - ${p['price']}" for p in PLANS.values()]:
        # استخراج الخطة المختارة
        p_key = next(k for k, p in PLANS.items() if text == f"{p['name']} - ${p['price']}")
        p = PLANS[p_key]
        msg_text = f"*{p['name']}*\n💰 السعر: ${p['price']}\n📈 ربح يومي: ${p['daily']}\n📅 المدة: {p['days']} يوم\n🎁 مكافأة: ${p['bonus']}\n\n💳 *اختر طريقة الدفع:*"
        send_message(chat_id, msg_text, pay_keyboard(p_key))
    elif text == "💼 محفظتي":
        subs = [s for s in users_db[uid]["subs"] if s["status"] == "active"]
        send_message(chat_id, f"💼 *محفظتي*\n💰 الرصيد: ${users_db[uid]['balance']:.2f}\n📈 اشتراكات نشطة: {len(subs)}")
    elif text == "🔙 رجوع":
        send_message(chat_id, "🔙 القائمة الرئيسية", main_keyboard())

def handle_callback(cb):
    cb_id = cb["id"]
    uid = cb["from"]["id"]
    chat_id = cb["message"]["chat"]["id"]
    msg_id = cb["message"]["message_id"]
    data = cb["data"]

    if data == "back_plans":
        edit_message(chat_id, msg_id, "📦 *اختر خطة الاشتراك:*", plans_keyboard())
        answer_cb(cb_id)
        return

    if data.startswith("binance_") or data.startswith("trx_"):
        method, plan = data.split("_")
        addr = BINANCE_ADDRESS if method == "binance" else TRX_ADDRESS
        net = "BEP-20" if method == "binance" else "TRC-20"
        edit_message(chat_id, msg_id, f"🔗 *إيداع {method.capitalize()}*\n\n📌 أرسل ${PLANS[plan]['price']} إلى:\n`{addr}`\n\n🌐 الشبكة: {net}\n⚠️ بعد التحويل أرسل *TxID* هنا:")
        user_states[uid] = f"await_{plan}"
        answer_cb(cb_id)
        return

    if data.startswith("stars_"):
        plan = data.split("_")[1]
        p = PLANS[plan]
        stars = p["price"] * STARS_RATE
        
        # إرسال فاتورة النجوم
        requests.post(f"{API_URL}/sendInvoice", json={
            "chat_id": chat_id, "title": f"{p['name']}", "description": f"اشتراك {p['name']} لمدة {p['days']} يوم",
            "payload": f"sub_{plan}", "currency": "XTR", "prices": [{"label": "سعر", "amount": stars}]
        })
        answer_cb(cb_id)
        return

    # معالجة موافقة/رفض المشرف
    if uid == ADMIN_ID and (data.startswith("app_") or data.startswith("rej_")):
        action, target = data.split("_")[0], data.split("_")[1]
        user_id, plan = target.split("|")
        user_id = int(user_id)
        
        if action == "app":
            p = PLANS[plan]
            end_date = (datetime.now() + timedelta(days=p["days"])).isoformat()
            users_db[user_id]["subs"].append({
                "plan": plan, "amount": p["price"], "daily": p["daily"], "days": p["days"],
                "start": datetime.now().isoformat(), "end_date": end_date, "last_payout": datetime.now().isoformat(), "status": "active"
            })
            users_db[user_id]["balance"] += p["bonus"]
            send_message(user_id, f"✅ *تم تفعيل اشتراكك*\n📦 {p['name']}\n🎁 أضيفت مكافأة ${p['bonus']} لرصيدك!", main_keyboard())
            edit_message(chat_id, msg_id, "✅ تم القبول والتفعيل")
        else:
            send_message(user_id, "❌ تم رفض الإيداع، يرجى مراجعة الدعم.")
            edit_message(chat_id, msg_id, "❌ تم الرفض")
        answer_cb(cb_id)
        return

    answer_cb(cb_id)

# ================= معالجة الدفع بالنجوم =================
def handle_payment(msg):
    uid = msg["from"]["id"]
    chat_id = msg["chat"]["id"]
    payload = msg["successful_payment"].get("invoice_payload", "")
    
    if payload.startswith("sub_"):
        plan = payload.split("_")[1]
        p = PLANS[plan]
        if uid not in users_db: users_db[uid] = {"balance": 0, "subs": []}
        
        end_date = (datetime.now() + timedelta(days=p["days"])).isoformat()
        users_db[uid]["subs"].append({
            "plan": plan, "amount": p["price"], "daily": p["daily"], "days": p["days"],
            "start": datetime.now().isoformat(), "end_date": end_date, "last_payout": datetime.now().isoformat(), "status": "active"
        })
        users_db[uid]["balance"] += p["bonus"]
        send_message(chat_id, f"✅ *تم الدفع بنجاح!*\n📦 {p['name']}\n🎁 مكافأة: ${p['bonus']}", main_keyboard())

# ================= التشغيل الرئيسي =================
def main():
    print("🚀 البوت يعمل الآن...")
    # تشغيل خدمة الأرباح في الخلفية
    threading.Thread(target=daily_payout_worker, daemon=True).start()
    
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
                    if "successful_payment" in msg:
                        handle_payment(msg)
                    else:
                        handle_message(msg)
                elif "pre_checkout_query" in upd:
                    requests.post(f"{API_URL}/answerPreCheckoutQuery", json={"pre_checkout_query_id": upd["pre_checkout_query"]["id"], "ok": True})
                elif "callback_query" in upd:
                    handle_callback(upd["callback_query"])
            time.sleep(0.5)
        except Exception as e:
            print(f"خطأ: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
