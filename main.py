import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties

# سحب التوكن أماناً من إعدادات البيئة في Render
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [123456789]  # ضع آيدي الأدمز هنا
CHANNEL_USERNAME = "@El962Store"  # قناة المتجر

# بيانات الدفع عبر كليك
CLIQ_INFO = (
    "💳 **معلومات الدفع عبر كليك (CliQ):**\n"
    "• **الاسم المستعار:** `XM22`\n"
    "• **البنك:** البنك الإسلامي العربي (International Islamic Arab Bank)\n"
    "• **اسم المستلم:** محمد بلال فايز بني أحمد\n\n"
    "📷 **بعد التحويل، يرجى إرسال صورة الإيصال (الوصل) هنا في المحادثة.**"
)

# حالات FSM (الخطوات)
class OrderState(StatesGroup):
    waiting_for_receipt = State()

class IssueState(StatesGroup):
    waiting_for_email = State()
    waiting_for_description = State()

class CodeState(StatesGroup):
    waiting_for_code_info = State()

# تهيئة البوت
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# ==================== الأزرار والقوائم الرئيسية ====================
def main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎬 الاشتراكات الفردية", callback_data="cat_individual")],
        [InlineKeyboardButton(text="🔥 عرض التوفير (الباقات الكبرى)", callback_data="cat_bundles")],
        [InlineKeyboardButton(text="🔑 طلب كود (دخول / سكن / 2FA)", callback_data="cat_codes")],
        [InlineKeyboardButton(text="⚠️ مشاكل الحساب", callback_data="cat_issues")],
        [InlineKeyboardButton(text="📞 دعم فني", url="https://t.me/El962Store")]
    ])

# ==================== القائمة الرئيسية /start ====================
@router.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = (
        "مرحباً بك في متجر **962ElStore** 🛍️\n\n"
        "متجرك الأول للاشتراكات الرقمية والخدمات الترفيهية بأفضل الأسعار.\n"
        "يرجى اختيار ما تحتاجه من القائمة أدناه:"
    )
    await message.answer(welcome_text, reply_markup=main_menu_keyboard())

# أمر الرد المباشر للإدارة على الزبائن عبر البوت
@router.message(Command("reply"))
async def admin_reply_user(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply("⚠️ الاستخدام الصحيح:\n`/reply <user_id> <الرسالة>`")
        return
    
    target_user_id = int(args[1])
    reply_text = args[2]
    
    try:
        await bot.send_message(
            target_user_id,
            f"📥 **رد من إدارة متجر 962ElStore:**\n\n{reply_text}"
        )
        await message.reply("✅ تم إرسال الرد إلى الزبون بنجاح عبر البوت.")
    except Exception as e:
        await message.reply(f"❌ تعذر إرسال الرد للزبون: {e}")

# زر الرجوع للقائمة الرئيسية
@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "القائمة الرئيسية لمتجر **962ElStore** 🛍️:",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()

# ==================== 1. قسم الاشتراكات الفردية ====================
@router.callback_query(F.data == "cat_individual")
async def individual_subscriptions(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎬 Netflix", callback_data="sub_netflix"),
         InlineKeyboardButton(text="📺 Shahid VIP", callback_data="sub_shahid")],
        [InlineKeyboardButton(text="🟣 OSN+", callback_data="sub_osn"),
         InlineKeyboardButton(text="🟢 Noor Play", callback_data="sub_noor")],
        [InlineKeyboardButton(text="💫 Disney+", callback_data="sub_disney"),
         InlineKeyboardButton(text="⚽ TOD", callback_data="sub_tod")],
        [InlineKeyboardButton(text="💬 ChatGPT Plus", callback_data="sub_chatgpt"),
         InlineKeyboardButton(text="👻 Snapchat+", callback_data="sub_snap")],
        [InlineKeyboardButton(text="▶️ YouTube Premium", callback_data="sub_youtube")],
        [InlineKeyboardButton(text="⬅️ رجوع للقائمة الرئيسية", callback_data="main_menu")]
    ])
    await callback.message.edit_text("اختر المنصة المطلوبة للاشتراك الفردي:", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("sub_"))
async def handle_sub_selection(callback: CallbackQuery):
    sub_type = callback.data.split("_")[1]
    
    if sub_type in ["netflix", "shahid", "osn", "noor", "disney", "chatgpt"]:
        durations = [
            ("شهر واحد - 2.5 دينار", f"price_{sub_type}_1m"),
            ("3 أشهر - 5 دنانير", f"price_{sub_type}_3m"),
            ("6 أشهر - 9 دنانير", f"price_{sub_type}_6m"),
            ("سنة كاملة - 15 دينار", f"price_{sub_type}_1y"),
        ]
    elif sub_type == "tod":
        durations = [
            ("شهر واحد - 6 دنانير", f"price_tod_1m"),
            ("3 أشهر - 11 دينار", f"price_tod_3m"),
        ]
    elif sub_type == "snap":
        durations = [
            ("إهداء (3 أشهر) - 11 دينار", f"price_snap_gift_3m"),
            ("إهداء (6 أشهر) - 19 دينار", f"price_snap_gift_6m"),
            ("إهداء (سنة) - 27 دينار", f"price_snap_gift_1y"),
            ("من داخل الحساب (شهر) - 3 دنانير", f"price_snap_acc_1m"),
            ("من داخل الحساب (سنة) - 16 دينار", f"price_snap_acc_1y"),
        ]
    elif sub_type == "youtube":
        durations = [
            ("الشهر - 3 دنانير أردني", "price_youtube_1m"),
            ("3 أشهر - 7 دنانير أردني", "price_youtube_3m"),
            ("6 أشهر - 14 دينار أردني", "price_youtube_6m"),
            ("السنة - 19 دينار أردني", "price_youtube_1y"),
        ]
    
    keyboard_buttons = [[InlineKeyboardButton(text=text, callback_data=cb)] for text, cb in durations]
    keyboard_buttons.append([InlineKeyboardButton(text="⬅️ رجوع", callback_data="cat_individual")])
    
    await callback.message.edit_text(
        f"اختر المدة المطلوبة لـ **{sub_type.upper()}**:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("price_"))
async def show_price_and_details(callback: CallbackQuery):
    parts = callback.data.split("_")
    sub_type = parts[1]
    duration = parts[-1]
    
    details = ""
    is_long_term = duration in ["3m", "6m", "1y"] and sub_type in ["netflix", "osn"]
    
    if sub_type == "netflix":
        details = (
            "🎬 **تفاصيل اشتراك Netflix:**\n"
            "• الجودة: 4K Ultra HD\n"
            "• نوع الحساب: بروفايل خاص بك وحدك\n"
            "• عدد الأجهزة: جهاز واحد فقط (شاشة، تلفون، أو إيباد)\n"
        )
    elif sub_type == "osn":
        details = "🟣 **تفاصيل اشتراك OSN+:**\n• بروفايل خاص - جهاز واحد فقط\n"
    elif sub_type == "shahid":
        details = "📺 **تفاصيل اشتراك Shahid VIP:**\n• يتم تزويدك بـ (إيميل وكلمة سر) مباشرة.\n"
    elif sub_type == "noor":
        details = "🟢 **تفاصيل اشتراك Noor Play:**\n• يتم تزويدك بـ (إيميل وكلمة سر).\n"
    elif sub_type == "disney":
        details = "💫 **تفاصيل اشتراك Disney+:**\n• يتم تزويدك بـ (رقم تلفون وكود).\n"
    elif sub_type == "tod":
        details = "⚽ **تفاصيل اشتراك TOD:**\n• يتم تزويدك بـ (رقم تلفون وباسورد).\n"
    elif sub_type == "chatgpt":
        details = "💬 **تفاصيل اشتراك ChatGPT Plus:**\n• يتم تزويدك بـ (إيميل وكلمة سر) مع 2FA.\n"
    elif sub_type == "snap":
        details = "👻 **تفاصيل اشتراك Snapchat+:**\n• متوفر بنظام الإهداء أو من داخل الحساب.\n"
    elif sub_type == "youtube":
        details = (
            "▶️ **تفاصيل اشتراك YouTube Premium:**\n"
            "• ودّع الإعلانات للأبد وبدون أي إزعاج[span_4](start_span)[span_4](end_span)!\n"
            "• تشغيل الفيديوهات والموسيقى في الخلفية وفي الشاشة المقفلة[span_5](start_span)[span_5](end_span).\n"
            "• تنزيل المحتوى لمشاهدته بدون إنترنت[span_6](start_span)[span_6](end_span).\n"
            "• اشتراك مجاني في تطبيق YouTube Music[span_7](start_span)[span_7](end_span).\n"
            "• **طريقة التفعيل:** دعوة رسمية ومضمونة 100% على إيميلك الشخصي[span_8](start_span)[span_8](end_span)!\n"
        )

    long_term_warning = (
        "\n⚠️ **تنبيه هام:** الاشتراكات الطويلة (3 أشهر، 6 أشهر، والسنة) "
        "يتم تزويد العميل فيها **كل شهر بحساب مختلف وليس نفس الحساب** لضمان الاستمرارية."
        if is_long_term else ""
    )

    text_to_show = f"📋 **ملخص الطلب:**\n\n{details}{long_term_warning}\n\n👉 اضغط أدناه لإتمام عملية الدفع والشراء."
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 شراء وإتمام الدفع", callback_data=f"pay_{sub_type}_{duration}")],
        [InlineKeyboardButton(text="⬅️ رجوع", callback_data=f"sub_{sub_type}")]
    ])
    
    await callback.message.edit_text(text_to_show, reply_markup=keyboard)
    await callback.answer()

# ==================== 2. قسم عروض التوفير (الباقات الكبرى) ====================
@router.callback_query(F.data == "cat_bundles")
async def bundles_menu(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 اشتراكين معاً", callback_data="bundle_2")],
        [InlineKeyboardButton(text="👨‍👩‍👦 ثلاثة اشتراكات معاً", callback_data="bundle_3")],
        [InlineKeyboardButton(text="👨‍👩‍👧‍👦 أربعة اشتراكات معاً", callback_data="bundle_4")],
        [InlineKeyboardButton(text="⬅️ رجوع للقائمة الرئيسية", callback_data="main_menu")]
    ])
    text = (
        "🔥 **عروض التوفير الكبرى:**\n"
        "التطبيقات المشمولة: نتفليكس، شاهد، OSN، ديزني، نور بلاي، وشات جي بي تي.\n\n"
        "اختر عدد الاشتراكات المطلوبة:"
    )
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("bundle_"))
async def bundle_durations(callback: CallbackQuery):
    b_count = callback.data.split("_")[1]
    
    if b_count == "2":
        durations = [
            ("شهر - 4 دنانير", "pay_bundle_2_1m"),
            ("3 أشهر - 8 دنانير", "pay_bundle_2_3m"),
            ("6 أشهر - 15 دينار", "pay_bundle_2_6m"),
            ("سنة - 25 دينار", "pay_bundle_2_1y"),
        ]
    elif b_count == "3":
        durations = [
            ("شهر - 5 دنانير", "pay_bundle_3_1m"),
            ("3 أشهر - 10 دنانير", "pay_bundle_3_3m"),
            ("6 أشهر - 18 دينار", "pay_bundle_3_6m"),
            ("سنة - 30 دينار", "pay_bundle_3_1y"),
        ]
    else:
        durations = [
            ("شهر - 6 دنانير", "pay_bundle_4_1m"),
            ("3 أشهر - 12 دينار", "pay_bundle_4_3m"),
            ("6 أشهر - 22 دينار", "pay_bundle_4_6m"),
            ("سنة - 35 دينار", "pay_bundle_4_1y"),
        ]
        
    keyboard_buttons = [[InlineKeyboardButton(text=text, callback_data=cb)] for text, cb in durations]
    keyboard_buttons.append([InlineKeyboardButton(text="⬅️ رجوع", callback_data="cat_bundles")])
    
    await callback.message.edit_text(
        f"اختر المدة لباقة (**{b_count} اشتراكات**):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    )
    await callback.answer()

# ==================== 3. قسم طلب الأكواد ====================
@router.callback_query(F.data == "cat_codes")
async def codes_menu(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 طلب كود تسجيل دخول", callback_data="code_login")],
        [InlineKeyboardButton(text="🏠 طلب كود سكن (نتفليكس / OSN)", callback_data="code_household")],
        [InlineKeyboardButton(text="🔒 طلب كود 2FA", callback_data="code_2fa")],
        [InlineKeyboardButton(text="⬅️ رجوع للقائمة الرئيسية", callback_data="main_menu")]
    ])
    await callback.message.edit_text("اختر نوع الكود المطلوب:", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("code_"))
async def request_specific_code(callback: CallbackQuery, state: FSMContext):
    code_type = callback.data.split("_")[1]
    await state.update_data(code_type=code_type)
    
    titles = {
        "login": "كود تسجيل الدخول",
        "household": "كود سكن (نتفليكس / OSN)",
        "2fa": "كود 2FA للتحقق الثنائي"
    }
    
    await state.update_data(code_title=titles.get(code_type))
    await callback.message.edit_text(
        f"📩 لقد اخترت: **{titles.get(code_type)}**\n\n"
        "يرجى إرسال الإيميل أو رقم الهاتف المرتبط بالحساب ليتم توجيهه للإدارة وتزويدك بالكود:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ إلغاء", callback_data="cat_codes")]
        ])
    )
    await state.set_state(CodeState.waiting_for_code_info)
    await callback.answer()

@router.message(CodeState.waiting_for_code_info)
async def process_code_info(message: Message, state: FSMContext):
    data = await state.get_data()
    code_title = data.get("code_title")
    user = message.from_user
    
    admin_text = (
        "🔑 **طلب كود جديد!**\n\n"
        f"📌 **نوع الكود:** {code_title}\n"
        f"📧 **المعلومات المرسلة:** `{message.text}`\n\n"
        f"💬 للرد عليه وإرسال الكود، اضغط على الرابط التالي لمراسلته مباشرة:\n"
        f"[مراسلة الزبون](tg://user?id={user.id})\n"
        f"أو استخدم الأمر:\n`/reply {user.id} [اكتب الكود هنا]`"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text)
        except Exception:
            pass
            
    await message.answer(
        "✅ **تم إرسال طلبك للإدارة بنجاح!**\n"
        "سيتم إرسال الكود لك عبر البوت فور توفره.",
        reply_markup=main_menu_keyboard()
    )
    await state.clear()

# ==================== 4. قسم مشاكل الحساب (نظام التذاكر) ====================
@router.callback_query(F.data == "cat_issues")
async def start_issue_ticket(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "⚠️ **نظام حل مشاكل الحسابات:**\n\n"
        "يرجى إرسال البريد الإلكتروني (الإيميل) الخاص بالحساب الذي واجهت فيه المشكلة:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ إلغاء", callback_data="main_menu")]
        ])
    )
    await state.set_state(IssueState.waiting_for_email)
    await callback.answer()

@router.message(IssueState.waiting_for_email)
async def process_issue_email(message: Message, state: FSMContext):
    await state.update_data(issue_email=message.text)
    await message.answer(
        "📝 ممتاز. الآن يرجى **وصف المشكلة بالتفصيل** وإرفاق صورة للمشكلة إن وجدت في رسالة واحدة:"
    )
    await state.set_state(IssueState.waiting_for_description)

@router.message(IssueState.waiting_for_description)
async def process_issue_description(message: Message, state: FSMContext):
    data = await state.get_data()
    email = data.get("issue_email")
    user = message.from_user
    
    admin_text = (
        "🚨 **تذكرة مشكلة جديدة!**\n\n"
        f"📧 **الإيميل:** `{email}`\n"
        f"📋 **وصف المشكلة:** {message.text or message.caption or 'بدون نص'}\n\n"
        f"💬 للرد وحل المشكلة، اضغط على الرابط التالي لمراسلته مباشرة:\n"
        f"[مراسلة الزبون](tg://user?id={user.id})\n"
        f"أو استخدم الأمر:\n`/reply {user.id} [الرد أو الحل]`"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            if message.photo:
                await bot.send_photo(admin_id, message.photo[-1].file_id, caption=admin_text)
            else:
                await bot.send_message(admin_id, admin_text)
        except Exception:
            pass
            
    await message.answer(
        "✅ **تم إرسال تذكرتك بنجاح للإدارة!**\n"
        "سيتم مراجعة مشكلتك والرد عليك عبر البوت قريباً.",
        reply_markup=main_menu_keyboard()
    )
    await state.clear()

# ==================== 5. تدفق الدفع وإرسال الوصل ====================
@router.callback_query(F.data.startswith("pay_"))
async def start_payment(callback: CallbackQuery, state: FSMContext):
    await state.update_data(order_details=callback.data)
    await callback.message.edit_text(
        f"{CLIQ_INFO}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ إلغاء", callback_data="main_menu")]
        ])
    )
    await state.set_state(OrderState.waiting_for_receipt)
    await callback.answer()

@router.message(OrderState.waiting_for_receipt, F.photo)
async def receive_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    order_info = data.get("order_details")
    user = message.from_user
    
    admin_text = (
        "💰 **طلب شراء جديد بانتظار التأكيد!**\n\n"
        f"📦 **الطلب:** `{order_info}`\n\n"
        f"💬 لتسليم الحساب، اضغط على الرابط التالي لمراسلته مباشرة:\n"
        f"[مراسلة الزبون](tg://user?id={user.id})\n"
        f"أو استخدم الأمر:\n`/reply {user.id} [معلومات الحساب أو التأكيد]`"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_photo(
                admin_id,
                message.photo[-1].file_id,
                caption=admin_text
            )
        except Exception:
            pass
            
    await message.answer(
        "✅ **تم إرسال وصل الدفع بنجاح!**\n"
        "جاري مراجعة الحوالة وإرسال تفاصيل الحساب لك عبر البوت.",
        reply_markup=main_menu_keyboard()
    )
    await state.clear()

# تشغيل البوت
async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
