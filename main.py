import os
import logging
import threading
import time
import urllib.request
from decimal import Decimal, InvalidOperation
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import db as database

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
log = logging.getLogger("962ElStore")

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("أضف BOT_TOKEN في Render Environment")

ADMINS = [
    int(x.strip())
    for x in os.getenv("ADMIN_IDS", "7983029778,5884539860").split(",")
    if x.strip()
]

CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@El962Store")
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "@e962ElStore")
RENDER_URL = os.getenv(
    "RENDER_EXTERNAL_URL",
    "https://netflix-bot-8p4c.onrender.com"
)

RECEIPT_INSTRUCTIONS = {
    "default": (
        "✅ تم استلام صورة الإيصال بنجاح!\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول قريباً:\n"
        "⚠️ يرجى الالتزام بعدم فتح الحساب على أكثر من جهاز لضمان استمرار ضمانك!"
    ),
    "netflix": (
        "✅ تم استلام صورة الإيصال بنجاح!\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 سيتم تزويدك بمعلومات الحساب وتعليمات تسجيل الدخول:\n"
        "• يرجى إدخال البريد الإلكتروني، ثم الرجوع للقائمة الرئيسية لطلب الكود الخاص بتسجيل الدخول.\n"
        "⚠️ التسجيل متاح في جهاز واحد فقط."
    ),
    "shahid": (
        "✅ تم استلام صورة الإيصال بنجاح!\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 سيتم تزويدك ببيانات الدخول.\n"
        "• يرجى إدخال البريد الإلكتروني وكلمة السر لتسجيل الدخول.\n"
        "⚠️ الحساب مخصص لجهاز واحد فقط."
    ),
    "osn": (
        "✅ تم استلام صورة الإيصال بنجاح!\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 يرجى إدخال البريد الإلكتروني ثم الرجوع للقائمة الرئيسية لطلب كود تسجيل الدخول.\n"
        "⚠️ التسجيل متاح في جهاز واحد فقط."
    ),
    "disney": (
        "✅ تم استلام صورة الإيصال بنجاح!\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 يرجى استخدام رقم تلفون وكود لتسجيل الدخول.\n"
        "⚠️ الاشتراك مخصص لجهاز واحد فقط."
    ),
    "noor": (
        "✅ تم استلام صورة الإيصال بنجاح!\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 سيتم تزويدك ببيانات الدخول.\n"
        "• يرجى إدخال البريد الإلكتروني وكلمة السر لتسجيل الدخول.\n"
        "⚠️ الحساب مخصص لجهاز واحد فقط."
    ),
    "tod": (
        "✅ تم استلام صورة الإيصال بنجاح!\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 سيتم تزويدك بتفاصيل الدخول.\n"
        "• الحساب يعمل على جهازين FHD كحد أقصى."
    ),
    "chatgpt_shared": (
        "✅ تم استلام صورة الإيصال بنجاح!\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 سيتم تزويدك بمعلومات حساب ChatGPT المشترك."
    ),
    "chatgpt_private": (
        "✅ تم استلام صورة الإيصال بنجاح!\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 سيتم تزويدك بمعلومات حساب ChatGPT الخاص بك."
    ),
    "snap_gift": (
        "✅ تم استلام صورة الإيصال بنجاح!\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 سيتم تزويدك بتفاصيل إهداء سناب بلس قريباً:\n"
        "• يرجى إضافة حساب المتجر على سناب شات:\n"
        "https://snapchat.com/t/oqpRPOYx\n"
        "• يتم الإهداء عن طريق الإضافة فقط."
    ),
    "snap_private": (
        "✅ تم استلام صورة الإيصال بنجاح!\n"
        "شكراً لك لاختيارك متجر 962ElStore.\n\n"
        "📦 سيتم التواصل معك من قبل الإدارة لتفعيل سناب بلس للحفاظ على الخصوصيه."
    )
}

CLIQ_INFO = (
    "🔹 معلومات الدفع عبر كليك (CliQ):\n"
    "• الاسم المستعار: XM22\n"
    "• مزود الخدمة: البنك العربي الإسلامي الدولي\n"
    "• اسم المستلم: محمد بلال فايز بني احمد"
)

web_app = Flask(__name__)


@web_app.route("/")
def home():
    return "962ElStore Bot is active and running!"


def run_web():
    port = int(os.getenv("PORT", "8080"))
    web_app.run(
        host="0.0.0.0",
        port=port,
        use_reloader=False
    )


def self_ping():
    while True:
        try:
            urllib.request.urlopen(RENDER_URL, timeout=10).read()
            log.info("Self-ping successful")
        except Exception as exc:
            log.warning("Self-ping failed: %s", exc)

        time.sleep(240)


threading.Thread(target=run_web, daemon=True).start()

if os.getenv("ENABLE_SELF_PING", "false").lower() == "true":
    threading.Thread(target=self_ping, daemon=True).start()


def is_admin(user_id):
    return user_id in ADMINS


def main_menu():
    keyboard = [
        [
            KeyboardButton("🛒 الاشتراكات الفردية"),
            KeyboardButton("🔥 عروض التوفير الكبرى")
        ],
        [
            KeyboardButton("🔑 طلب كود"),
            KeyboardButton("⚠️ مشكلة في حسابي")
        ],
        [
            KeyboardButton("🛠 التواصل مع الدعم")
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


def join_markup():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📢 اشترك في القناة الآن",
                url="https://t.me/El962Store"
            )
        ],
        [
            InlineKeyboardButton(
                "✅ لقد اشتريت / اشتركت، تحقق الآن",
                callback_data="verify_subscription"
            )
        ]
    ])


async def is_member(bot, user_id):
    try:
        member = await bot.get_chat_member(
            CHANNEL_USERNAME,
            user_id
        )

        return member.status in (
            "member",
            "administrator",
            "creator"
        )

    except Exception:
        log.exception("Channel membership check failed")
        return False


async def ensure_member(update):
    user = update.effective_user

    if await is_member(update.get_bot(), user.id):
        return True

    if update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ يرجى الاشتراك في قناة المتجر أولاً ثم اضغط تحقق.",
            reply_markup=join_markup()
        )

    return False


async def notify_admins(
    context,
    text,
    photo=None,
    keyboard=None
):
    sent = {}

    for admin_id in ADMINS:
        try:
            if photo:
                msg = await context.bot.send_photo(
                    chat_id=admin_id,
                    photo=photo,
                    caption=text,
                    reply_markup=keyboard
                )
            else:
                msg = await context.bot.send_message(
                    chat_id=admin_id,
                    text=text,
                    reply_markup=keyboard
                )

            sent[admin_id] = msg.message_id

        except Exception:
            log.exception(
                "Could not notify admin %s",
                admin_id
            )

    return sent


def platform_name(code):
    names = {
        "netflix": "Netflix - نتفليكس",
        "shahid": "Shahid VIP - شاهد",
        "osn": "OSN+ - أوس إن",
        "disney": "Disney+ - ديزني",
        "noor": "Noor Play - نور بلاي",
        "tod": "TOD - تود",
        "snap_gift": "Snapchat+ إهداء",
        "snap_private": "Snapchat+ من داخل الحساب",
        "chatgpt_shared": "ChatGPT Plus مشترك",
        "chatgpt_private": "ChatGPT Plus خاص",
        "b2": "باقة منصتين",
        "b3": "باقة 3 منصات",
        "b4": "باقة 4 منصات"
    }

    return names.get(code, code)


def price_and_duration(sub_type, duration):
    prices = {
        "b2": {
            "1m": 5,
            "3m": 12,
            "6m": 22,
            "1y": 38
        },
        "b3": {
            "1m": 6,
            "3m": 15,
            "6m": 28,
            "1y": 48
        },
        "b4": {
            "1m": 8,
            "3m": 20,
            "6m": 36,
            "1y": 60
        },
        "tod": {
            "1m": 6,
            "3m": 9
        },
        "snap_gift": {
            "3m": 11,
            "6m": 22,
            "1y": 25
        },
        "snap_private": {
            "1m": 3,
            "1y": 16
        },
        "chatgpt_shared": {
            "1m": 2.5,
            "3m": 5,
            "6m": 9,
            "1y": 15
        },
        "chatgpt_private": {
            "1m": 8
        }
    }

    durations = {
        "1m": "شهر واحد",
        "3m": "3 أشهر",
        "6m": "6 أشهر",
        "1y": "سنة كاملة"
    }

    price = prices.get(sub_type, {}).get(duration)

    if price is None:
        price = {
            "1m": 2.5,
            "3m": 5,
            "6m": 9,
            "1y": 15
        }.get(duration)

    if price is None:
        raise ValueError("المدة أو السعر غير معروف")

    return Decimal(str(price)), durations[duration]


def parse_package(data, prefix):
    parts = data.split("_")

    if parts[0] != prefix:
        raise ValueError("طلب غير صحيح")

    if parts[1] in ("chatgpt", "snap"):
        sub_type = "_".join(parts[1:3])
        duration = parts[3]
    else:
        sub_type = parts[1]
        duration = parts[2]

    return sub_type, duration


def bundle_keyboard(selected, count):
    platforms = [
        ("netflix", "🎬 Netflix"),
        ("shahid", "📺 Shahid"),
        ("osn", "🎥 OSN+"),
        ("disney", "✨ Disney+"),
        ("noor", "🌙 Noor Play"),
        ("chatgpt", "🤖 ChatGPT Plus")
    ]

    rows = []

    for key, label in platforms:
        mark = "✅ " if key in selected else ""

        rows.append([
            InlineKeyboardButton(
                mark + label,
                callback_data=(
                    "unsel_" if key in selected else "sel_"
                ) + key
            )
        ])

    if len(selected) == count:
        rows.append([
            InlineKeyboardButton(
                "➡️ متابعة لاختيار المدة",
                callback_data="proceed_to_duration"
            )
        ])

    rows.append([
        InlineKeyboardButton(
            "⬅️ رجوع",
            callback_data="back_to_bundles"
        )
    ])

    return InlineKeyboardMarkup(rows)


def admin_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📊 الملخص المالي",
                callback_data="fin_report"
            ),
            InlineKeyboardButton(
                "💰 صافي الربح",
                callback_data="fin_profit"
            )
        ],
        [
            InlineKeyboardButton(
                "➕ تسجيل دخل",
                callback_data="fin_income"
            ),
            InlineKeyboardButton(
                "➖ تسجيل مصروف",
                callback_data="fin_expense"
            )
        ],
        [
            InlineKeyboardButton(
                "🏦 رأس المال",
                callback_data="fin_capital"
            ),
            InlineKeyboardButton(
                "🔄 تحويل بين المحافظ",
                callback_data="fin_transfer"
            )
        ],
        [
            InlineKeyboardButton(
                "📦 المخزون",
                callback_data="fin_stock"
            ),
            InlineKeyboardButton(
                "🧾 آخر العمليات",
                callback_data="fin_history"
            )
        ],
        [
            InlineKeyboardButton(
                "📋 جرد المحفظة",
                callback_data="fin_count"
            )
        ]
    ])


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user = update.effective_user

    if not await ensure_member(update):
        return

    database.save_customer(user)

    await update.message.reply_text(
        f"أهلاً بك في متجر 962ElStore!\n\n"
        f"رقمك التعريفي: {user.id}\n"
        f"الاسم: {user.full_name}\n\n"
        "اختر من القائمة:",
        reply_markup=main_menu()
    )


async def admin_panel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not is_admin(update.effective_user.id):
        return

    await update.effective_message.reply_text(
        "لوحة إدارة 962ElStore:",
        reply_markup=admin_keyboard()
    )


async def admin_reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "الاستخدام: /reply USER_ID نص الرسالة"
        )
        return

    try:
        target = int(context.args[0])

        await context.bot.send_message(
            target,
            "📬 رد جديد من إدارة 962ElStore:\n\n"
            + " ".join(context.args[1:])
        )

        await update.message.reply_text(
            "✅ تم إرسال الرد."
        )

    except Exception as exc:
        await update.message.reply_text(
            f"❌ تعذر إرسال الرد: {exc}"
        )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user = update.effective_user

    if not await ensure_member(update):
        return

    database.save_customer(user)

    text = (update.message.text or "").strip()

    action = context.user_data.get("finance_wait")

    if action:
        context.user_data.pop("finance_wait", None)

        if not is_admin(user.id):
            return

        try:
            fields = [
                x.strip()
                for x in text.split("|")
            ]

            if action == "income" and len(fields) >= 3:
                database.add_income(
                    fields[0],
                    fields[1],
                    fields[2],
                    user.id
                )

                await update.message.reply_text(
                    "✅ تم تسجيل الدخل."
                )

            elif action == "expense" and len(fields) >= 4:
                database.add_expense(
                    fields[1],
                    fields[0],
                    fields[2],
                    fields[3],
                    user.id
                )

                await update.message.reply_text(
                    "✅ تم تسجيل المصروف."
                )

            elif action == "capital" and len(fields) >= 4:
                database.add_capital(
                    fields[0],
                    fields[1],
                    fields[2],
                    fields[3],
                    user.id
                )

                await update.message.reply_text(
                    "✅ تم تسجيل حركة رأس المال."
                )

            elif action == "transfer" and len(fields) >= 4:
                database.transfer(
                    fields[0],
                    fields[1],
                    fields[2],
                    fields[3],
                    user.id
                )

                await update.message.reply_text(
                    "✅ تم التحويل بين المحافظ دون احتسابه ربحاً أو مصروفاً."
                )

            elif action == "count" and len(fields) >= 2:
                expected, difference = database.record_cash_count(
                    fields[0],
                    fields[1],
                    "|".join(fields[2:]),
                    user.id
                )

                await update.message.reply_text(
                    f"📋 نتيجة الجرد\n"
                    f"الرصيد الدفتري: {expected} د.أ\n"
                    f"الفرق: {difference} د.أ"
                )

            else:
                await update.message.reply_text(
                    "❌ صيغة الإدخال غير صحيحة. افتح /admin واتبع الصيغة الموضحة."
                )

        except Exception as exc:
            await update.message.reply_text(
                f"❌ لم تتم العملية: {exc}"
            )

        return

    if context.user_data.get("waiting_for_issue_email"):
        context.user_data["issue_email"] = text
        context.user_data["waiting_for_issue_email"] = False
        context.user_data["waiting_for_issue_description"] = True

        await update.message.reply_text(
            "📝 أرسل وصف المشكلة بالتفصيل، ويمكنك إرسال صورة."
        )
        return

    if context.user_data.get("waiting_for_issue_description"):
        context.user_data["waiting_for_issue_description"] = False

        msg = (
            f"⚠️ بلاغ مشكلة جديد\n"
            f"الاسم: {user.full_name}\n"
            f"المعرف: {user.id}\n"
            f"المنصة: {context.user_data.get('issue_platform', 'غير محدد')}\n"
            f"الحساب: {context.user_data.get('issue_email', 'غير محدد')}\n"
            f"الوصف:\n{text}"
        )

        await notify_admins(context, msg)

        await update.message.reply_text(
            "✅ تم إرسال بلاغك للدعم."
        )
        return

    if (
        context.user_data.get("waiting_for_login_code_email")
        or context.user_data.get("waiting_for_netflix_household_email")
    ):
        is_household = context.user_data.get(
            "waiting_for_netflix_household_email",
            False
        )

        context.user_data["waiting_for_login_code_email"] = False
        context.user_data["waiting_for_netflix_household_email"] = False

        label = (
            "كود سكن Netflix"
            if is_household
            else "كود تسجيل دخول " + context.user_data.get(
                "login_code_platform", ""
            )
        )

        msg = (
            f"🔑 طلب {label}\n"
            f"الاسم: {user.full_name}\n"
            f"المعرف: {user.id}\n"
            f"بيانات الحساب: {text}"
        )

        await notify_admins(context, msg)

        await update.message.reply_text(
            "✅ تم إرسال طلب الكود للإدارة."
        )
        return

    if text == "🛒 الاشتراكات الفردية":
        rows = [
            [("🎬 Netflix - نتفليكس", "sub_netflix")],
            [("📺 Shahid VIP - شاهد", "sub_shahid")],
            [("🎥 OSN+ - أوس إن", "sub_osn")],
            [("✨ Disney+ - ديزني", "sub_disney")],
            [("🌙 Noor Play - نور بلاي", "sub_noor")],
            [("⚽ TOD - تود", "sub_tod")],
            [("👻 Snapchat+ - سناب بلس", "sub_snapchat_menu")],
            [("🤖 ChatGPT Plus - شات جي بي تي", "sub_chatgpt_menu")]
        ]

        await update.message.reply_text(
            "📦 اختر المنصة:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(a, callback_data=b)
                ]
                for row in rows
                for a, b in row
            ])
        )

    elif text == "🔥 عروض التوفير الكبرى":
        await update.message.reply_text(
            "🔥 عروض التوفير الكبرى:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "👥 منصتان (5 JD)",
                        callback_data="bundle_init_2"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⭐ 3 منصات (6 JD)",
                        callback_data="bundle_init_3"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "💎 4 منصات (8 JD)",
                        callback_data="bundle_init_4"
                    )
                ]
            ])
        )

    elif text == "🔑 طلب كود":
        await update.message.reply_text(
            "اختر نوع الكود:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔑 كود تسجيل دخول",
                        callback_data="code_login_menu"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🏠 كود سكن Netflix",
                        callback_data="code_household"
                    )
                ]
            ])
        )

    elif text == "⚠️ مشكلة في حسابي":
        codes = [
            "netflix",
            "shahid",
            "osn",
            "disney",
            "noor",
            "tod",
            "snapchat",
            "chatgpt"
        ]

        await update.message.reply_text(
            "اختر المنصة التي تواجه مشكلة فيها:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        platform_name(x),
                        callback_data="issue_" + x
                    )
                ]
                for x in codes
            ])
        )

    elif text == "🛠 التواصل مع الدعم":
        await update.message.reply_text(
            "للتواصل مع الدعم الفني:\n" + SUPPORT_USERNAME
        )


async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    q = update.callback_query
    user = q.from_user
    data = q.data

    await q.answer()

    if data == "verify_subscription":
        if await is_member(context.bot, user.id):
            database.save_customer(user)

            await q.message.edit_text(
                "✅ تم التحقق من اشتراكك."
            )

            await q.message.reply_text(
                "القائمة الرئيسية:",
                reply_markup=main_menu()
            )

        else:
            await q.message.reply_text(
                "❌ لم تشترك بالقناة بعد. اشترك ثم أعد التحقق."
            )

        return

    if data.startswith("claim_"):
        if not is_admin(user.id):
            await q.message.reply_text(
                "هذا الزر للإدارة فقط."
            )
            return

        try:
            order_id = int(data.split("_", 1)[1])

            ok = database.claim_order(
                order_id,
                user.id
            )

            await q.message.reply_text(
                "✅ تم استلام الطلب."
                if ok
                else "⚠️ الطلب مستلم مسبقاً أو غير موجود."
            )

            if ok:
                await q.message.edit_reply_markup(
                    reply_markup=None
                )

                await q.message.reply_text(
                    f"تم استلام الطلب رقم {order_id} بواسطة {user.full_name}"
                )

        except Exception as exc:
            await q.message.reply_text(str(exc))

        return

    if data.startswith("issue_"):
        code = data.replace("issue_", "", 1)

        context.user_data["issue_platform"] = platform_name(code)
        context.user_data["waiting_for_issue_email"] = True

        await q.message.edit_text(
            "أرسل البريد الإلكتروني أو اسم الحساب المرتبط بالمشكلة."
        )

        return

    if data == "back_to_main":
        await q.message.edit_text(
            "اختر المنصة:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        platform_name(x),
                        callback_data="sub_" + x
                    )
                ]
                for x in [
                    "netflix",
                    "shahid",
                    "osn",
                    "disney",
                    "noor",
                    "tod"
                ]
            ])
        )

        return

    if data == "back_to_bundles":
        await q.message.edit_text(
            "اختر الباقة:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "منصتان",
                        callback_data="bundle_init_2"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "3 منصات",
                        callback_data="bundle_init_3"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "4 منصات",
                        callback_data="bundle_init_4"
                    )
                ]
            ])
        )

        return

    if data == "code_login_menu":
        await q.message.edit_text(
            "اختر المنصة:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        platform_name(x),
                        callback_data="login_code_" + x
                    )
                ]
                for x in [
                    "netflix",
                    "osn",
                    "disney",
                    "chatgpt"
                ]
            ])
        )

        return

    if data == "code_household":
        await q.message.edit_text(
            "طلب كود سكن Netflix. اضغط للمتابعة:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "Netflix Household",
                        callback_data="hh_netflix"
                    )
                ]
            ])
        )

        return

    if data == "hh_netflix":
        context.user_data[
            "waiting_for_netflix_household_email"
        ] = True

        await q.message.edit_text(
            "أرسل البريد الإلكتروني لحساب Netflix."
        )

        return

    if data.startswith("login_code_"):
        context.user_data["login_code_platform"] = platform_name(
            data.replace("login_code_", "")
        )

        context.user_data[
            "waiting_for_login_code_email"
        ] = True

        await q.message.edit_text(
            "أرسل البريد الإلكتروني أو معلومات الحساب لطلب الكود."
        )

        return

    if data == "sub_snapchat_menu":
        await q.message.edit_text(
            "اختر نوع Snapchat+:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "إهداء",
                        callback_data="snap_gift_menu"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "من داخل الحساب",
                        callback_data="snap_private_menu"
                    )
                ]
            ])
        )

        return

    if data == "snap_gift_menu":
        choices = [
            ("3 أشهر (11 JD)", "pkg_snap_gift_3m"),
            ("6 أشهر (22 JD)", "pkg_snap_gift_6m"),
            ("سنة (25 JD)", "pkg_snap_gift_1y")
        ]

        await q.message.edit_text(
            "Snapchat+ إهداء:\n"
            "• يرجى إضافة حساب المتجر على سناب شات:\n"
            "https://snapchat.com/t/oqpRPOYx\n"
            "• اختر المدة المطلوبة:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(a, callback_data=b)
                ]
                for a, b in choices
            ]),
            disable_web_page_preview=True
        )

        return

    if data == "snap_private_menu":
        choices = [
            ("شهر (3 JD)", "pkg_snap_private_1m"),
            ("سنة (16 JD)", "pkg_snap_private_1y")
        ]

        await q.message.edit_text(
            "Snapchat+ من داخل الحساب:\n"
            "• سيتم التواصل معك من قبل الإدارة لتزويدك بمعلومات تسجيل الدخول للحفاظ على الخصوصيه.\n"
            "• اختر المدة المطلوبة:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(a, callback_data=b)
                ]
                for a, b in choices
            ])
        )

        return

    if data == "sub_chatgpt_menu":
        await q.message.edit_text(
            "اختر نوع ChatGPT:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "حساب مشترك",
                        callback_data="sub_chatgpt_shared_menu"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "حساب خاص (8 JD)",
                        callback_data="pkg_chatgpt_private_1m"
                    )
                ]
            ])
        )

        return

    if data == "sub_chatgpt_shared_menu":
        choices = [
            ("شهر 2.5 JD", "pkg_chatgpt_shared_1m"),
            ("3 أشهر 5 JD", "pkg_chatgpt_shared_3m"),
            ("6 أشهر 9 JD", "pkg_chatgpt_shared_6m"),
            ("سنة 15 JD", "pkg_chatgpt_shared_1y")
        ]

        await q.message.edit_text(
            "ChatGPT مشترك:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(a, callback_data=b)
                ]
                for a, b in choices
            ])
        )

        return

    if data.startswith("sub_"):
        code = data.replace("sub_", "")

        if code not in (
            "netflix",
            "shahid",
            "osn",
            "disney",
            "noor",
            "tod"
        ):
            return

        durations = [
            ("شهر واحد (2.5 JD)", "1m"),
            ("3 أشهر (5 JD)", "3m"),
            ("6 أشهر (9 JD)", "6m"),
            ("سنة (15 JD)", "1y")
        ]

        if code == "tod":
            durations = [
                ("شهر (6 JD)", "1m"),
                ("3 أشهر (9 JD)", "3m")
            ]

        await q.message.edit_text(
            platform_name(code) + " - اختر المدة:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        label,
                        callback_data=f"pkg_{code}_{dur}"
                    )
                ]
                for label, dur in durations
            ])
        )

        return

    if data.startswith("bundle_init_"):
        count = int(data.rsplit("_", 1)[1])

        context.user_data["bundle_target_count"] = count
        context.user_data["selected_platforms"] = []
        context.user_data["bundle_type"] = "b" + str(count)

        await q.message.edit_text(
            f"اختر {count} منصات:",
            reply_markup=bundle_keyboard([], count)
        )

        return

    if data.startswith("sel_") or data.startswith("unsel_"):
        key = data.split("_", 1)[1]

        selected = context.user_data.get(
            "selected_platforms",
            []
        )

        target = context.user_data.get(
            "bundle_target_count",
            2
        )

        if data.startswith("sel_"):
            if key not in selected and len(selected) < target:
                selected.append(key)

        elif key in selected:
            selected.remove(key)

        context.user_data["selected_platforms"] = selected

        await q.message.edit_reply_markup(
            reply_markup=bundle_keyboard(selected, target)
        )

        return

    if data == "proceed_to_duration":
        count = context.user_data.get(
            "bundle_target_count",
            2
        )

        selected = context.user_data.get(
            "selected_platforms",
            []
        )

        if len(selected) != count:
            await q.message.reply_text(
                "أكمل اختيار المنصات أولاً."
            )
            return

        b = "b" + str(count)

        context.user_data["bundle_type"] = b

        durations = {
            "b2": [
                ("شهر 5 JD", "1m"),
                ("3 أشهر 12 JD", "3m"),
                ("6 أشهر 22 JD", "6m"),
                ("سنة 38 JD", "1y")
            ],
            "b3": [
                ("شهر 6 JD", "1m"),
                ("3 أشهر 15 JD", "3m"),
                ("6 أشهر 28 JD", "6m"),
                ("سنة 48 JD", "1y")
            ],
            "b4": [
                ("شهر 8 JD", "1m"),
                ("3 أشهر 20 JD", "3m"),
                ("6 أشهر 36 JD", "6m"),
                ("سنة 60 JD", "1y")
            ]
        }

        await q.message.edit_text(
            "اختر مدة الباقة:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        a,
                        callback_data=f"pkg_{b}_{d}"
                    )
                ]
                for a, d in durations[b]
            ])
        )

        return

    if data.startswith("pkg_"):
        sub_type, duration = parse_package(data, "pkg")

        price, dur_text = price_and_duration(
            sub_type,
            duration
        )

        if sub_type.startswith("b"):
            selected = context.user_data.get(
                "selected_platforms",
                []
            )

            if len(selected) != int(sub_type[1:]):
                await q.message.reply_text(
                    "يرجى اختيار المنصات من جديد."
                )
                return

            name = (
                platform_name(sub_type)
                + " ("
                + " + ".join(
                    platform_name(x)
                    for x in selected
                )
                + ")"
            )

        else:
            name = platform_name(sub_type)

        context.user_data.update({
            "current_sub": sub_type,
            "current_duration": duration,
            "sub_name_text": name,
            "dur_text": dur_text,
            "price_value": str(price),
            "price_text": f"{price} دينار"
        })

        await q.message.edit_text(
            f"🛒 ملخص طلب الاشتراك\n\n"
            f"الخدمة: {name}\n"
            f"المدة: {dur_text}\n"
            f"السعر: {price} دينار\n\n"
            "اضغط شراء لإتمام الدفع.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "💳 شراء وإتمام الدفع",
                        callback_data=f"buy_{sub_type}_{duration}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⬅️ رجوع",
                        callback_data="back_to_main"
                    )
                ]
            ])
        )

        return

    if data.startswith("buy_"):
        sub_type, duration = parse_package(data, "buy")

        price, dur_text = price_and_duration(
            sub_type,
            duration
        )

        context.user_data.update({
            "current_sub": sub_type,
            "current_duration": duration,
            "price_value": str(price),
            "price_text": f"{price} دينار",
            "dur_text": dur_text,
            "waiting_for_receipt": True
        })

        await q.message.edit_text(
            "💳 معلومات الدفع عبر كليك (CliQ)\n\n"
            + CLIQ_INFO
            + f"\n\nالمبلغ المطلوب: {price} دينار\n\n"
            "بعد التحويل أرسل صورة الإيصال هنا.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⬅️ رجوع",
                        callback_data=f"pkg_{sub_type}_{duration}"
                    )
                ]
            ])
        )

        return

    if data.startswith("fin_"):
        if not is_admin(user.id):
            await q.message.reply_text(
                "هذه اللوحة للإدارة فقط."
            )
            return

        if data == "fin_report":
            rows = database.financial_report()

            labels = {
                "owner": "أموال صاحب المتجر",
                "shared": "رأس المال المشترك",
                "operating": "الأموال التشغيلية"
            }

            body = "📊 أرصدة المحافظ\n\n"

            body += "\n".join(
                f"{labels.get(r['fund_source'], r['fund_source'])}: "
                f"{r['balance']} د.أ"
                for r in rows
            )

            await q.message.reply_text(body)

        elif data == "fin_profit":
            r = database.profit_report()

            await q.message.reply_text(
                f"📈 تقرير الأرباح\n"
                f"المبيعات: {r['sales']} د.أ\n"
                f"تكلفة الاشتراكات: {r['costs']} د.أ\n"
                f"المصاريف: {r['expenses']} د.أ\n"
                f"صافي الربح: {r['net_profit']} د.أ"
            )

        elif data == "fin_history":
            rows = database.recent_transactions()

            if not rows:
                await q.message.reply_text(
                    "لا توجد عمليات مسجلة."
                )

            else:
                await q.message.reply_text(
                    "\n".join(
                        f"#{r['id']} | {r['transaction_type']} | "
                        f"{r['fund_source']} | {r['amount']} د.أ\n"
                        f"{r['description']}"
                        for r in rows
                    )
                )

        elif data == "fin_stock":
            rows = database.inventory_list()

            if not rows:
                await q.message.reply_text(
                    "المخزون فارغ."
                )

            else:
                await q.message.reply_text(
                    "\n".join(
                        f"#{r['id']} {r['item_name']}: "
                        f"{r['quantity']} | قيمة {r['stock_value']} د.أ"
                        for r in rows
                    )
                )

            await q.message.reply_text(
                "لإضافة مخزون أرسل:\n"
                "/stock اسم الصنف | الكمية | تكلفة الوحدة | مصدر الأموال"
            )

        else:
            prompts = {
                "fin_income": (
                    "income",
                    "أرسل: المبلغ | owner أو shared أو operating | الوصف"
                ),
                "fin_expense": (
                    "expense",
                    "أرسل: المبلغ | التصنيف | owner أو shared أو operating | الوصف"
                ),
                "fin_capital": (
                    "capital",
                    "أرسل: المبلغ | owner أو shared أو operating | in أو out | الوصف"
                ),
                "fin_transfer": (
                    "transfer",
                    "أرسل: المبلغ | المحفظة المصدر | المحفظة المستقبلة | الوصف"
                ),
                "fin_count": (
                    "count",
                    "أرسل: المحفظة (owner/shared/operating) | الرصيد الفعلي | ملاحظات"
                )
            }

            action, prompt = prompts[data]

            context.user_data["finance_wait"] = action

            await q.message.reply_text(prompt)

        return


async def handle_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user = update.effective_user

    if not await ensure_member(update):
        return

    photo_id = update.message.photo[-1].file_id

    if context.user_data.get("waiting_for_issue_description"):
        context.user_data["waiting_for_issue_description"] = False

        await notify_admins(
            context,
            f"⚠️ بلاغ مشكلة مع صورة\n"
            f"الاسم: {user.full_name}\n"
            f"المعرف: {user.id}\n"
            f"المنصة: {context.user_data.get('issue_platform', 'غير محدد')}\n"
            f"الحساب: {context.user_data.get('issue_email', 'غير محدد')}",
            photo=photo_id
        )

        await update.message.reply_text(
            "✅ تم إرسال البلاغ والصورة للدعم."
        )

        return

    if context.user_data.get("waiting_for_receipt"):
        sub = context.user_data.get("current_sub", "")
        
        # التأكد من توفر السعر، وإلا يتم تعويض قيمة افتراضية لتجنب التعطل
        raw_price = context.user_data.get("price_value", "0")
        try:
            price = Decimal(str(raw_price))
        except (InvalidOperation, TypeError):
            price = Decimal("0")

        name = context.user_data.get(
            "sub_name_text",
            platform_name(sub) if sub else "خدمة رقمية"
        )

        dur_text = context.user_data.get("dur_text", "غير محددة")

        try:
            order_id = database.create_order(
                user.id,
                name,
                dur_text,
                price,
                photo_id
            )

        except Exception as exc:
            log.exception("Could not save order due to DB error: %s", exc)

            await update.message.reply_text(
                f"❌ تعذر تسجيل الطلب حالياً بسبب خطأ تقني: {exc}\n"
                "يرجى محاولة اختيار الخدمة من جديد أو تواصل مع الدعم."
            )

            return

        context.user_data["waiting_for_receipt"] = False

        await update.message.reply_text(
            RECEIPT_INSTRUCTIONS.get(
                sub,
                RECEIPT_INSTRUCTIONS["default"]
            )
            + "\n\nرقم طلبك: "
            + str(order_id)
            + "\nستراجع الإدارة الحوالة وتتواصل معك."
        )

        await notify_admins(
            context,
            f"🚨 طلب اشتراك جديد #{order_id}\n"
            f"الاسم: {user.full_name}\n"
            f"المعرف: {user.id}\n"
            f"الخدمة: {name}\n"
            f"المدة: {dur_text}\n"
            f"السعر: {price} د.أ\n"
            f"الحالة: بانتظار الاستلام\n\n"
            f"بعد التحقق من الحوالة استخدم:\n"
            f"/complete {order_id} COST INCOME_SOURCE COST_SOURCE\n"
            f"مثال: /complete {order_id} 1.50 operating shared",
            photo=photo_id,
            keyboard=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🙋 استلام الطلب",
                        callback_data=f"claim_{order_id}"
                    )
                ]
            ])
        )

    else:
        await update.message.reply_text(
            "يرجى استخدام أزرار القائمة."
        )



async def stock_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not is_admin(update.effective_user.id):
        return

    raw = " ".join(context.args)

    try:
        name, qty, cost, source = [
            x.strip()
            for x in raw.split("|")
        ]

        database.add_stock(
            name,
            qty,
            cost,
            update.effective_user.id,
            source
        )

        await update.message.reply_text(
            "✅ تمت إضافة المخزون."
        )

    except Exception as exc:
        await update.message.reply_text(
            "الصيغة الصحيحة:\n"
            "/stock اسم الصنف | الكمية | تكلفة الوحدة | owner/shared/operating\n\n"
            f"{exc}"
        )


async def complete_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) != 4:
        await update.message.reply_text(
            "الصيغة:\n"
            "/complete ORDER_ID COST INCOME_SOURCE COST_SOURCE\n\n"
            "مثال:\n"
            "/complete 12 1.50 operating shared"
        )
        return

    try:
        order_id = int(context.args[0])
        cost = context.args[1]
        income_source = context.args[2]
        cost_source = context.args[3]

        database.complete_order(
            order_id,
            update.effective_user.id,
            cost,
            income_source,
            cost_source
        )

        await update.message.reply_text(
            "✅ تم إغلاق الطلب وتسجيل المبيعات والتكلفة."
        )

    except Exception as exc:
        await update.message.reply_text(
            f"❌ {exc}"
        )


async def admin_help(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not is_admin(update.effective_user.id):
        return

    await update.message.reply_text(
        "أوامر الإدارة:\n"
        "/admin - لوحة الإدارة\n"
        "/reply USER_ID نص الرد\n"
        "/stock اسم الصنف | الكمية | تكلفة الوحدة | owner/shared/operating\n"
        "/complete ORDER_ID COST INCOME_SOURCE COST_SOURCE\n\n"
        "مهم: لا تغلق الطلب إلا بعد التحقق من الحوالة."
    )


def main():
    database.init_db()

    log.info("962ElStore PostgreSQL connected")

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("reply", admin_reply)
    )

    app.add_handler(
        CommandHandler("admin", admin_panel)
    )

    app.add_handler(
        CommandHandler("helpadmin", admin_help)
    )

    app.add_handler(
        CommandHandler("stock", stock_command)
    )

    app.add_handler(
        CommandHandler("complete", complete_command)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            handle_photo
        )
    )

    app.run_polling(
        drop_pending_updates=False
    )


if __name__ == "__main__":
    main()
