import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import sqlite3

# التوكن ورقم الأدمن الخاص بك
TOKEN = "8600844088:AAGWB9gpw3ETz0R0hGQxOmmGVVW9bAGmFls"
ADMIN_ID = 7983029778

CLIQ_INFO = "0776453875 (962ElStore)"

# تعليمات تسجيل الدخول الخاصة بكل منصة
LOGIN_INSTRUCTIONS = {
    "netflix": (
        "🎬 **تعليمات تسجيل الدخول لـ Netflix (4K):**\n"
        "1. قم بتسجيل الدخول بالبريد وكلمة المرور المرسلة.\n"
        "2. ادخل حصرياً إلى **البروفايل المخصص لك** فقط.\n"
        "3. يمنع منعاً باتاً تغيير كلمة المرور أو إعدادات البروفايل لضمان استمرار عمل الضمان."
    ),
    "shahid": (
        "📺 **تعليمات تسجيل الدخول لـ Shahid VIP:**\n"
        "1. سجل الدخول بالحساب المرسل.\n"
        "2. اختر البروفايل الخاص بك فقط ولا تدخل بروفايلات الآخرين.\n"
        "3. حافظ على خصوصية الحساب واستمتع بالمشاهدة."
    ),
    "osn": (
        "🎥 **تعليمات تسجيل الدخول لـ OSN+:**\n"
        "1. افتح تطبيق OSN+ وسجل الدخول بالبيانات.\n"
        "2. التزم بالبروفايل المخصص لك لضمان استقرار الخدمة."
    ),
    "disney": (
        "✨ **تعليمات تسجيل الدخول لـ Disney+:**\n"
        "1. سجل الدخول عبر التطبيق أو الموقع.\n"
        "2. توجه إلى بروفايلك الخاص واستمتع بأضخم الأعمال بجودة عالية."
    ),
    "noor": (
        "🌙 **تعليمات تسجيل الدخول لـ Noor Play:**\n"
        "1. قم بتسجيل الدخول بالبيانات المرسلة.\n"
        "2. اختر البروفايل المخصص لك ولا تقم بتعديل إعدادات الحساب."
    ),
    "tod": (
        "⚽ **تعليمات تسجيل الدخول لـ TOD:**\n"
        "1. الحساب يعمل على **جهازين FHD** في نفس الوقت كحد أقصى.\n"
        "2. لا تتجاوز الحد المسموح للأجهزة حتى لا يتوقف الحساب.\n"
        "مشاهدة ممتعة للمباريات والأفلام!"
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
            "إذا قمت بالدفع وتحتاج إلى استلام كود التفعيل أو التحقق الخاص بحسابك، يرجى تزويدنا برقم الطلب أو التواصل مباشرة مع الدعم الفني لتسليمك الكود فوراً."
        )
        
    elif text == "🛠 التواصل مع الدعم":
        await update.message.reply_text("💬 للدعم الفني والمتابعة بعد الشراء: @YourSupportUsername")

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
        text = "🎬 **اشتراك Netflix - جودة 4K**\n\nاختر المدة المطلوبة:"
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
        text = "📺 **اشتراك Shahid VIP - شاهد**\n\nاختر المدة المطلوبة:"
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
        text = "🎥 **اشتراك OSN+ - أوس إن**\n\nاختر المدة المطلوبة:"
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
        text = "✨ **اشتراك Disney+ - ديزني**\n\nاختر المدة المطلوبة:"
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
        text = "🌙 **اشتراك Noor Play - نور بلاي**\n\nاختر المدة المطلوبة:"
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

        if sub_type == "tod":
            price = "6 دنانير" if duration == "1m" else "9 دنانير"
        else:
            prices = {"1m": "2.5 دينار", "3m": "5 دنانير", "6m": "9 دنانير", "1y": "15 دينار"}
            price = prices.get(duration, "حسب الباقة")

        summary_text = (
            f"🛒 **ملخص طلب الاشتراك**\n\n"
            f"📌 الباقة المختارة جاهزة للتفعيل\n"
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
            f"🔹 **رقم/حساب كليك:**\n`{CLIQ_INFO}`\n\n"
            f"💵 **المطلوب تحويله:** {price}\n\n"
            f"📸 **الخطوة الأخيرة:** قم بتحويل المبلغ، ثم **أرسل صورة (سكرين شوت) للإيصال** هنا في الشات وسنقوم بتفعيل طلبك فوراً!"
        )
        
        back_keyboard = [
            [InlineKeyboardButton("🔙 رجوع", callback_data=f"pkg_{sub_type}_{duration}")]
        ]
        await query.message.edit_text(checkout_text, reply_markup=InlineKeyboardMarkup(back_keyboard), parse_mode="Markdown")
        context.user_data['waiting_for_receipt'] = True

# استقبال صور الإيصالات وإرسال التعليمات بناءً على المنصة
async def handle_photo(update
