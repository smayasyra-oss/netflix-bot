import logging
import threading
import time
import urllib.request
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import sqlite3

# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# إعداد خادم الويب لـ Render
web_app = Flask(__name__)

RENDER_URL = "https://netflix-bot-8p4c.onrender.com"

@web_app.route('/')
def home():
    return "962ElStore Bot is active and running 24/7!"

def run_web():
    web_app.run(host="0.0.0.0", port=8080)

def self_ping():
    while True:
        try:
            urllib.request.urlopen(RENDER_URL)
            print("Self-ping sent successfully to keep bot alive!")
        except Exception as e:
            print(f"Self-ping failed: {e}")
        time.sleep(240)

threading.Thread(target=run_web, daemon=True).start()
threading.Thread(target=self_ping, daemon=True).start()

TOKEN = "8600844088:AAGWB9gpw3ETz0R0hGQxOmmGVVW9bAGmFls"
ADMINS = [7983029778, 5884539860]
SUPPORT_USERNAME = "@e962ElStore"
CHANNEL_USERNAME = "@El962Store"

CLIQ_INFO = (
    "🔹 معلومات الدفع عبر كليك (CliQ):\n"
    "• الاسم المستعار: XM22\n"
    "• مزود الخدمة: البنك العربي الإسلامي الدولي\n"
    "• اسم المستلم: محمد بلال فايز بني احمد"
)

RECEIPT_INSTRUCTIONS = {
    "default": (
        "✅ تم استلام صورة الإيصال بنجاح!\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول قريباً:\n"
        "⚠️ تنبيه هام: يرجى الالتزام بعدم فتح الحساب على أكثر من جهاز لضمان استمرار ضمانك!"
    ),
    "netflix": (
        "✅ تم استلام صورة الإيصال بنجاح!\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول:\n"
        "• يرجى إدخال البريد الإلكتروني، ثم الرجوع للقائمة الرئيسية لطلب الكود الخاص بتسجيل الدخول.\n"
        "⚠️ تنبيه هام: التسجيل متاح في جهاز واحد فقط، وسيتم سحب الحساب فوراً إذا تم فتحه على جهازين بنفس الوقت!"
    ),
    "shahid": (
        "✅ تم استلام صورة الإيصال بنجاح!\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول:\n"
        "• يرجى إدخال البريد الإلكتروني وكلمة السر لتسجيل الدخول.\n"
        "⚠️ تنبيه هام: يمنع الدخول إلى الحساب أكثر من جهاز، وسوف يتم سحب الاشتراك إذا تم الفتح على جهازين وأكثر!"
    ),
    "osn": (
        "✅ تم استلام صورة الإيصال بنجاح!\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول:\n"
        "• يرجى إدخال البريد الإلكتروني، ثم الرجوع للقائمة الرئيسية لطلب الكود الخاص بتسجيل الدخول.\n"
        "⚠️ تنبيه هام: التسجيل متاح في جهاز واحد فقط، وسيتم سحب الحساب فوراً إذا تم فتحه على جهازين بنفس الوقت!"
    ),
    "disney": (
        "✅ تم استلام صورة الإيصال بنجاح!\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول:\n"
        "• يرجى استخدام رقم تلفون و كود لتسجيل الدخول.\n"
        "⚠️ تنبيه هام: مخصص لجهاز واحد فقط لضمان استقرار الضمان."
    ),
    "noor": (
        "✅ تم استلام صورة الإيصال بنجاح!\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول:\n"
        "• يرجى إدخال البريد الإلكتروني وكلمة السر لتسجيل الدخول:\n"
        "⚠️ تنبيه هام: يمنع الدخول إلى الحساب أكثر من جهاز، وسوف يتم سحب الاشتراك إذا تم الفتح على جهازين وأكثر!"
    ),
    "tod": (
        "✅ تم استلام صورة الإيصال بنجاح!\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول:\n"
        "• يرجى استخدام رقم تلفون و باسورد لتسجيل الدخول.\n"
        "⚠️ تنبيه هام: الحساب يعمل على جهازين FHD كحد أقصى."
    ),
    "chatgpt_shared": (
        "✅ تم استلام صورة الإيصال بنجاح!\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 سيتم تزويدك بمعلومات حساب ChatGPT المشترك فوراً."
    ),
    "chatgpt_private": (
        "✅ تم استلام صورة الإيصال بنجاح!\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 سيتم تزويدك بمعلومات حساب ChatGPT الخاص بك فوراً:\n"
        "⚠️ تنبيه هام: الحساب خاص بك وحدك ومحمي بالكامل طوال فترة الاشتراك."
    )
}

def get_main_menu():
    keyboard = [
        [KeyboardButton("🛒 الاشتراكات الفردية"), KeyboardButton("🔥 عروض التوفير الكبرى")],
        [KeyboardButton("🔑 طلب كود"), KeyboardButton("⚠️ مشكلة في حسابي")],
        [KeyboardButton("🛠 التواصل مع الدعم")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def check_user_channel_membership(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception as e:
        print(f"Error checking channel membership: {e}")
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_member = await check_user_channel_membership(context.bot, user.id)
    
    if not is_member:
        join_keyboard = [
            [InlineKeyboardButton("📢 اشترك في القناة الآن", url="https://t.me/El962Store")],
            [InlineKeyboardButton("✅ لقد اشتريت / اشتركت، تحقق الآن", callback_data="verify_subscription")]
        ]
        await update.message.reply_text(
            f"أهلاً بك يا {user.full_name} في متجر 962ElStore 🎬🤖\n\n"
            "⚠️ **عذراً، يرجى الاشتراك في قناة المتجر أولاً لتتمكن من استخدام البوت ومتابعة العروض الحصرية:**\n"
            "👉 https://t.me/El962Store\n\n"
            "بعد الانضمام، اضغط على زر **(تحقق الآن)** بالأسفل 👇",
            reply_markup=InlineKeyboardMarkup(join_keyboard),
            disable_web_page_preview=True
        )
        return

    welcome_text = (
        "أهلاً بك في متجر 962ElStore للتسوق الرقمي!\n\n"
        "كل اللي تحبه من عالم الترفيه والذكاء الاصطناعي بأسرار مميزة وأسعار منافسة 🎬🤖\n\n"
        f"رقمك التعريفي: {user.id}\n"
        f"الاسم: {user.full_name}\n\n"
        "اختر من القائمة أدناه للبدء:"
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_menu())

async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("❌ الاستخدام الصحيح:\n/reply [user_id] [الرسالة]")
        return

    target_user_id = args[0]
    reply_message = " ".join(args[1:])

    try:
        await context.bot.send_message(
            chat_id=target_user_id,
            text=f"📬 رد جديد من الإدارة (962ElStore):\n\n{reply_message}"
        )
        await update.message.reply_text("✅ تم إرسال الرد إلى الزبون بنجاح!")
    except Exception as e:
        await update.message.reply_text(f"❌ فشل إرسال الرسالة للزبون:\n{e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    is_member = await check_user_channel_membership(context.bot, user.id)
    if not is_member:
        join_keyboard = [
            [InlineKeyboardButton("📢 اشترك في القناة الآن", url="https://t.me/El962Store")],
            [InlineKeyboardButton("✅ لقد اشتريت / اشتركت، تحقق الآن", callback_data="verify_subscription")]
        ]
        await update.message.reply_text(
            "⚠️ تنبيه: يرجى الاشتراك في قناة المتجر أولاً للاستمرار:\n👉 https://t.me/El962Store\n\nثم اضغط على زر التحقق 👇",
            reply_markup=InlineKeyboardMarkup(join_keyboard),
            disable_web_page_preview=True
        )
        return

    text = update.message.text
    
    if context.user_data.get('waiting_for_issue_email'):
        context.user_data['issue_email'] = text
        context.user_data['waiting_for_issue_email'] = False
        context.user_data['waiting_for_issue_description'] = True
        
        await update.message.reply_text(
            "📝 تم استلام البريد الإلكتروني بنجاح.\n\n"
            "الآن، يرجى **وصف المشكلة بالتفصيل** (ويمكنك إرسال صورة للمشكلة إن وجدت):"
        )
        return

    if context.user_data.get('waiting_for_issue_description'):
        platform_name = context.user_data.get('issue_platform', 'منصة رقمية')
        issue_email = context.user_data.get('issue_email', 'غير محدد')
        issue_desc = text
        
        await update.message.reply_text(
            "✅ **تم إرسال بلاغ المشكلة بنجاح!**\n"
            "فريق الدعم في متجر 962ElStore سيقوم بمراجعة المشكلة والرد عليك قريباً جداً ⏳"
        )

        admin_msg = (
            "⚠️ **تنبيه: بلاغ مشكلة جديدة في حساب زبون!**\n\n"
            f"👤 اسم الزبون: {user.full_name}\n"
            f"🔗 يوزر الزبون: @{user.username if user.username else 'لا يوجد'}\n"
            f"🆔 معرف الزبون: {user.id}\n\n"
            f"📦 المنصة: {platform_name}\n"
            f"📧 البريد الإلكتروني للحساب:\n`{issue_email}`\n\n"
            f"📝 وصف المشكلة:\n{issue_desc}\n\n"
            f"🟢 حالة الطلب: لم يتم الاستلام بعد\n\n"
            f"👇 انسخ هذا الأمر للرد:\n"
            f"```\n/reply {user.id} ضع_الرد_هنا\n```"
        )
        
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🙋‍♂️ استلام (محمد)", callback_data=f"claim_m_{user.id}"),
             InlineKeyboardButton("🙋‍♂️ استلام (حسام)", callback_data=f"claim_h_{user.id}")]
        ])
        
        for admin_id in ADMINS:
            try:
                await context.bot.send_message(chat_id=admin_id, text=admin_msg, reply_markup=markup, parse_mode="Markdown")
            except Exception as e:
                print(f"Error: {e}")

        context.user_data['waiting_for_issue_description'] = False
        return

    if context.user_data.get('waiting_for_netflix_household_email'):
        netflix_email = text
        
        await update.message.reply_text(
            "✅ تم استلام بريد نتفليكس بنجاح!\n"
            "جارٍ إرسال طلب كود السكن للأدمن، سيتم تزويدك بالكود قريباً ⏳"
        )

        admin_msg = (
            "🏠 طلب كود سكن نتفليكس (Household Code)!\n\n"
            f"اسم الزبون: {user.full_name}\n"
            f"يوزر الزبون: @{user.username if user.username else 'لا يوجد'}\n"
            f"🆔 معرف الزبون: {user.id}\n\n"
            f"إيميل نتفليكس المطلوب له الكود:\n{netflix_email}\n\n"
            f"🟢 حالة الطلب: لم يتم الاستلام بعد\n\n"
            f"👇 انسخ هذا الأمر للرد:\n"
            f"```\n/reply {user.id} ضع_الكود_هنا\n```"
        )
        
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🙋‍♂️ استلام (محمد)", callback_data=f"claim_m_{user.id}"),
             InlineKeyboardButton("🙋‍♂️ استلام (حسام)", callback_data=f"claim_h_{user.id}")]
        ])
        
        for admin_id in ADMINS:
            try:
                await context.bot.send_message(chat_id=admin_id, text=admin_msg, reply_markup=markup, parse_mode="Markdown")
            except Exception as e:
                print(f"Error: {e}")

        context.user_data['waiting_for_netflix_household_email'] = False
        return

    if context.user_data.get('waiting_for_login_code_email'):
        platform_name = context.user_data.get('login_code_platform', 'منصة رقمية')
        account_info = text
        
        await update.message.reply_text(
            f"✅ تم استلام تفاصيل حساب ({platform_name}) بنجاح!\n"
            "جارٍ إرسال طلب كود تسجيل الدخول للأدمن، سيتم تزويدك بالكود قريباً ⏳"
        )

        admin_msg = (
            "🔑 طلب كود تسجيل دخول جديد!\n\n"
            f"اسم الزبون: {user.full_name}\n"
            f"يوزر الزبون: @{user.username if user.username else 'لا يوجد'}\n"
            f"🆔 معرف الزبون: {user.id}\n\n"
            f"المنصة: {platform_name}\n"
            f"معلومات الحساب / الإيميل:\n{account_info}\n\n"
            f"🟢 حالة الطلب: لم يتم الاستلام بعد\n\n"
            f"👇 انسخ هذا الأمر للرد:\n"
            f"```\n/reply {user.id} ضع_الكود_هنا\n```"
        )
        
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🙋‍♂️ استلام (محمد)", callback_data=f"claim_m_{user.id}"),
             InlineKeyboardButton("🙋‍♂️ استلام (حسام)", callback_data=f"claim_h_{user.id}")]
        ])
        
        for admin_id in ADMINS:
            try:
                await context.bot.send_message(chat_id=admin_id, text=admin_msg, reply_markup=markup, parse_mode="Markdown")
            except Exception as e:
                print(f"Error: {e}")

        context.user_data['waiting_for_login_code_email'] = False
        return

    if text == "🛒 الاشتراكات الفردية":
        subs_keyboard = [
            [InlineKeyboardButton("🎬 Netflix - نتفليكس", callback_data="sub_netflix")],
            [InlineKeyboardButton("📺 Shahid VIP - شاهد", callback_data="sub_shahid")],
            [InlineKeyboardButton("🎥 OSN+ - أوس إن", callback_data="sub_osn")],
            [InlineKeyboardButton("✨ Disney+ - ديزني", callback_data="sub_disney")],
            [InlineKeyboardButton("🌙 Noor Play - نور بلاي", callback_data="sub_noor")],
            [InlineKeyboardButton("⚽ TOD - تود (رياضة وترفيه)", callback_data="sub_tod")],
            [InlineKeyboardButton("🤖 ChatGPT Plus - شات جي بي تي", callback_data="sub_chatgpt_menu")]
        ]
        await update.message.reply_text(
            "📦 قسم الاشتراكات الفردية (الاشتراك الواحد):\nاختر المنصة التي تناسبك:",
            reply_markup=InlineKeyboardMarkup(subs_keyboard)
        )
        
    elif text == "🔥 عروض التوفير الكبرى":
        bundles_keyboard = [
            [InlineKeyboardButton("👥 عرض منصتين معاً (5 JD)", callback_data="bundle_init_2")],
            [InlineKeyboardButton("⭐ عرض الـ 3 منصات (6 JD)", callback_data="bundle_init_3")],
            [InlineKeyboardButton("💎 عرض الـ 4 منصات معاً (8 JD)", callback_data="bundle_init_4")]
        ]
        await update.message.reply_text(
            "🔥 عروض التوفير الكبرى - 962ElStore\n\n"
            "اجمع منصاتك المفضلة (بما فيها ChatGPT Plus) في باقة واحدة ووفر أكثر.. اختر نوع العرض:",
            reply_markup=InlineKeyboardMarkup(bundles_keyboard)
        )
        
    elif text == "🔑 طلب كود":
        code_keyboard = [
            [InlineKeyboardButton("🔑 كود تسجيل دخول", callback_data="code_login_menu")],
            [InlineKeyboardButton("🏠 كود سكن (Netflix Household)", callback_data="code_household")]
        ]
        await update.message.reply_text(
            "🔑 قسم طلب الأكواد:\n\nيرجى اختيار نوع الكود الذي تحتاجه:",
            reply_markup=InlineKeyboardMarkup(code_keyboard)
        )

    elif text == "⚠️ مشكلة في حسابي":
        issue_keyboard = [
            [InlineKeyboardButton("🎬 Netflix - نتفليكس", callback_data="issue_netflix")],
            [InlineKeyboardButton("📺 Shahid VIP - شاهد", callback_data="issue_shahid")],
            [InlineKeyboardButton("🎥 OSN+ - أوس إن", callback_data="issue_osn")],
            [InlineKeyboardButton("✨ Disney+ - ديزني", callback_data="issue_disney")],
            [InlineKeyboardButton("🌙 Noor Play - نور بلاي", callback_data="issue_noor")],
            [InlineKeyboardButton("⚽ TOD - تود (رياضة وترفيه)", callback_data="issue_tod")],
            [InlineKeyboardButton("🤖 ChatGPT Plus - شات جي بي تي", callback_data="issue_chatgpt")]
        ]
        await update.message.reply_text(
            "⚠️ **قسم الإبلاغ عن مشكلة في الحساب:**\n\nاختر المنصة التي تواجه مشكلة فيها:",
            reply_markup=InlineKeyboardMarkup(issue_keyboard),
            parse_mode="Markdown"
        )
        
    elif text == "🛠 التواصل مع الدعم":
        support_text = (
            "🛠 الدعم الفني وخدمة العملاء - 962ElStore\n\n"
            "إذا واجهتك أي مشكلة أو استفسار، يسعدنا تواصلك معنا مباشرة عبر حساب الدعم:\n"
            f"💬 {SUPPORT_USERNAME}\n\n"
            "نحن في خدمتكم على مدار الساعة!"
        )
        await update.message.reply_text(support_text)

def get_bundle_selection_keyboard(selected_list, target_count):
    platforms = [
        ("netflix", "🎬 Netflix - نتفليكس"),
        ("shahid", "📺 Shahid VIP - شاهد"),
        ("osn", "🎥 OSN+ - أوس إن"),
        ("disney", "✨ Disney+ - ديزني"),
        ("noor", "🌙 Noor Play - نور بلاي"),
        ("chatgpt", "🤖 ChatGPT Plus - شات جي بي تي")
    ]
    
    keyboard = []
    for key, name in platforms:
        if key in selected_list:
            btn_text = f"✅ {name}"
            cb_data = f"unsel_{key}"
        else:
            btn_text = name
            cb_data = f"sel_{key}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=cb_data)])
    
    if len(selected_list) == target_count:
        keyboard.append([InlineKeyboardButton("➡️ متابعة لاختيار المدة", callback_data="proceed_to_duration")])
    
    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="back_to_bundles")])
    return InlineKeyboardMarkup(keyboard)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data

    if data.startswith("claim_"):
        parts = data.split("_")
        claimer = "محمد 🟢" if parts[1] == "m" else "حسام 🟢"
        
        try:
            if query.message.caption:
                old_text = query.message.caption
                new_text = old_text.replace("🟢 حالة الطلب: لم يتم الاستلام بعد", f"🔥 قيد المعالجة حالياً بواسطة: {claimer}")
                await query.message.edit_caption(caption=new_text, parse_mode="Markdown", reply_markup=None)
            else:
                old_text = query.message.text
                new_text = old_text.replace("🟢 حالة الطلب: لم يتم الاستلام بعد", f"🔥 قيد المعالجة حالياً بواسطة: {claimer}")
                await query.message.edit_text(text=new_text, parse_mode="Markdown", reply_markup=None)
                
            await query.answer(f"✅ تم استلام الطلب بنجاح يا {claimer.split()[0]}!")
        except Exception as e:
            print(f"Error claiming order: {e}")
            await query.answer(f"✅ تم تسجيل استلام الطلب بواسطة {claimer.split()[0]}!", show_alert=True)
        return

    if data == "verify_subscription":
        is_member = await check_user_channel_membership(context.bot, user.id)
        if is_member:
            await query.answer("✅ شكراً لاشتراكك في القناة!", show_alert=True)
            welcome_text = (
                "أهلاً بك في متجر 962ElStore للتسوق الرقمي!\n\n"
                "كل اللي تحبه من عالم الترفيه والذكاء الاصطناعي بأسرار مميزة وأسعار منافسة 🎬🤖\n\n"
                f"رقمك التعريفي: {user.id}\n"
                f"الاسم: {user.full_name}\n\n"
                "اختر من القائمة أدناه للبدء:"
            )
            await query.message.edit_text(welcome_text)
            await query.message.reply_text("القائمة الرئيسية:", reply_markup=get_main_menu())
        else:
            await query.answer("❌ عذراً، لم تقم بالاشتراك في القناة بعد! يرجى الاشتراك أولاً.", show_alert=True)
        return

    await query.answer()

    if data.startswith("issue_"):
        p_code = data.replace("issue_", "")
        p_map = {
            "netflix": "Netflix - نتفليكس",
            "shahid": "Shahid VIP - شاهد",
            "osn": "OSN+ - أوس إن",
            "disney": "Disney+ - ديزني",
            "noor": "Noor Play - نور بلاي",
            "tod": "TOD - تود",
            "chatgpt": "ChatGPT Plus - شات جي بي تي"
        }
        platform_name = p_map.get(p_code, "المنصة")
        context.user_data['issue_platform'] = platform_name
        context.user_data['waiting_for_issue_email'] = True

        await query.message.edit_text(
            f"⚠️ **الإبلاغ عن مشكلة في حساب ({platform_name}):**\n\n"
            "الرجاء إرسال **البريد الإلكتروني (الإيميل)** الخاص بالحساب الذي تواجه مشكلة فيه هنا في المحادثة الآن ✍️",
            parse_mode="Markdown"
        )
        return

    if data == "back_to_main":
        subs_keyboard = [
            [InlineKeyboardButton("🎬 Netflix - نتفليكس", callback_data="sub_netflix")],
            [InlineKeyboardButton("📺 Shahid VIP - شاهد", callback_data="sub_shahid")],
            [InlineKeyboardButton("🎥 OSN+ - أوس إن", callback_data="sub_osn")],
            [InlineKeyboardButton("✨ Disney+ - ديزني", callback_data="sub_disney")],
            [InlineKeyboardButton("🌙 Noor Play - نور بلاي", callback_data="sub_noor")],
            [InlineKeyboardButton("⚽ TOD - تود (رياضة وترفيه)", callback_data="sub_tod")],
            [InlineKeyboardButton("🤖 ChatGPT Plus - شات جي بي تي", callback_data="sub_chatgpt_menu")]
        ]
        await query.message.edit_text(
            "📦 قسم الاشتراكات الفردية (الاشتراك الواحد):\nاختر المنصة التي تناسبك:",
            reply_markup=InlineKeyboardMarkup(subs_keyboard)
        )

    elif data == "back_to_bundles":
        bundles_keyboard = [
            [InlineKeyboardButton("👥 عرض منصتين معاً (5 JD)", callback_data="bundle_init_2")],
            [InlineKeyboardButton("⭐ عرض الـ 3 منصات (6 JD)", callback_data="bundle_init_3")],
            [InlineKeyboardButton("💎 عرض الـ 4 منصات معاً (8 JD)", callback_data="bundle_init_4")]
        ]
        await query.message.edit_text(
            "🔥 عروض التوفير الكبرى - 962ElStore\n\n"
            "اجمع منصاتك المفضلة (بما فيها ChatGPT Plus) في باقة واحدة ووفر أكثر.. اختر نوع العرض:",
            reply_markup=InlineKeyboardMarkup(bundles_keyboard)
        )

    elif data == "code_login_menu":
        kb = [
            [InlineKeyboardButton("🎬 Netflix - نتفليكس", callback_data="login_code_netflix")],
            [InlineKeyboardButton("🎥 OSN+ - أوس إن", callback_data="login_code_osn")],
            [InlineKeyboardButton("✨ Disney+ - ديزني", callback_data="login_code_disney")],
            [InlineKeyboardButton("🤖 ChatGPT Plus - شات جي بي تي", callback_data="login_code_chatgpt")],
            [InlineKeyboardButton("⬅️ رجوع", callback_data="code_back_main")]
        ]
        await query.message.edit_text(
            "🔑 اختر المنصة التي تحتاج كود تسجيل دخول لها:",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif data == "code_back_main":
        code_keyboard = [
            [InlineKeyboardButton("🔑 كود تسجيل دخول", callback_data="code_login_menu")],
            [InlineKeyboardButton("🏠 كود سكن (Netflix Household)", callback_data="code_household")]
        ]
        await query.message.edit_text(
            "🔑 قسم طلب الأكواد:\n\nيرجى اختيار نوع الكود الذي تحتاجه:",
            reply_markup=InlineKeyboardMarkup(code_keyboard)
        )

    elif data.startswith("login_code_"):
        p_code = data.replace("login_code_", "")
        p_map = {
            "netflix": "Netflix - نتفليكس",
            "osn": "OSN+ - أوس إن",
            "disney": "Disney+ - ديزني",
            "chatgpt": "ChatGPT Plus - شات جي بي تي"
        }
        platform_name = p_map.get(p_code, "المنصة")
        context.user_data['login_code_platform'] = platform_name
        context.user_data['waiting_for_login_code_email'] = True

        await query.message.edit_text(
            f"🔑 طلب كود تسجيل دخول ({platform_name}):\n\n"
            "الرجاء إرسال البريد الإلكتروني (الإيميل) أو معلومات الحساب هنا في المحادثة الآن ✍️"
        )

    elif data == "code_household":
        await query.message.edit_text(
            "🏠 قسم كود السكن (Household Code):\n\nاختر المنصة المطلوبة:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎬 Netflix - نتفليكس", callback_data="hh_netflix")],
                [InlineKeyboardButton("⬅️ رجوع", callback_data="code_back_main")]
            ])
        )

    elif data == "hh_netflix":
        context.user_data['waiting_for_netflix_household_email'] = True
        await query.message.edit_text(
            "🎬 طلب كود سكن نتفليكس:\n\n"
            "الرجاء إرسال البريد الإلكتروني (الإيميل) الخاص بحساب نتفليكس هنا في المحادثة الآن ✍️"
        )

    elif data == "sub_chatgpt_menu":
        kb = [
            [InlineKeyboardButton("👥 حساب ChatGPT مشترك", callback_data="sub_chatgpt_shared_menu")],
            [InlineKeyboardButton("⭐ حساب ChatGPT خاص (مستقل)", callback_data="pkg_chatgpt_private_1m")],
            [InlineKeyboardButton("⬅️ رجوع", callback_data="back_to_main")]
        ]
        await query.message.edit_text(
            "🤖 اختر نوع اشتراك ChatGPT Plus الذي تفضله:",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif data == "sub_chatgpt_shared_menu":
        kb = [
            [InlineKeyboardButton("🟢 شهر واحد (2.5 JD)", callback_data="pkg_chatgpt_shared_1m")],
            [InlineKeyboardButton("🟢 3 أشهر (5 JD)", callback_data="pkg_chatgpt_shared_3m")],
            [InlineKeyboardButton("🟢 6 أشهر (9 JD)", callback_data="pkg_chatgpt_shared_6m")],
            [InlineKeyboardButton("🟢 سنة كاملة (15 JD)", callback_data="pkg_chatgpt_shared_1y")],
            [InlineKeyboardButton("⬅️ رجوع", callback_data="sub_chatgpt_menu")]
        ]
        await query.message.edit_text(
            "🤖 اشتراك ChatGPT Plus (حساب مشترك):\nاختر المدة المطلوبة:",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif data.startswith("sub_"):
        sub_type = data.replace("sub_", "")
        details_map = {
            "netflix": ("🎬 اشتراك Netflix - جودة 4K (بروفايل خاص - جهاز واحد)", "pkg_netflix"),
            "shahid": ("📺 اشتراك Shahid VIP - شاهد (جهاز واحد)", "pkg_shahid"),
            "osn": ("🎥 اشتراك OSN+ - أوس إن (جهاز واحد)", "pkg_osn"),
            "disney": ("✨ اشتراك Disney+ - ديزني (جهاز واحد)", "pkg_disney"),
            "noor": ("🌙 اشتراك Noor Play - نور بلاي (جهاز واحد)", "pkg_noor"),
            "tod": ("⚽ اشتراك TOD - تود (رياضة وترفيه - جهازين FHD)", "pkg_tod")
        }
        title, prefix = details_map[sub_type]
        
        if sub_type == "tod":
            kb = [
                [InlineKeyboardButton("🟢 شهر واحد (6 JD)", callback_data=f"{prefix}_1m")],
                [InlineKeyboardButton("🟢 3 أشهر (9 JD)", callback_data=f"{prefix}_3m")],
                [InlineKeyboardButton("⬅️ رجوع", callback_data="back_to_main")]
            ]
        else:
            kb = [
                [InlineKeyboardButton("🟢 شهر واحد (2.5 JD)", callback_data=f"{prefix}_1m")],
                [InlineKeyboardButton("🟢 3 أشهر (5 JD)", callback_data=f"{prefix}_3m")],
                [InlineKeyboardButton("🟢 6 أشهر (9 JD)", callback_data=f"{prefix}_6m")],
                [InlineKeyboardButton("🟢 سنة كاملة (15 JD)", callback_data=f"{prefix}_1y")],
                [InlineKeyboardButton("⬅️ رجوع", callback_data="back_to_main")]
            ]
        await query.message.edit_text(f"{title}\n\nاختر المدة المطلوبة:", reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("bundle_init_"):
        count = int(data.replace("bundle_init_", ""))
        context.user_data['bundle_target_count'] = count
        context.user_data['selected_platforms'] = []
        context.user_data['bundle_type'] = f"b{count}"

        text = (
            f"🎯 اختر {count} منصات تفضلها من القائمة أدناه (تشمل ChatGPT Plus):\n"
            "(كلما تضغط على منصة سيتم تفعيلها بـ ✅، وعند إتمام اختيارك سيظهر زر المتابعة)"
        )
        kb = get_bundle_selection_keyboard([], count)
        await query.message.edit_text(text, reply_markup=kb)

    elif data.startswith("sel_"):
        p_key = data.replace("sel_", "")
        selected = context.user_data.get('selected_platforms', [])
        target = context.user_data.get('bundle_target_count', 2)

        if len(selected) < target and p_key not in selected:
            selected.append(p_key)
            context.user_data['selected_platforms'] = selected

        text = (
            f"🎯 اختر {target} منصات تفضلها من القائمة أدناه:\n"
            f"تم اختيار ({len(selected)} من {target})"
        )
        kb = get_bundle_selection_keyboard(selected, target)
        await query.message.edit_text(text, reply_markup=kb)

    elif data.startswith("unsel_"):
        p_key = data.replace("unsel_", "")
        selected = context.user_data.get('selected_platforms', [])
        target = context.user_data.get('bundle_target_count', 2)

        if p_key in selected:
            selected.remove(p_key)
            context.user_data['selected_platforms'] = selected

        text = (
            f"🎯 اختر {target} منصات تفضلها من القائمة أدناه:\n"
            f"تم اختيار ({len(selected)} من {target})"
        )
        kb = get_bundle_selection_keyboard(selected, target)
        await query.message.edit_text(text, reply_markup=kb)

    elif data == "proceed_to_duration":
        b_type = context.user_data.get('bundle_type', 'b2')
        
        if b_type == "b2":
            text = "👥 عرض منصتين معاً (5 JD للشهر)\nاختر المدة المطلوبة:"
            kb = [
                [InlineKeyboardButton("🟢 شهر واحد (5 JD)", callback_data="pkg_b2_1m")],
                [InlineKeyboardButton("🟢 3 أشهر (12 JD)", callback_data="pkg_b2_3m")],
                [InlineKeyboardButton("🟢 6 أشهر (22 JD)", callback_data="pkg_b2_6m")],
                [InlineKeyboardButton("🟢 سنة كاملة (38 JD)", callback_data="pkg_b2_1y")],
                [InlineKeyboardButton("⬅️ رجوع لتعديل المنصات", callback_data="bundle_init_2")]
            ]
        elif b_type == "b3":
            text = "⭐ عرض الـ 3 منصات (6 JD للشهر)\nاختر المدة المطلوبة:"
            kb = [
                [InlineKeyboardButton("🟢 شهر واحد (6 JD)", callback_data="pkg_b3_1m")],
                [InlineKeyboardButton("🟢 3 أشهر (15 JD)", callback_data="pkg_b3_3m")],
                [InlineKeyboardButton("🟢 6 أشهر (28 JD)", callback_data="pkg_b3_6m")],
                [InlineKeyboardButton("🟢 سنة كاملة (48 JD)", callback_data="pkg_b3_1y")],
                [InlineKeyboardButton("⬅️ رجوع لتعديل المنصات", callback_data="bundle_init_3")]
            ]
        else:
            text = "💎 عرض الـ 4 منصات معاً - الباكج الشامل (8 JD للشهر)\nاختر المدة المطلوبة:"
            kb = [
                [InlineKeyboardButton("🟢 شهر واحد (8 JD)", callback_data="pkg_b4_1m")],
                [InlineKeyboardButton("🟢 3 أشهر (20 JD)", callback_data="pkg_b4_3m")],
                [InlineKeyboardButton("🟢 6 أشهر (36 JD)", callback_data="pkg_b4_6m")],
                [InlineKeyboardButton("🟢 سنة كاملة (60 JD)", callback_data="pkg_b4_1y")],
                [InlineKeyboardButton("⬅️ رجوع لتعديل المنصات", callback_data="bundle_init_4")]
            ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("pkg_"):
        parts = data.split("_")
        
        if parts[1] == "chatgpt":
            sub_type = f"{parts[1]}_{parts[2]}"
            duration = parts[3]
        else:
            sub_type = parts[1]
            duration = parts[2]

        context.user_data['current_sub'] = sub_type

        p_names = {
            "netflix": "Netflix 4K",
            "shahid": "Shahid VIP",
            "osn": "OSN+",
            "disney": "Disney+",
            "noor": "Noor Play",
            "tod": "TOD",
            "chatgpt_shared": "ChatGPT Plus (مشترك)",
            "chatgpt_private": "ChatGPT Plus (خاص)"
        }

        if sub_type.startswith("b"):
            selected_keys = context.user_data.get('selected_platforms', [])
            selected_names = [p_names.get(k, k) for k in selected_keys]
            platforms_str = " + ".join(selected_names) if selected_names else "منصات متعددة"
            
            if sub_type == "b2":
                sub_name = f"عرض منصتين ({platforms_str})"
            elif sub_type == "b3":
                sub_name = f"عرض 3 منصات ({platforms_str})"
            else:
                sub_name = f"الباكج الشامل (4 منصات: {platforms_str})"
        else:
            sub_name = p_names.get(sub_type, "اشتراك رقمي")

        if sub_type == "b2":
            prices = {"1m": "5 دنانير", "3m": "12 دينار", "6m": "22 دينار", "1y": "38 دينار"}
            dur_map = {"1m": "شهر واحد", "3m": "3 أشهر", "6m": "6 أشهر", "1y": "سنة كاملة"}
        elif sub_type == "b3":
            prices = {"1m": "6 دنانير", "3m": "15 دينار", "6m": "28 دينار", "1y": "48 دينار"}
            dur_map = {"1m": "شهر واحد", "3m": "3 أشهر", "6m": "6 أشهر", "1y": "سنة كاملة"}
        elif sub_type == "b4":
            prices = {"1m": "8 دنانير", "3m": "20 دينار", "6m": "36 دينار", "1y": "60 دينار"}
            dur_map = {"1m": "شهر واحد", "3m": "3 أشهر", "6m": "6 أشهر", "1y": "سنة كاملة"}
        elif sub_type == "tod":
            prices = {"1m": "6 دنانير", "3m": "9 دنانير"}
            dur_map = {"1m": "شهر واحد", "3m": "3 أشهر"}
        elif sub_type == "chatgpt_shared":
            prices = {"1m": "2.5 دينار", "3m": "5 دنانير", "6m": "9 دنانير", "1y": "15 دينار"}
            dur_map = {"1m": "شهر واحد", "3m": "3 أشهر", "6m": "6 أشهر", "1y": "سنة كاملة"}
        elif sub_type == "chatgpt_private":
            prices = {"1m": "8 دنانير"}
            dur_map = {"1m": "شهر واحد"}
        else:
            prices = {"1m": "2.5 دينار", "3m": "5 دنانير", "6m": "9 دنانير", "1y": "15 دينار"}
            dur_map = {"1m": "شهر واحد", "3m": "3 أشهر", "6m": "6 أشهر", "1y": "سنة كاملة"}

        price = prices.get(duration, "حسب الباقة")
        dur_text = dur_map.get(duration, "")

        context.user_data['sub_name_text'] = sub_name
        context.user_data['dur_text'] = dur_text
        context.user_data['price_text'] = price

        summary_text = (
            "🛒 ملخص طلب الاشتراك\n\n"
            f"📌 الخدمة / الباقة: {sub_name}\n"
            f"⏳ المدة: {dur_text}\n"
            f"💵 السعر الإجمالي: {price}\n\n"
        )

        if sub_type == "chatgpt_shared" and duration in ["3m", "6m", "1y"]:
            summary_text += "⚠️ **ملاحظة هامة:** في الاشتراكات المشتركة طويلة الأجل (3 أشهر، 6 أشهر، سنة)، يتم تزويدك **بكل شهر بإيميل مختلف** لضمان استمرارية الضمان.\n\n"

        summary_text += "اضغط على زر 'شراء' أدناه لإتمام الدفع أو تراجع للخلف:"
        
        if sub_type.startswith("b"):
            back_target = f"bundle_init_{sub_type.replace('b', '')}"
        elif sub_type == "chatgpt_shared":
            back_target = "sub_chatgpt_shared_menu"
        elif sub_type == "chatgpt_private":
            back_target = "sub_chatgpt_menu"
        else:
            back_target = f"sub_{sub_type}"

        buy_keyboard = [
            [InlineKeyboardButton("💳 شراء وإتمام الدفع", callback_data=f"buy_{sub_type}_{duration}")],
            [InlineKeyboardButton("⬅️ رجوع", callback_data=back_target)]
        ]
        await query.message.edit_text(summary_text, reply_markup=InlineKeyboardMarkup(buy_keyboard))

    elif data.startswith("buy_"):
        parts = data.split("_")
        
        if parts[1] == "chatgpt":
            sub_type = f"{parts[1]}_{parts[2]}"
            duration = parts[3]
        else:
            sub_type = parts[1]
            duration = parts[2]

        if sub_type == "b2":
            prices = {"1m": "5 دنانير", "3m": "12 دينار", "6m": "22 دينار", "1y": "38 دينار"}
        elif sub_type == "b3":
            prices = {"1m": "6 دنانير", "3m": "15 دينار", "6m": "28 دينار", "1y": "48 دينار"}
        elif sub_type == "b4":
            prices = {"1m": "8 دنانير", "3m": "20 دينار", "6m": "36 دينار", "1y": "60 دينار"}
        elif sub_type == "tod":
            prices = {"1m": "6 دنانير", "3m": "9 دنانير"}
        elif sub_type == "chatgpt_shared":
            prices = {"1m": "2.5 دينار", "3m": "5 دنانير", "6m": "9 دنانير", "1y": "15 دينار"}
        elif sub_type == "chatgpt_private":
            prices = {"1m": "8 دنانير"}
        else:
            prices = {"1m": "2.5 دينار", "3m": "5 دنانير", "6m": "9 دنانير", "1y": "15 دينار"}

        price = prices.get(duration, "حسب الباقة")

        checkout_text = (
            "💳 معلومات الدفع عبر كليك (CliQ)\n\n"
            f"{CLIQ_INFO}\n\n"
            f"💵 المطلوب تحويله: {price}\n\n"
            "📸 الخطوة الأخيرة: قم بتحويل المبلغ، ثم أرسل صورة (سكرين شوت) للإيصال هنا في الشات وسنقوم بتفعيل باقتك فوراً!"
        )
        
        back_keyboard = [
            [InlineKeyboardButton("⬅️ رجوع", callback_data=f"pkg_{sub_type}_{duration}")]
        ]
        await query.message.edit_text(checkout_text, reply_markup=InlineKeyboardMarkup(back_keyboard))
        context.user_data['waiting_for_receipt'] = True

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    is_member = await check_user_channel_membership(context.bot, user.id)
    if not is_member:
        await update.message.reply_text("⚠️ يرجى الاشتراك في قناة المتجر أولاً للاستمرار: https://t.me/El962Store")
        return

    if context.user_data.get('waiting_for_issue_description'):
        platform_name = context.user_data.get('issue_platform', 'منصة رقمية')
        issue_email = context.user_data.get('issue_email', 'غير محدد')
        
        await update.message.reply_text(
            "✅ **تم استلام صورة المشكلة وبلاغك بنجاح!**\n"
            "فريق الدعم في متجر 962ElStore سيقوم بمراجعتها والرد عليك قريباً جداً ⏳"
        )

        admin_msg = (
            "⚠️ **تنبيه: بلاغ مشكلة مع صورة من زبون!**\n\n"
            f"👤 اسم الزبون: {user.full_name}\n"
            f"🔗 يوزر الزبون: @{user.username if user.username else 'لا يوجد'}\n"
            f"🆔 معرف الزبون: {user.id}\n\n"
            f"📦 المنصة: {platform_name}\n"
            f"📧 البريد الإلكتروني للحساب:\n`{issue_email}`\n\n"
            f"🟢 حالة الطلب: لم يتم الاستلام بعد\n\n"
            f"👇 انسخ هذا الأمر للرد:\n"
            f"```\n/reply {user.id} ضع_الرد_هنا\n```"
        )

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🙋‍♂️ استلام (محمد)", callback_data=f"claim_m_{user.id}"),
             InlineKeyboardButton("🙋‍♂️ استلام (حسام)", callback_data=f"claim_h_{user.id}")]
        ])

        try:
            for admin_id in ADMINS:
                await context.bot.send_photo(
                    chat_id=admin_id,
                    photo=update.message.photo[-1].file_id,
                    caption=admin_msg,
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
        except Exception as e:
            print(f"Error: {e}")

        context.user_data['waiting_for_issue_description'] = False
        return

    if context.user_data.get('waiting_for_receipt'):
        current_sub = context.user_data.get('current_sub', 'default')
        receipt_text = RECEIPT_INSTRUCTIONS.get(current_sub, RECEIPT_INSTRUCTIONS['default'])

        await update.message.reply_text(receipt_text)

        sub_name = context.user_data.get('sub_name_text', 'باقة ترفيهية')
        dur_text = context.user_data.get('dur_text', 'غير محدد')
        price_text = context.user_data.get('price_text', 'غير محدد')

        admin_message = (
            "🚨 طلب اشتراك جديد تم دفع إيصاله (962ElStore)!\n\n"
            f"اسم الزبون: {user.full_name}\n"
            f"يوزر الزبون: @{user.username if user.username else 'لا يوجد'}\n"
            f"🆔 معرف الزبون: {user.id}\n\n"
            f"الخدمة / الباقة: {sub_name}\n"
            f"المدة: {dur_text}\n"
            f"السعر المدفوع: {price_text}\n\n"
            f"🟢 حالة الطلب: لم يتم الاستلام بعد\n\n"
            f"👇 انسخ هذا الأمر للرد:\n"
            f"```\n/reply {user.id} ضع_معلومات_الحساب_هنا\n```"
        )

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🙋‍♂️ استلام (محمد)", callback_data=f"claim_m_{user.id}"),
             InlineKeyboardButton("🙋‍♂️ استلام (حسام)", callback_data=f"claim_h_{user.id}")]
        ])

        try:
            for admin_id in ADMINS:
                await context.bot.send_photo(
                    chat_id=admin_id,
                    photo=update.message.photo[-1].file_id,
                    caption=admin_message,
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
        except Exception as e:
            print(f"Error: {e}")

        context.user_data['waiting_for_receipt'] = False
    else:
        await update.message.reply_text("يرجى استخدام الأزرار في القائمة للتنقل بسلاسة.")

def main():
    while True:
        try:
            app = ApplicationBuilder().token(TOKEN).build()
            
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("reply", admin_reply))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            app.add_handler(CallbackQueryHandler(button_handler))
            app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
            
            print("962ElStore Bot is running smoothly with fixed Claim handler...")
            app.run_polling(drop_pending_updates=True)
        except Exception as e:
            print(f"Error: {e}. Restarting in 5 seconds...")
            time.sleep(5)

if __name__ == '__main__':
    main()
