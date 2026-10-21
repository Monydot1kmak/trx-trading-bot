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

if name == "main":
    main()
