from email import message_from_bytes
import imaplib
import os
import re
import sqlite3
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# ==================== الإعدادات الرئيسية ====================
INFOBIP_API_KEY = os.getenv(
    "INFOBIP_API_KEY", "مفتاح_الاب_ايكي_هنا"
)
INFOBIP_BASE_URL = os.getenv("INFOBIP_BASE_URL", "jrnrkv.api.infobip.com")
INFOBIP_SENDER = os.getenv(
    "INFOBIP_SENDER", ""
)  # رقم المرسل التجريبي من إنفوبيب إذا طُلب
ADMIN_PHONE = os.getenv("ADMIN_PHONE", "962XXXXXXXXX")  # رقم هاتفك بدون +


# ==================== إدارة قاعدة البيانات ====================
def init_db():
  try:
    conn = sqlite3.connect("netflix.db")
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                email TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                imap_server TEXT DEFAULT 'imap.gmail.com'
            )
        """)
    conn.commit()
    conn.close()
  except Exception as e:
    print(f"DB Init Error: {e}")


def add_account(email_addr, password):
  email_addr = email_addr.lower().strip()
  if (
      "outlook" in email_addr
      or "hotmail" in email_addr
      or "live" in email_addr
  ):
    imap_server = "imap-mail.outlook.com"
  else:
    imap_server = "imap.gmail.com"

  try:
    conn = sqlite3.connect("netflix.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO accounts VALUES (?, ?, ?)",
        (email_addr, password, imap_server),
    )
    conn.commit()
    conn.close()
    return True
  except Exception as e:
    print(f"Add Account Error: {e}")
    return False


def get_account(email_addr):
  try:
    conn = sqlite3.connect("netflix.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password, imap_server FROM accounts WHERE email = ?",
        (email_addr.lower().strip(),),
    )
    res = cursor.fetchone()
    conn.close()
    return res
  except Exception:
    return None


# ==================== إرسال رسالة عبر Infobip WhatsApp ====================
def send_whatsapp_message(to_phone, text):
  url = f"https://{INFOBIP_BASE_URL}/whatsapp/1/message/text"
  headers = {
      "Authorization": f"App {INFOBIP_API_KEY}",
      "Content-Type": "application/json",
      "Accept": "application/json",
  }

  payload = {"to": to_phone, "content": {"text": text}}
  if INFOBIP_SENDER:
    payload["from"] = INFOBIP_SENDER

  try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f"Infobip Response: {response.text}")
  except Exception as e:
    print(f"Infobip Send Error: {e}")


# ==================== جلب الكود من أحدث رسالة ====================
def get_netflix_code_by_type(email_addr, password, imap_server, code_type):
  try:
    mail = imaplib.IMAP4_SSL(imap_server, 993)
    mail.login(email_addr, password)
    mail.select("inbox")

    status, messages = mail.search(None, '(FROM "netflix")')
    if status != "OK" or not messages[0]:
      mail.logout()
      return "⚠️ لم يتم العثور على أي رسائل من نتفليكس لهذا الإيميل."

    email_ids = messages[0].split()
    latest_id = email_ids[-1]

    status, msg_data = mail.fetch(latest_id, "(RFC822)")
    html_content = ""
    text_content = ""

    for response in msg_data:
      if isinstance(response, tuple):
        msg = email.message_from_bytes(response[1])
        if msg.is_multipart():
          for part in msg.walk():
            ct = part.get_content_type()
            if ct == "text/html":
              html_content = part.get_payload(decode=True).decode(
                  errors="ignore"
              )
            elif ct == "text/plain":
              text_content = part.get_payload(decode=True).decode(
                  errors="ignore"
              )
        else:
          html_content = msg.get_payload(decode=True).decode(errors="ignore")

    mail.logout()

    if code_type == "household":
      code_match = re.search(r"\b\d{4}\b", text_content)
      if code_match:
        return f"🔑 كود السكن (من أحدث رسالة):\n{code_match.group(0)}"

      urls = re.findall(r'href="(https://[^\"]*netflix[^\"]*)"', html_content)
      if urls:
        valid_url = urls[0]
        for u in urls:
          if any(
              k in u for k in ["account", "travel", "pin", "get-code", "cl", "common"]
          ):
            valid_url = u
            break
        return f"🔗 رابط كود السكن (من أحدث رسالة):\n{valid_url}"

    elif code_type == "signin":
      code_match = re.search(r"\b\d{4,6}\b", text_content)
      if code_match:
        return f"🔐 كود تسجيل الدخول (من أحدث رسالة):\n{code_match.group(0)}"
      else:
        return "ℹ️ أحدث رسالة لا تحتوي على رقم كود واضح."

    return "ℹ️ لم يتم التعرف على الطلب."

  except Exception as e:
    return f"❌ خطأ في الاتصال بالبريد:\n{str(e)}"


# ==================== مسار الويب (Webhook) لاستقبال رسائل Infobip ====================
@app.route("/webhook", methods=["POST"])
def receive_message():
  data = request.get_json()
  print(f"Received Webhook: {data}")
  try:
    if "results" in data:
      for result in data["results"]:
        sender_phone = result.get("from")
        msg_body = result.get("text", "").strip()

        if not sender_phone or not msg_body:
          continue

        # التعامل مع أمر الإضافة /add
        if msg_body.startswith("/add"):
          if sender_phone != ADMIN_PHONE:
            send_whatsapp_message(
                sender_phone, "❌ هذا الأمر مخصص للأدمن فقط."
            )
            return jsonify({"status": "success"}), 200

          lines = msg_body.split("\n")[1:]
          added_count = 0
          for line in lines:
            parts = re.split(r"[\s:]+", line.strip())
            if len(parts) >= 2:
              if add_account(parts[0], parts[1]):
                added_count += 1
          send_whatsapp_message(
              sender_phone,
              f"✅ تمت الإضافة بنجاح!\nتم تحديث {added_count} حساباً.",
          )
          return jsonify({"status": "success"}), 200

        # التعامل مع إرسال الإيميل
        if "@" in msg_body and "." in msg_body:
          email_match = re.search(
              r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", msg_body
          )
          if email_match:
            target_email = email_match.group(0).lower()
            account_data = get_account(target_email)
            if account_data:
              if "signin" in msg_body.lower():
                res = get_netflix_code_by_type(
                    target_email, account_data[0], account_data[1], "signin"
                )
              else:
                res = get_netflix_code_by_type(
                    target_email, account_data[0], account_data[1], "household"
                )
              send_whatsapp_message(
                  sender_phone, f"📧 البريد: {target_email}\n\n{res}"
              )
            else:
              send_whatsapp_message(
                  sender_phone, "❌ هذا الإيميل غير مسجل في النظام."
              )
        else:
          send_whatsapp_message(
              sender_phone,
              "مرحباً! 🎬\nأرسل الإيميل مباشرة لسحب كود نتفليكس، أو أرسل"
              " الإيميل متبوعاً بـ signin لكود تسجيل الدخول.",
          )

  except Exception as e:
    print(f"Webhook Error: {e}")

  return jsonify({"status": "success"}), 200


@app.route("/", methods=["GET"])
def home():
  return "Infobip WhatsApp Bot Server is Running!", 200


if __name__ == "__main__":
  init_db()
  port = int(os.getenv("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
