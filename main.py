import sqlite3
import imaplib
import email
import re
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# ==================== الإعدادات الرئيسية ====================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8600844088:AAFMfgNnSypaN05fGvZaXM-H_8MtUftuQcM")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7983029778"))  

# ==================== إدارة قاعدة البيانات ====================
def init_db():
    try:
        conn = sqlite3.connect('netflix.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                email TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                imap_server TEXT DEFAULT 'imap.gmail.com'
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Init Error: {e}")

def add_account(email_addr, password):
    email_addr = email_addr.lower().strip()
    if "outlook" in email_addr or "hotmail" in email_addr or "live" in email_addr:
        imap_server = "imap-mail.outlook.com"
    else:
        imap_server = "imap.gmail.com"

    try:
        conn = sqlite3.connect('netflix.db')
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO accounts VALUES (?, ?, ?)', 
                       (email_addr, password, imap_server))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Add Account Error: {e}")
        return False

def get_account(email_addr):
    try:
        conn = sqlite3.connect('netflix.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password, imap_server FROM accounts WHERE email = ?', (email_addr.lower().strip(),))
        res = cursor.fetchone()
        conn.close()
        return res
    except Exception:
        return None

# ==================== جلب الكود من أحدث رسالة حصرياً حسب النوع ====================
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
        # التركيز حصرياً على أحدث رسالة واصلة
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
                            html_content = part.get_payload(decode=True).decode(errors='ignore')
                        elif ct == "text/plain":
                            text_content = part.get_payload(decode=True).decode(errors='ignore')
                else:
                    html_content = msg.get_payload(decode=True).decode(errors='ignore')

        mail.logout()

        # 1. طلب كود السكن (Temporary Access / Get Code)
        if code_type == "type_household":
            code_match = re.search(r'\b\d{4}\b', text_content)
            if code_match:
                return f"🔑 **كود السكن (من أحدث رسالة):**\n\n`{code_match.group(0)}`"
            
            urls = re.findall(r'href="(https://[^\"]*netflix[^\"]*)"', html_content)
            if urls:
                valid_url = urls[0]
                for u in urls:
                    if any(k in u for k in ["account", "travel", "pin", "get-code", "cl", "common"]):
                        valid_url = u
                        break
                
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                    page_res = requests.get(valid_url, headers=headers, timeout=10)
                    if page_res.status_code == 200:
                        page_code_match = re.search(r'\b\d{4}\b', page_res.text)
                        if page_code_match:
                            return f"🔑 **كود السكن المستخرج تلقائياً من أحدث رسالة:**\n\n`{page_code_match.group(0)}`"
                except Exception as e:
                    print(f"Auto fetch error: {e}")

                return (
                    "🔗 **رابط كود السكن (من أحدث رسالة):**\n\n"
                    f"[اضغط هنا للحصول على الكود مباشرة]({valid_url})\n\n"
                    "*(اضغط على الرابط لتظهر لك الـ 4 أرقام فوراً)*"
                )

        # 2. طلب كود تسجيل الدخول (Sign-in Code)
        elif code_type == "type_signin":
            code_match = re.search(r'\b\d{4,6}\b', text_content)
            if code_match:
                return f"🔐 **كود تسجيل الدخول (من أحدث رسالة):**\n\n`{code_match.group(0)}`"
            else:
                return "ℹ️ أحدث رسالة لا تحتوي على رقم كود تسجيل دخول واضح."

        return "ℹ️ لم يتم التعرف على نوع الطلب."

    except Exception as e:
        return f"❌ حدث خطأ أثناء الاتصال بالبريد الإلكتروني:\n`{str(e)}`"

# ==================== أوامر البوت ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "مرحباً بك! 🎬\n\n"
            "للحصول على الأكواد، قم بإرسال **الإيميل** مباشرة في الشات وسيعطيك البوت خيارات الأكواد.\n\n"
            "مثال:\n`example@outlook.com`",
            parse_mode="Markdown"
        )
    except Exception:
        pass

# أمر لإضافة عدة إيميلات نصياً دفعة واحدة (كل حساب في سطر)
async def add_email_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        text = update.message.text
        if text.startswith('/add'):
            text = text[len('/add'):].strip()

        if not text:
            await update.message.reply_text(
                """⚠️ يرجى إرسال الإيميلات وكلمات المرور بالطريقة التالية:

/add
email1@outlook.com password123
email2@gmail.com password456""", 
                parse_mode="Markdown"
            )
            return

        lines = text.split('\n')
        added_count = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            parts = re.split(r'[\s:]+', line)
            if len(parts) >= 2:
                email_addr = parts[0].lower().strip()
                password = parts[1].strip()
                
                if "@" in email_addr and "." in email_addr:
                    if add_account(email_addr, password):
                        added_count += 1

        await update.message.reply_text(
            f"✅ تمت العملية بنجاح!\nتم إضافة وتحديث `{added_count}` حساباً في قاعدة البيانات.", 
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء الإضافة: `{str(e)}`", parse_mode="Markdown")
