import requests
import time
import json

# ================= الإعدادات الأساسية =================
BOT_TOKEN = "8716379649:AAGPM6wjXyuu1zqvQyjWf9ZxqA2tbb-9_A8"
ADMIN_ID = 8883517436
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# عناوين الدفع
BINANCE_ADDRESS = "0x0d55f41d0859febc41a55dc3ddeae77443837b8c"
TRX_ADDRESS = "TPTzMmk1ZD8g4z7H6CiqCpYWb9xPRbpgbj"

# ================= لوحات المفاتيح =================
def main_keyboard():
    return {
        "keyboard": [
            ["📊 الاشتراكات", "💼 محفظتي"],
            ["📈 اشتراكاتي", "💰 رصيدي"],
            ["📞 الدعم الفني"]
        ],
        "resize_keyboard": True
    }

def plans_keyboard():
    return {
        "keyboard": [
            ["🥉 برونزية ($15)", "🥈 فضية ($30)"],
            ["🥇 ذهبية ($50)", "💎 بلاتينية ($100)"],
            ["👑 ماسية ($200)"],
            ["🔙 رجوع"]
        ],
        "resize_keyboard": True
    }

def deposit_keyboard():
    return {
        "keyboard": [
            ["🔗 إيداع Binance", "🟢 إيداع TRX"],
            ["🔙 رجوع"]
        ],
        "resize_keyboard": True
    }

# ================= الدوال المساعدة =================
def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        requests.post(f"{API_URL}/sendMessage", json=payload, timeout=5)
    except Exception as e:
        print(f"خطأ في الإرسال: {e}")

# ================= التشغيل الرئيسي =================
def main():
    print("🚀 البوت يعمل الآن...")
    print(f"👤 المشرف: {ADMIN_ID}")
    
    offset = 0
    while True:
        try:
            # جلب الرسائل من تلغرام
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
                    
                    # ====== الأوامر والردود ======
                    if text == "/start":
                        send_message(chat_id, 
                            "💎 *مرحباً بك في منصة TRX TRADING*\n\n"
                            "اختر من الأزرار أدناه للبدء:", 
                            main_keyboard())
                            
                    elif text == "📊 الاشتراكات":
                        send_message(chat_id, 
                            "📦 *خطط الاشتراك المتاحة*\n\n"
                            "🥉 برونزية: $15 (عائد $5/يوم)\n"
                            "🥈 فضية: $30 (عائد $8/يوم)\n"
                            "🥇 ذهبية: $50 (عائد $10/يوم)\n"
                            "💎 بلاتينية: $100 (عائد $18/يوم)\n"
                            "👑 ماسية: $200 (عائد $30/يوم)\n\n"
                            "👇 اختر الخطة للاستثمار:", 
                            plans_keyboard())
                            
                    elif text in ["🥉 برونزية ($15)", "🥈 فضية ($30)", "🥇 ذهبية ($50)", "💎 بلاتينية ($100)", "👑 ماسية ($200)"]:
                        send_message(chat_id, 
                            f"✅ *تم اختيار الخطة*\n\n"
                            f"لإتمام الاشتراك، اختر طريقة الدفع:", 
                            deposit_keyboard())
                            
                    elif text == "🔗 إيداع Binance":
                        send_message(chat_id, 
                            f"🔗 *إيداع عبر Binance*\n\n"
                            f"📌 أرسل المبلغ إلى العنوان التالي:\n"
                            f"{BINANCE_ADDRESS}\n\n"
                            f"🌐 الشبكة: BEP-20 (BSC)\n\n"
                            f"⚠️ بعد التحويل، أرسل لنا صورة الإشعار أو هاش العملية.")
                            
                    elif text == "🟢 إيداع TRX":
                        send_message(chat_id, 
                            f"🟢 *إيداع عبر TRX*\n\n"
                            f"📌 أرسل المبلغ إلى العنوان التالي:\n"
                            f"{TRX_ADDRESS}\n\n"
                            f"🌐 الشبكة: TRC-20\n\n"
                            f"⚠️ بعد التحويل، أرسل لنا صورة الإشعار أو هاش العملية.")
                            
                    elif text == "💼 محفظتي" or text == "💰 رصيدي":
                        send_message(chat_id, 
                            "💰 *محفظتك*\n\n"
                            "الرصيد الحالي: $0.00\n"
                            "الأرباح: $0.00\n\n"
                            "💡 استثمر الآن لزيادة رصيدك!")
                            
                    elif text == "📈 اشتراكاتي":
                        send_message(chat_id, 
                            "📈 *اشتراكاتي*\n\n"
                            "لا توجد اشتراكات نشطة حالياً.")
                            
                    elif text == "📞 الدعم الفني":
                        send_message(chat_id, 
                            "📞 *الدعم الفني*\n\n"
                            "للتواصل: @BlackData5")
                            
                    elif text == "🔙 رجوع":
                        send_message(chat_id, "🔙 القائمة الرئيسية", main_keyboard())
                        
                    else:
                        send_message(chat_id, "👇 اختر من الأزرار", main_keyboard())
                        
            time.sleep(0.5)
            
        except Exception as e:
            print(f"خطأ: {e}")
            time.sleep(2)

if name == "main":
    main()
