import logging
import threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import sqlite3

# إعداد خادم ويب خفيف لضمان عدم إغلاق الخدمة على Render
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
    "default": (
        "✅ **تم استلام صورة الإيصال بنجاح!**\n"
        "شكراً لك لاختيارك متجر **962ElStore**[span_0](start_span)[span_0](end_span).\n\n"
        "📦 **سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول قريباً:**\n"
        "⚠️ **تنبيه هام:** يرجى الالتزام بعدم فتح الحساب على أجهزة أكثر من المسموح به لضمان استمرار ضمانك!"
    ),
    "netflix": (
        "✅ **تم استلام صورة الإيصال بنجاح!**\n"
        "شكراً لك لاختيارك متجر **962ElStore**[span_1](start_span)[span_1](end_span).\n\n"
        "📦 **سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول:**\n"
        "• يرجى إدخال البريد الإلكتروني، ثم **الرجوع للقائمة الرئيسية لطلب الكود الخاص بتسجيل الدخول**.\n"
        "⚠️ **تنبيه هام:** التسجيل متاح في **جهاز واحد فقط**، وسيتم سحب الحساب فوراً إذا تم فتحه على جهازين بنفس الوقت!"
    ),
    "shahid": (
        "✅ **تم استلام صورة الإيصال بنجاح!**\n"
        "شكراً لك لاختيارك متجر **962ElStore**[span_2](start_span)[span_2](end_span).\n\n"
        "📦 **سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول:**\n"
        "• يرجى إدخال البريد الإلكتروني وكلمة السر لتسجيل الدخول.\n"
        "⚠️ **تنبيه هام:** يمنع الدخول إلى الحساب أكثر من جهاز، وسوف يتم سحب الاشتراك إذا تم الفتح على جهازين وأكثر!"
    ),
    "osn": (
        "✅ **تم استلام صورة الإيصال بنجاح!**\n"
        "شكراً لك لاختيارك متجر **962ElStore**[span_3](start_span)[span_3](end_span).\n\n"
        "📦 **سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول:**\n"
        "• يرجى إدخال البريد الإلكتروني، ثم **الرجوع للقائمة الرئيسية لطلب الكود الخاص بتسجيل الدخول**.\n"
        "⚠️ **تنبيه هام:** التسجيل متاح في **جهاز واحد فقط**، وسيتم سحب الحساب فوراً إذا تم فتحه على جهازين بنفس الوقت!"
    ),
    "disney": (
        "✅ **تم استلام صورة الإيصال بنجاح!**\n"
        "شكراً لك لاختيارك متجر **962ElStore**[span_4](start_span)[span_4](end_span).\n\n"
        "📦 **سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول:**\n"
        "• يرجى استخدام **رقم تلفون و كود** لتسجيل الدخول.\n"
        "⚠️ **تنبيه هام:** مخصص لجهاز واحد فقط لضمان استقرار الضمان."
    ),
    "noor": (
        "✅ **تم استلام صورة الإيصال بنجاح!**\n"
        "شكراً لك لاختيارك متجر **962ElStore**[span_5](start_span)[span_5](end_span).\n\n"
        "📦 **سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول:**\n"
        "• يرجى إدخال البريد الإلكتروني وكلمة السر لتسجيل الدخول.\n"
        "⚠️ **تنبيه هام:** يمنع الدخول إلى الحساب أكثر من جهاز، وسوف يتم سحب الاشتراك إذا تم الفتح على جهازين وأكثر!"
    ),
    "tod": (
        "✅ **تم استلام صورة الإيصال بنجاح!**\n"
        "شكراً لك لاختيارك متجر **962ElStore**[span_6](start_span)[span_6](end_span).\n\n"
        "📦 **سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول:**\n"
        "• يرجى استخدام **رقم تلفون و باسورد** لتسجيل الدخول.\n"
        "⚠️ **تنبيه هام:** الحساب يعمل على جهازين FHD كحد أقصى[span_7](start_span)[span_7](end_span)."
    )
}

# القائمة الرئيسية الثابتة
def get_main_menu():
    keyboard = [
        [KeyboardButton("🛒 الاشتراكات الفردية"), KeyboardButton("🔥 عروض التوفير الكبرى")],
        [KeyboardButton("🔑 طلب كود"), KeyboardButton("🛠 التواصل مع الدعم")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"أهلاً بك في متجر **962ElStore** للتسوق الرقمي[span_8](start_span)[span_8](end_span)!\n\n"
        f"كل اللي تحبه من عالم الترفيه بأسرار مميزة وأسعار منافسة 🎬🍿\n\n"
        f"🆔 رقمك التعريفي: `{user.id}`\n"
        f"👤 الاسم: {user.full_name}\n\n"
        f"اختر من القائمة أدناه للبدء:"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=get_main_menu())

# أمر الرد المخصص للأدمن (/reply [user_id] [message])
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("❌ الاستخدام الصحيح للأمر:\n`/reply [user_id] [الرسالة]`", parse_mode="Markdown")
        return

    target_user_id = args[0]
    reply_message = " ".join(args[1:])

    try:
        await context.bot.send_message(
            chat_id=target_user_id,
            text=f"📬 **رد جديد من الإدارة (962ElStore):**\n\n{reply_message}",
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ تم إرسال الرد إلى الزبون بنجاح!")
    except Exception as e:
        await update.message.reply_text(f"❌ فشل إرسال الرسالة للزبون. تأكد من صحة الـ ID.\nالخطأ: {e}")

# التعامل مع الأزرار النصية الرئيسية
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # التعامل مع طلب كود السكن (نتفليكس)
    if context.user_data.get('waiting_for_netflix_household_email'):
        user = update.effective_user
        netflix_email = text
        
        await update.message.reply_text(
            "✅ **تم استلام بريد نتفليكس بنجاح!**\n"
            "جارٍ إرسال طلب كود السكن للأدمن، سيتم تزويدك بالكود في أقرب وقت ممكن ⏳",
            parse_mode="Markdown"
        )

        admin_msg = (
            f"🏠 **طلب كود سكن نتفليكس (Household Code)!**\n\n"
            f"👤 **اسم الزبون:** {user.full_name}\n"
            f"🔗 **يوزر الزبون:** @{user.username if user.username else 'لا يوجد'}\n"
            f"🆔 **معرف الزبون (ID):** `{user.id}`\n\n"
            f"📧 **إيميل نتفليكس المطلوب له الكود:**\n`{netflix_email}`\n\n"
            f"💡 للرد عليه استخدم الأمر:\n`/reply {user.id} [الكود هنا]`"
        )
        
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode="Markdown")
        except Exception as e:
            print(f"Error sending household request to admin: {e}")

        context.user_data['waiting_for_netflix_household_email'] = False
        return

    # التعامل مع طلب كود تسجيل الدخول لأي منصة
    if context.user_data.get('waiting_for_login_code_email'):
        user = update.effective_user
        platform_name = context.user_data.get('login_code_platform', 'منصة رقمية')
        account_info = text
        
        await update.message.reply_text(
            f"✅ **تم استلام تفاصيل حساب ({platform_name}) بنجاح!**\n"
            "جارٍ إرسال طلب كود تسجيل الدخول للأدمن، سيتم تزويدك بالكود قريباً ⏳",
            parse_mode="Markdown"
        )

        admin_msg = (
            f"🔑 **طلب كود تسجيل دخول جديد!**\n\n"
            f"👤 **اسم الزبون:** {user.full_name}\n"
            f"🔗 **يوزر الزبون:** @{user.username if user.username else 'لا يوجد'}\n"
            f"🆔 **معرف الزبون (ID):** `{user.id}`\n\n"
            f"📦 **المنصة:** {platform_name}\n"
            f"📧 **معلومات الحساب / الإيميل:**\n`{account_info}`\n\n"
            f"💡 للرد عليه استخدم الأمر:\n`/reply {user.id} [الكود هنا]`"
        )
        
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode="Markdown")
        except Exception as e:
            print(f"Error sending login code request to admin: {e}")

        context.user_data['waiting_for_login_code_email'] = False
        return

    # باقي الأزرار النصية
    if text == "🛒 الاشتراكات الفردية":
        subs_keyboard = [
            [InlineKeyboardButton("🎬 Netflix - نتفليكس", callback_data="sub_netflix")],
            [InlineKeyboardButton("📺 Shahid VIP - شاهد", callback_data="sub_shahid")],
            [InlineKeyboardButton("🎥 OSN+ - أوس إن", callback_data="sub_osn")],
            [InlineKeyboardButton("✨ Disney+ - ديزني", callback_data="sub_disney")],
            [InlineKeyboardButton("🌙 Noor Play - نور بلاي", callback_data="sub_noor")],
            [InlineKeyboardButton("⚽ TOD - تود (رياضة وترفيه)", callback_data="sub_tod")]
        ]
        await update.message.reply_text(
            "📦 **قسم الاشتراكات الفردية (الاشتراك الواحد):**\nاختر المنصة التي تناسبك:",
            reply_markup=InlineKeyboardMarkup(subs_keyboard),
            parse_mode="Markdown"
        )
        
    elif text == "🔥 عروض التوفير الكبرى":
        bundles_keyboard = [
            [InlineKeyboardButton("👥 عرض منصتين معاً (4 JD)", callback_data="bundle_init_2")],
            [InlineKeyboardButton("⭐ عرض الـ 3 منصات (5 JD)", callback_data="bundle_init_3")],
            [InlineKeyboardButton("💎 عرض الـ 4 منصات معاً (6 JD)", callback_data="bundle_init_4")]
        ]
        await update.message.reply_text(
            "🔥 **عروض التوفير الكبرى - 962ElStore**\n\n"
            "اجمع منصاتك المفضلة (نتفليكس، شاهد، ديزني، نور بلاي، أو إس إن) في باقة واحدة ووفر أكثر.. اختر نوع العرض:",
            reply_markup=InlineKeyboardMarkup(bundles_keyboard),
            parse_mode="Markdown"
        )
        
    elif text == "🔑 طلب كود":
        code_keyboard = [
            [InlineKeyboardButton("🔑 كود تسجيل دخول", callback_data="code_login_menu")],
            [InlineKeyboardButton("🏠 كود سكن (Netflix Household)", callback_data="code_household")]
        ]
        await update.message.reply_text(
            "🔑 **قسم طلب الأكواد:**\n\n"
            "يرجى اختيار نوع الكود الذي تحتاجه:",
            reply_markup=InlineKeyboardMarkup(code_keyboard),
            parse_mode="Markdown"
        )
        
    elif text == "🛠 التواصل مع الدعم":
        support_text = (
            f"🛠 **الدعم الفني وخدمة العملاء - 962ElStore**\n\n"
            f"إذا واجهتك أي مشكلة أو استفسار، يسعدنا تواصلك معنا مباشرة عبر حساب الدعم:\n"
            f"💬 {SUPPORT_USERNAME}\n\n"
            f"نحن في خدمتكم على مدار الساعة!"
        )
        await update.message.reply_text(support_text, parse_mode="Markdown")

# دالة لتوليد أزرار اختيار المنصات التفاعلية مع وضع الصح ✅
def get_selection_keyboard(selected_list, target_count):
    platforms = [
        ("netflix", "🎬 Netflix - نتفليكس"),
        ("shahid", "📺 Shahid VIP - شاهد"),
        ("osn", "🎥 OSN+ - أوس إن"),
        ("disney", "✨ Disney+ - ديزني"),
        ("noor", "🌙 Noor Play - نور بلاي")
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

# التعامل مع الأزرار التفاعلية وأزرار الرجوع
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_main":
        subs_keyboard = [
            [InlineKeyboardButton("🎬 Netflix - نتفليكس", callback_data="sub_netflix")],
            [InlineKeyboardButton("📺 Shahid VIP - شاهد", callback_data="sub_shahid")],
            [InlineKeyboardButton("🎥 OSN+ - أوس إن", callback_data="sub_osn")],
            [InlineKeyboardButton("✨ Disney+ - ديزني", callback_data="sub_disney")],
            [InlineKeyboardButton("🌙 Noor Play - نور بلاي", callback_data="sub_noor")],
            [InlineKeyboardButton("⚽ TOD - تود (رياضة وترفيه)", callback_data="sub_tod")]
        ]
        await query.message.edit_text(
            "📦 **قسم الاشتراكات الفردية (الاشتراك الواحد):**\nاختر المنصة التي تناسبك:",
            reply_markup=InlineKeyboardMarkup(subs_keyboard),
            parse_mode="Markdown"
        )

    elif data == "back_to_bundles":
        bundles_keyboard = [
            [InlineKeyboardButton("👥 عرض منصتين معاً (4 JD)", callback_data="bundle_init_2")],
            [InlineKeyboardButton("⭐ عرض الـ 3 منصات (5 JD)", callback_data="bundle_init_3")],
            [InlineKeyboardButton("💎 عرض الـ 4 منصات معاً (6 JD)", callback_data="bundle_init_4")]
        ]
        await query.message.edit_text(
            "🔥 **عروض التوفير الكبرى - 962ElStore**\n\n"
            "اجمع منصاتك المفضلة (نتفليكس، شاهد، ديزني، نور بلاي، أو إس إن) في باقة واحدة ووفر أكثر.. اختر نوع العرض:",
            reply_markup=InlineKeyboardMarkup(bundles_keyboard),
            parse_mode="Markdown"
        )

    # معالجة طلب الأكواد الرئيسية
    elif data == "code_login_menu":
        kb = [
            [InlineKeyboardButton("🎬 Netflix - نتفليكس", callback_data="login_code_netflix")],
            [InlineKeyboardButton("🎥 OSN+ - أوس إن", callback_data="login_code_osn")],
            [InlineKeyboardButton("✨ Disney+ - ديزني", callback_data="login_code_disney")],
            [InlineKeyboardButton("⬅️ رجوع", callback_data="code_back_main")]
        ]
        await query.message.edit_text(
            "🔑 **اختر المنصة التي تحتاج كود تسجيل دخول لها:**",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="Markdown"
        )

    elif data == "code_back_main":
        code_keyboard = [
            [InlineKeyboardButton("🔑 كود تسجيل دخول", callback_data="code_login_menu")],
            [InlineKeyboardButton("🏠 كود سكن (Netflix Household)", callback_data="code_household")]
        ]
        await query.message.edit_text(
            "🔑 **قسم طلب الأكواد:**\n\nيرجى اختيار نوع الكود الذي تحتاجه:",
            reply_markup=InlineKeyboardMarkup(code_keyboard),
            parse_mode="Markdown"
        )

    elif data.startswith("login_code_"):
        p_code = data.replace("login_code_", "")
        p_map = {
            "netflix": "Netflix - نتفليكس",
            "osn": "OSN+ - أوس إن",
            "disney": "Disney+ - ديزني"
        }
        platform_name = p_map.get(p_code, "المنصة")
        context.user_data['login_code_platform'] = platform_name
        context.user_data['waiting_for_login_code_email'] = True

        await query.message.edit_text(
            f"🔑 **طلب كود تسجيل دخول ({platform_name}):**\n\n"
            "الرجاء إرسال **البريد الإلكتروني (الإيميل)** أو معلومات الحساب هنا في المحادثة الآن ✍️",
            parse_mode="Markdown"
        )

    elif data == "code_household":
        await query.message.edit_text(
            "🏠 **قسم كود السكن (Household Code):**\n\nاختر المنصة المطلوبة:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎬 Netflix - نتفليكس", callback_data="hh_netflix")],
                [InlineKeyboardButton("⬅️ رجوع", callback_data="code_back_main")]
            ]),
            parse_mode="Markdown"
        )

    elif data == "hh_netflix":
        context.user_data['waiting_for_netflix_household_email'] = True
        await query.message.edit_text(
            "🎬 **طلب كود سكن نتفليكس:**\n\n"
            "الرجاء إرسال **البريد الإلكتروني (الإيميل)** الخاص بحساب نتفليكس هنا في المحادثة الآن ✍️",
            parse_mode="Markdown"
        )

    # 1. الاشتراكات الفردية
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
        await query.message.edit_text(f"{title}\n\nاختر المدة المطلوبة:", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    # 2. عروض التوفير المشتركة
    elif data.startswith("bundle_init_"):
        count = int(data.replace("bundle_init_", ""))
        context.user_data['bundle_target_count'] = count
        context.user_data['selected_platforms'] = []
        context.user_data['bundle_type'] = f"b{count}"

        text = (
            f"🎯 **اختر {count} منصات** تفضلها من القائمة أدناه:\n"
            f"(كلما تضغط على منصة سيتم تفعيلها بـ ✅، وعند إتمام اختيارك سيظهر زر المتابعة)"
        )
        kb = get_selection_keyboard([], count)
        await query.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")

    elif data.startswith("sel_"):
        p_key = data.replace("sel_", "")
        selected = context.user_data.get('selected_platforms', [])
        target = context.user_data.get('bundle_target_count', 2)

        if len(selected) < target and p_key not in selected:
            selected.append(p_key)
            context.user_data['selected_platforms'] = selected

        text = (
            f"🎯 **اختر {target} منصات** تفضلها من القائمة أدناه:\n"
            f"تم اختيار ({len(selected)} من {target})"
        )
        kb = get_selection_keyboard(selected, target)
        await query.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")

    elif data.startswith("unsel_"):
        p_key = data.replace("unsel_", "")
        selected = context.user_data.get('selected_platforms', [])
        target = context.user_data.get('bundle_target_count', 2)

        if p_key in selected:
            selected.remove(p_key)
            context.user_data['selected_platforms'] = selected

        text = (
            f"🎯 **اختر {target} منصات** تفضلها من القائمة أدناه:\n"
            f"تم اختيار ({len(selected)} من {target})"
        )
        kb = get_selection_keyboard(selected, target)
        await query.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")

    elif data == "proceed_to_duration":
        b_type = context.user_data.get('bundle_type', 'b2')
        
        if b_type == "b2":
            text = "👥 **عرض منصتين معاً (4 JD للشهر)**\nاختر المدة المطلوبة:"
            kb = [
                [InlineKeyboardButton("🟢 شهر واحد (4 JD)", callback_data="pkg_b2_1m")],
                [InlineKeyboardButton("🟢 3 أشهر (8 JD)", callback_data="pkg_b2_3m")],
                [InlineKeyboardButton("🟢 6 أشهر (15 JD)", callback_data="pkg_b2_6m")],
                [InlineKeyboardButton("🟢 سنة كاملة (25 JD)", callback_data="pkg_b2_1y")],
                [InlineKeyboardButton("⬅️ رجوع لتعديل المنصات", callback_data="bundle_init_2")]
            ]
        elif b_type == "b3":
            text = "⭐ **عرض الـ 3 منصات (5 JD للشهر)**\nاختر المدة المطلوبة:"
            kb = [
                [InlineKeyboardButton("🟢 شهر واحد (5 JD)", callback_data="pkg_b3_1m")],
                [InlineKeyboardButton("🟢 3 أشهر (10 JD)", callback_data="pkg_b3_3m")],
                [InlineKeyboardButton("🟢 6 أشهر (18 JD)", callback_data="pkg_b3_6m")],
                [InlineKeyboardButton("🟢 سنة كاملة (30 JD)", callback_data="pkg_b3_1y")],
                [InlineKeyboardButton("⬅️ رجوع لتعديل المنصات", callback_data="bundle_init_3")]
            ]
        else:
            text = "💎 **عرض الـ 4 منصات معاً - الباكج الشامل (6 JD للشهر)**\nاختر المدة المطلوبة:"
            kb = [
                [InlineKeyboardButton("🟢 شهر واحد (6 JD)", callback_data="pkg_b4_1m")],
                [InlineKeyboardButton("🟢 3 أشهر (12 JD)", callback_data="pkg_b4_3m")],
                [InlineKeyboardButton("🟢 6 أشهر (22 JD)", callback_data="pkg_b4_6m")],
                [InlineKeyboardButton("🟢 سنة كاملة (35 JD)", callback_data="pkg_b4_1y")],
                [InlineKeyboardButton("⬅️ رجوع لتعديل المنصات", callback_data="bundle_init_4")]
            ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    elif data.startswith("pkg_"):
        parts = data.split("_")
        sub_type = parts[1]
        duration = parts[2]

        context.user_data['current_sub'] = sub_type

        p_names = {
            "netflix": "Netflix 4K",
            "shahid": "Shahid VIP",
            "osn": "OSN+",
            "disney": "Disney+",
            "noor": "Noor Play",
            "tod": "TOD"
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
            prices = {"1m": "4 دنانير", "3m": "8 دنانير", "6m": "15 دينار", "1y": "25 دينار"}
            dur_map = {"1m": "شهر واحد", "3m": "3 أشهر", "6m": "6 أشهر", "1y": "سنة كاملة"}
        elif sub_type == "b3":
            prices = {"1m": "5 دنانير", "3m": "10 دنانير", "6m": "18 دينار", "1y": "30 دينار"}
            dur_map = {"1m": "شهر واحد", "3m": "3 أشهر", "6m": "6 أشهر", "1y": "سنة كاملة"}
        elif sub_type == "b4":
            prices = {"1m": "6 دنانير", "3m": "12 دينار", "6m": "22 دينار", "1y": "35 دينار"}
            dur_map = {"1m": "شهر واحد", "3m": "3 أشهر", "6m": "6 أشهر", "1y": "سنة كاملة"}
        elif sub_type == "tod":
            prices = {"1m": "6 دنانير", "3m": "9 دنانير"}
            dur_map = {"1m": "شهر واحد", "3m": "3 أشهر"}
        else:
            prices = {"1m": "2.5 دينار", "3m": "5 دنانير", "6m": "9 دنانير", "1y": "15 دينار"}
            dur_map = {"1m": "شهر واحد", "3m": "3 أشهر", "6m": "6 أشهر", "1y": "سنة كاملة"}

        price = prices.get(duration, "حسب الباقة")
        dur_text = dur_map.get(duration, "")

        context.user_data['sub_name_text'] = sub_name
        context.user_data['dur_text'] = dur_text
        context.user_data['price_text'] = price

        summary_text = (
            f"🛒 **ملخص طلب الاشتراك**\n\n"
            f"📌 **الخدمة / الباقة:** {sub_name}\n"
            f"⏳ **المدة:** {dur_text}\n"
            f"💵 **السعر الإجمالي:** {price}\n\n"
            f"اضغط على زر **'شراء'** أدناه لإتمام الدفع أو تراجع للخلف:"
        )
        
        if sub_type.startswith("b"):
            back_target = f"bundle_init_{sub_type.replace('b', '')}"
        else:
            back_target = f"sub_{sub_type}"

        buy_keyboard = [
            [InlineKeyboardButton("💳 شراء وإتمام الدفع", callback_data=f"buy_{sub_type}_{duration}")],
            [InlineKeyboardButton("⬅️ رجوع", callback_data=back_target)]
        ]
        await query.message.edit_text(summary_text, reply_markup=InlineKeyboardMarkup(buy_keyboard), parse_mode="Markdown")

    elif data.startswith("buy_"):
        parts = data.split("_")
        sub_type = parts[1]
        duration = parts[2]

        if sub_type == "b2":
            prices = {"1m": "4 دنانير", "3m": "8 دنانير", "6m": "15 دينار", "1y": "25 دينار"}
        elif sub_type == "b3":
            prices = {"1m": "5 دنانير", "3m": "10 دنانير", "6m": "18 دينار", "1y": "30 دينار"}
        elif sub_type == "b4":
            prices = {"1m": "6 دنانير", "3m": "12 دينار", "6m": "22 دينار", "1y": "35 دينار"}
        elif sub_type == "tod":
            prices = {"1m": "6 دنانير", "3m": "9 دنانير"}
        else:
            prices = {"1m": "2.5 دينار", "3m": "5 دنانير", "6m": "9 دنانير", "1y": "15 دينار"}

        price = prices.get(duration, "حسب الباقة")

        checkout_text = (
            f"💳 **معلومات الدفع عبر كليك (CliQ)**\n\n"
            f"{CLIQ_INFO}\n\n"
            f"💵 **المطلوب تحويله:** {price}\n\n"
            f"📸 **الخطوة الأخيرة:** قم بتحويل المبلغ، ثم **أرسل صورة (سكرين شوت) للإيصال** هنا في الشات وسنقوم بتفعيل باقتك فوراً!"
        )
        
        back_keyboard = [
            [InlineKeyboardButton("⬅️ رجوع", callback_data=f"pkg_{sub_type}_{duration}")]
        ]
        await query.message.edit_text(checkout_text, reply_markup=InlineKeyboardMarkup(back_keyboard), parse_mode="Markdown")
        context.user_data['waiting_for_receipt'] = True

# استقبال صور الإيصالات للأدمن مع تضمين أمر الرد السريع
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_receipt'):
        current_sub = context.user_data.get('current_sub', 'default')
        receipt_text = RECEIPT_INSTRUCTIONS.get(current_sub, RECEIPT_INSTRUCTIONS['default'])

        await update.message.reply_text(receipt_text, parse_mode="Markdown")

        user = update.effective_user
        sub_name = context.user_data.get('sub_name_text', 'باقة ترفيهية')
        dur_text = context.user_data.get('dur_text', 'غير محدد')
        price_text = context.user_data.get('price_text', 'غير محدد')

        admin_message = (
            f"🚨 **طلب اشتراك جديد تم دفع إيصاله (962ElStore)!**\n\n"
            f"👤 **اسم الزبون:** {user.full_name}\n"
            f"🔗 **يوزر الزبون:** @{user.username if user.username else 'لا يوجد'}\n"
            f"🆔 **معرف الزبون (ID):** `{user.id}`\n\n"
            f"📦 **الخدمة / الباقة:** {sub_name}\n"
            f"⏳ **المدة:** {dur_text}\n"
            f"💵 **السعر المدفوع:** {price_text}\n\n"
            f"💡 للرد عليه وتسليمه الحساب استخدم الأمر:\n`/reply {user.id} [معلومات الحساب هنا]`"
        )

        try:
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=update.message.photo[-1].file_id,
                caption=admin_message,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Error sending to admin: {e}")

        context.user_data['waiting_for_receipt'] = False
    else:
        await update.message.reply_text("يرجى استخدام الأزرار في القائمة للتنقل بسلاسة.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reply", admin_reply))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("962ElStore Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
