import logging
import threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import sqlite3

# إعداد خادم ويب خفيف لضمان عدم إغلاق الخدمة على Render (Web Service)
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "962ElStore Bot is active and running 24/7!"

def run_web():
    web_app.run(host="0.0.0.0", port=8080)

# تشغيل خادم الويب في خلفية منفصلة
threading.Thread(target=run_web).start()

# التوكن ورقم الأدمن الخاص بك
TOKEN = "8600844088:AAGWB9gpw3ETz0R0hGQxOmmGVVW9bAGmFls"
ADMIN_ID = 7983029778

# يوزر نيم حساب الدعم الفني الخاص بك
SUPPORT_USERNAME = "@e962ElStore"

# معلومات كليك المحدثة
CLIQ_INFO = (
    "🔹 **معلومات الدفع عبر كليك (CliQ):**\n"
    "• **الاسم المستعار:** `XM22`\n"
    "• **مزود الخدمة:** البنك العربي الإسلامي الدولي\n"
    "• **اسم المستلم:** محمد بلال فايز بني احمد"
)

# تعليمات ما بعد الدفع وإرسال الإيصال لكل منصة
RECEIPT_INSTRUCTIONS = {
    "netflix": (
        "✅ **تم استلام صورة الإيصال بنجاح!**\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 **سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول:**\n"
        "• يرجى إدخال البريد الإلكتروني، ثم **الرجوع للقائمة الرئيسية لطلب الكود الخاص بتسجيل الدخول**.\n"
        "⚠️ **تنبيه هام:** التسجيل متاح في **جهاز واحد فقط**، وسيتم سحب الحساب فوراً إذا تم فتحه على جهازين بنفس الوقت!"
    ),
    "shahid": (
        "✅ **تم استلام صورة الإيصال بنجاح!**\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 **سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول:**\n"
        "• يرجى إدخال البريد الإلكتروني وكلمة السر لتسجيل الدخول.\n"
        "⚠️ **تنبيه هام:** يمنع الدخول إلى الحساب أكثر من جهاز، وسوف يتم سحب الاشتراك إذا تم الفتح على جهازين وأكثر!"
    ),
    "osn": (
        "✅ **تم استلام صورة الإيصال بنجاح!**\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 **سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول:**\n"
        "• يرجى إدخال البريد الإلكتروني، ثم **الرجوع للقائمة الرئيسية لطلب الكود الخاص بتسجيل الدخول**.\n"
        "⚠️ **تنبيه هام:** التسجيل متاح في **جهاز واحد فقط**، وسيتم سحب الحساب فوراً إذا تم فتحه على جهازين بنفس الوقت!"
    ),
    "disney": (
        "✅ **تم استلام صورة الإيصال بنجاح!**\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 **سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول:**\n"
        "• يرجى استخدام **رقم تلفون و كود** لتسجيل الدخول.\n"
        "⚠️ **تنبيه هام:** مخصص لجهاز واحد فقط لضمان استقرار الضمان."
    ),
    "noor": (
        "✅ **تم استلام صورة الإيصال بنجاح!**\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 **سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول:**\n"
        "• يرجى إدخال البريد الإلكتروني وكلمة السر لتسجيل الدخول.\n"
        "⚠️ **تنبيه هام:** يمنع الدخول إلى الحساب أكثر من جهاز، وسوف يتم سحب الاشتراك إذا تم الفتح على جهازين وأكثر!"
    ),
    "tod": (
        "✅ **تم استلام صورة الإيصال بنجاح!**\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 **سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول:**\n"
        "• يرجى استخدام **رقم تلفون و باسورد** لتسجيل الدخول.\n"
        "⚠️ **تنبيه هام:** الحساب يعمل على جهازين FHD كحد أقصى."
    )
}

# القائمة الرئيسية الثابتة
def get_main_menu():
    keyboard = [
        [KeyboardButton("🛒 الاشتراكات المتوفرة"), KeyboardButton("🔑 طلب كود")],
        [KeyboardButton("🛠 التواصل مع الدعم")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"أهلاً بك في متجر **962ElStore** للتسوق الرقمي!\n\n"
        f"🆔 رقمك التعريفي: `{user.id}`\n"
        f"👤 الاسم: {user.full_name}\n\n"
        f"اختر من القائمة أدناه للبدء:"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_menu())

# التعامل مع الأزرار النصية الرئيسية
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🛒 الاشتراكات المتوفرة":
        subs_keyboard = [
            [InlineKeyboardButton("🎬 Netflix - نتفليكس", callback_data="sub_netflix")],
            [InlineKeyboardButton("📺 Shahid VIP - شاهد", callback_data="sub_shahid")],
            [InlineKeyboardButton("🎥 OSN+ - أوس إن", callback_data="sub_osn")],
            [InlineKeyboardButton("✨ Disney+ - ديزني", callback_data="sub_disney")],
            [InlineKeyboardButton("🌙 Noor Play - نور بلاي", callback_data="sub_noor")],
            [InlineKeyboardButton("⚽ TOD - تود (رياضة وترفيه)", callback_data="sub_tod")]
        ]
        await update.message.reply_text(
            "📦 **قسم الاشتراكات الرقمية:**\nاختر المنصة التي ترغب بالاشتراك بها:",
            reply_markup=InlineKeyboardMarkup(subs_keyboard),
            parse_mode="Markdown"
        )
        
    elif text == "🔑 طلب كود":
        await update.message.reply_text(
            "🔑 **قسم طلب الأكواد:**\n\n"
            "إذا قمت بالدفع وتحتاج إلى استلام كود التفعيل أو التحقق (مثل نتفليكس أو أوس إن) الخاص بحسابك، يرجى تزويدنا برقم الطلب أو التواصل مباشرة مع الدعم الفني لتسليمك الكود فوراً."
        )
        
    elif text == "🛠 التواصل مع الدعم":
        support_text = (
            f"🛠 **الدعم الفني وخدمة العملاء - 962ElStore**\n\n"
            f"إذا واجهتك أي مشكلة أو استفسار، يسعدنا تواصلك معنا مباشرة عبر حساب الدعم:\n"
            f"💬 {SUPPORT_USERNAME}\n\n"
            f"نحن في خدمتكم على مدار الساعة!"
        )
        await update.message.reply_text(support_text, parse_mode="Markdown")

# التعامل مع الأزرار التفاعلية وأزرار الرجوع
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_subs":
        subs_keyboard = [
            [InlineKeyboardButton("🎬 Netflix - نتفليكس", callback_data="sub_netflix")],
            [InlineKeyboardButton("📺 Shahid VIP - شاهد", callback_data="sub_shahid")],
            [InlineKeyboardButton("🎥 OSN+ - أوس إن", callback_data="sub_osn")],
            [InlineKeyboardButton("✨ Disney+ - ديزني", callback_data="sub_disney")],
            [InlineKeyboardButton("🌙 Noor Play - نور بلاي", callback_data="sub_noor")],
            [InlineKeyboardButton("⚽ TOD - تود (رياضة وترفيه)", callback_data="sub_tod")]
        ]
        await query.message.edit_text(
            "📦 **قسم الاشتراكات الرقمية:**\nاختر المنصة التي ترغب بالاشتراك بها:",
            reply_markup=InlineKeyboardMarkup(subs_keyboard),
            parse_mode="Markdown"
        )

    # 1. نتفليكس
    elif data == "sub_netflix":
        text = "🎬 **اشتراك Netflix - جودة 4K (بروفايل خاص - جهاز واحد)**\n\nاختر المدة المطلوبة:"
        kb = [
            [InlineKeyboardButton("🟢 شهر واحد (2.5 JD)", callback_data="pkg_netflix_1m")],
            [InlineKeyboardButton("🟢 3 أشهر (5 JD)", callback_data="pkg_netflix_3m")],
            [InlineKeyboardButton("🟢 6 أشهر (9 JD)", callback_data="pkg_netflix_6m")],
            [InlineKeyboardButton("🟢 سنة كاملة (15 JD)", callback_data="pkg_netflix_1y")],
            [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_subs")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    # 2. شاهد
    elif data == "sub_shahid":
        text = "📺 **اشتراك Shahid VIP - شاهد (جهاز واحد)**\n\nاختر المدة المطلوبة:"
        kb = [
            [InlineKeyboardButton("🟢 شهر واحد (2.5 JD)", callback_data="pkg_shahid_1m")],
            [InlineKeyboardButton("🟢 3 أشهر (5 JD)", callback_data="pkg_shahid_3m")],
            [InlineKeyboardButton("🟢 6 أشهر (9 JD)", callback_data="pkg_shahid_6m")],
            [InlineKeyboardButton("🟢 سنة كاملة (15 JD)", callback_data="pkg_shahid_1y")],
            [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_subs")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    # 3. أوس إن
    elif data == "sub_osn":
        text = "🎥 **اشتراك OSN+ - أوس إن (جهاز واحد)**\n\nاختر المدة المطلوبة:"
        kb = [
            [InlineKeyboardButton("🟢 شهر واحد (2.5 JD)", callback_data="pkg_osn_1m")],
            [InlineKeyboardButton("🟢 3 أشهر (5 JD)", callback_data="pkg_osn_3m")],
            [InlineKeyboardButton("🟢 6 أشهر (9 JD)", callback_data="pkg_osn_6m")],
            [InlineKeyboardButton("🟢 سنة كاملة (15 JD)", callback_data="pkg_osn_1y")],
            [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_subs")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    # 4. ديزني
    elif data == "sub_disney":
        text = "✨ **اشتراك Disney+ - ديزني (جهاز واحد)**\n\nاختر المدة المطلوبة:"
        kb = [
            [InlineKeyboardButton("🟢 شهر واحد (2.5 JD)", callback_data="pkg_disney_1m")],
            [InlineKeyboardButton("🟢 3 أشهر (5 JD)", callback_data="pkg_disney_3m")],
            [InlineKeyboardButton("🟢 6 أشهر (9 JD)", callback_data="pkg_disney_6m")],
            [InlineKeyboardButton("🟢 سنة كاملة (15 JD)", callback_data="pkg_disney_1y")],
            [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_subs")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    # 5. نور بلاي
    elif data == "sub_noor":
        text = "🌙 **اشتراك Noor Play - نور بلاي (جهاز واحد)**\n\nاختر المدة المطلوبة:"
        kb = [
            [InlineKeyboardButton("🟢 شهر واحد (2.5 JD)", callback_data="pkg_noor_1m")],
            [InlineKeyboardButton("🟢 3 أشهر (5 JD)", callback_data="pkg_noor_3m")],
            [InlineKeyboardButton("🟢 6 أشهر (9 JD)", callback_data="pkg_noor_6m")],
            [InlineKeyboardButton("🟢 سنة كاملة (15 JD)", callback_data="pkg_noor_1y")],
            [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_subs")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    # 6. تود
    elif data == "sub_tod":
        text = "⚽ **اشتراك TOD - تود (رياضة وترفيه)**\n(حساب جاهز - يعمل على جهازين FHD)\n\nاختر المدة المطلوبة:"
        kb = [
            [InlineKeyboardButton("🟢 شهر واحد - جهازين FHD (6 JD)", callback_data="pkg_tod_1m")],
            [InlineKeyboardButton("🟢 3 أشهر - جهازين FHD (9 JD)", callback_data="pkg_tod_3m")],
            [InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_subs")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    # ملخص الباقة وزر الشراء
    elif data.startswith("pkg_"):
        parts = data.split("_")
        sub_type = parts[1]
        duration = parts[2]

        context.user_data['current_sub'] = sub_type

        details_map = {
            "netflix": "Netflix - جودة 4K (بروفايل خاص - جهاز واحد)",
            "shahid": "Shahid VIP (جهاز واحد)",
            "osn": "OSN+ (جهاز واحد)",
            "disney": "Disney+ (جهاز واحد)",
            "noor": "Noor Play (جهاز واحد)",
            "tod": "TOD (رياضة وترفيه - جهازين FHD)"
        }
        
        sub_name = details_map.get(sub_type, "اشتراك رقمي")

        if sub_type == "tod":
            price = "6 دنانير" if duration == "1m" else "9 دنانير"
            dur_text = "شهر واحد" if duration == "1m" else "3 أشهر"
        else:
            prices = {"1m": "2.5 دينار", "3m": "5 دنانير", "6m": "9 دنانير", "1y": "15 دينار"}
            dur_map = {"1m": "شهر واحد", "3m": "3 أشهر", "6m": "6 أشهر", "1y": "سنة كاملة"}
            price = prices.get(duration, "حسب الباقة")
            dur_text = dur_map.get(duration, "")

        summary_text = (
            f"🛒 **ملخص طلب الاشتراك**\n\n"
            f"📌 **المنصة:** {sub_name}\n"
            f"⏳ **المدة:** {dur_text}\n"
            f"💵 **السعر الإجمالي:** {price}\n\n"
            f"اضغط على زر **'شراء'** أدناه لإتمام الدفع أو تراجع للوراء:"
        )
        
        buy_keyboard = [
            [InlineKeyboardButton("💳 شراء", callback_data=f"buy_{sub_type}_{duration}")],
            [InlineKeyboardButton("🔙 رجوع لاختيار الباقات", callback_data=f"sub_{sub_type}")]
        ]
        await query.message.edit_text(summary_text, reply_markup=InlineKeyboardMarkup(buy_keyboard), parse_mode="Markdown")

    # معلومات كليك وزر الشراء النهائي
    elif data.startswith("buy_"):
        parts = data.split("_")
        sub_type = parts[1]
        duration = parts[2]

        if sub_type == "tod":
            price = "6 دنانير" if duration == "1m" else "9 دنانير"
        else:
            prices = {"1m": "2.5 دينار", "3m": "5 دنانير", "6m": "9 دنانير", "1y": "15 دينار"}
            price = prices.get(duration, "حسب الباقة")

        checkout_text = (
            f"💳 **معلومات الدفع عبر كليك (CliQ)**\n\n"
            f"{CLIQ_INFO}\n\n"
            f"💵 **المطلوب تحويله:** {price}\n\n"
            f"📸 **الخطوة الأخيرة:** قم بتحويل المبلغ، ثم **أرسل صورة (سكرين شوت) للإيصال** هنا في الشات وسنقوم بتفعيل طلبك فوراً!"
        )
        
        back_keyboard = [
            [InlineKeyboardButton("🔙 رجوع", callback_data=f"pkg_{sub_type}_{duration}")]
        ]
        await query.message.edit_text(checkout_text, reply_markup=InlineKeyboardMarkup(back_keyboard), parse_mode="Markdown")
        context.user_data['waiting_for_receipt'] = True

# استقبال صور الإيصالات وإرسال التعليمات الدقيقة بناءً على المنصة
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_receipt'):
        current_sub = context.user_data.get('current_sub', 'netflix')
        receipt_text = RECEIPT_INSTRUCTIONS.get(current_sub, "✅ تم استلام الإيصال بنجاح وسيتم تزويدك بالبيانات قريباً.")

        await update.message.reply_text(receipt_text, parse_mode="Markdown")
        context.user_data['waiting_for_receipt'] = False
    else:
        await update.message.reply_text("يرجى استخدام الأزرار في القائمة للتنقل بسلاسة.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("962ElStore Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
