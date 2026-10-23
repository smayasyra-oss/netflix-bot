import sqlite3
import imaplib
import email
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ==================== الإعدادات الرئيسية ====================
BOT_TOKEN = "8600844088:AAFMfgNnSypaN05fGvZaXM-H_8MtUftuQcM"
ADMIN_ID = 7983029778  

# ==================== إدارة قاعدة البيانات ====================
def init_db():
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

def add_account(email_addr, password, imap="imap.gmail.com"):
    try:
        conn = sqlite3.connect('netflix.db')
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO accounts VALUES (?, ?, ?)', 
                       (email_addr.lower().strip(), password, imap))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def get_account(email_addr):
    conn = sqlite3.connect('netflix.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password, imap_server FROM accounts WHERE email = ?', (email_addr.lower().strip(),))
    res = cursor.fetchone()
    conn.close()
    return res

# ==================== جلب كود السكن من البريد ====================
def get_netflix_code(email_addr, password, imap_server):
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_addr, password)
        mail.select("inbox")

        # البحث عن الرسائل القادمة من نتفليكس
        status, messages = mail.search(None, '(FROM "netflix")')
        if status != "OK" or not messages[0]:
            mail.logout()
            return "⚠️ لم يتم العثور على أي رسائل من نتفليكس لهذا الإيميل."

        email_ids = messages[0].split()
        latest_id = email_ids[-1]  # أحدث رسالة واصلة

        status, msg_data = mail.fetch(latest_id, "(RFC822)")
        body = ""

        for response in msg_data:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode(errors='ignore')
                else:
                    body = msg.get_payload(decode=True).decode(errors='ignore')

        mail.logout()

        # استخراج كود التلفزيون/السكن (المكون من 4 أرقام)
        code_match = re.search(r'\b\d{4}\b', body)
        if code_match:
            return f"🔑 **كود سكن نتفليكس:**\n\n`{code_match.group(0)}`"
        else:
            return "ℹ️ وصلت رسالة من نتفليكس، لكن لم يتم العثور على كود سكن واضح بداخلها."

    except Exception as e:
        return f"❌ حدث خطأ أثناء الاتصال بالبريد الإلكتروني:\n`{str(e)}`"

# ==================== أوامر البوت ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً بك! 🎬\n\n"
        "للحصول على كود السكن الخاص بحساب نتفليكس، قم بإرسال الإيميل مباشرة في الشات.\n\n"
        "مثال:\n`example@gmail.com`",
        parse_mode="Markdown"
    )

# أمر لك كأدمن لإضافة أو تحديث إيميل مع كلمة مرور التطبيق (App Password)
async def add_email_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        e = context.args[0]
        p = context.args[1]
        if add_account(e, p):
            await update.message.reply_text(f"✅ تم إضافة/تحديث الإيميل بنجاح:\n`{e}`", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ حدث خطأ أثناء حفظ الإيميل في قاعدة البيانات.")
    except IndexError:
        await update.message.reply_text(
            "⚠️ طريقة الإضافة الخاطئة.\n"
            "يرجى إرسال الأمر كالتالي:\n"
            "`/add email@gmail.com app_password`", 
            parse_mode="Markdown"
        )

# معالجة طلبات التجار والمستخدمين
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    # استخراج الإيميل من النص المدخل
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)

    if email_match:
        target_email = email_match.group(0).lower()
        account_data = get_account(target_email)

        if account_data:
            await update.message.reply_text("⏳ جاري الدخول للبريد وجلب كود السكن...")
            password, imap = account_data
            result_message = get_netflix_code(target_email, password, imap)
            await update.message.reply_text(result_message, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ هذا الإيميل غير مسجل في النظام لدينا.")
    else:
        await update.message.reply_text("يرجى إرسال الإيميل بشكل صحيح.")

# ==================== نقطة الانطلاق ====================
if __name__ == '__main__':
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_email_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("البوت يعمل الآن بنجاح...")
    app.run_polling()
