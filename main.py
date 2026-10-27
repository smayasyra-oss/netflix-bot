import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import sqlite3

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
        
