import html
import logging

from telegram import (
    CopyTextButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


# =========================================================
# 配置区域：只需要修改这里
# =========================================================

# 重要：请先到 @BotFather 撤销已经泄露的旧 Token，再把新 Token 粘贴到这里。
BOT_TOKEN = "8975865846:AAED24tLyacuFPADanBvt2bZu242Ql5IgnM"

# 用户点击“注册就送188TRX”后打开的网站
WEBSITE_URL = "https://gxtrx88.xyz/?id=888"

# 客服 Telegram 用户名（不要带 @）
CUSTOMER_SERVICE_USERNAME = "TRX88898"

# 能量闪租和会员付款地址
TRX_ADDRESS = "TVVJrXXdqVswUQBWTkHK6gbPaaJSB7UcFx"


# =========================================================
# 固定文案
# =========================================================

PROMO_LINE = "🎁 限时活动注册就送88 TRX！"

WELCOME_TEXT = """
🎉 欢迎使用 TRX 能量租赁机器人！

👋 你好，{name}！

🚀 主要功能：
✏️ 笔数套餐
⚡️ 能量租赁
✅ TRX闪兑
💎 代开会员
❓ 帮助说明
💬 联系客服

请点击下方菜单选择需要的服务。

🎁 限时活动注册就送88 TRX！
""".strip()

PACKAGE_TEXT = """
【✏️笔数套餐】：
🔶赠送350带宽到地址，从此不再消耗0.35TRX
🔶按笔数计费的能量租用方式。
🔶每笔发送131K能量，对方地址无U也是扣一笔

🔶不限时，24小时内有一笔以上转账，不额外扣费！
1. 24小时内未转账，会扣除一笔计数。
2. 长时间不转账，可以在地址列表关闭笔数套餐

🔥【真】【假】笔数套餐科普：
✅无论65K或者131K（对方地址是否有U），只扣一笔！

❗️带宽兜底保护：
地址没有TRX并且没有带宽情况下，给地址发送350带宽或者0.35TRX，防止转账卡壳，地址从此不再预留TRX。

👆满足以上条件，才可称之为：【✏️笔数套餐】

🎁 限时活动注册就送88 TRX！
""".strip()

ENERGY_TEXT = f"""
【⚡️能量闪租】
🔸转账  1.5 TRX = 1 笔能量
🔸转账  3 TRX = 2 笔能量

单笔3 TRX，以此类推，最大5笔。
1. 向无U地址转账，需要双倍能量。
2. 请在1小时内转账，否则过期回收。

🔸闪租能量收款地址：
<code>{TRX_ADDRESS}</code>

📋 请点击下方“复制收款地址”按钮即可复制。
➖➖➖➖➖➖➖➖➖
以下按钮可以选择其他能量租用模式。

温馨提醒：
闪租地址保存到地址本时要打上醒目标识，以免转账转错！
下方按钮揭秘低于成本价出租能量、依靠客户转错USDT获利的风险。

🎁 限时活动注册就送88 TRX！
""".strip()

MEMBERSHIP_TEXT = """
🌟星星价格：0.02 U/个
（支持单次购买50-10000个星星）

💎会员价格：
3个月会员：10 U
6个月会员：15 U
1年会员：30 U

请选择需要开通的会员时长：

🎁 限时活动注册就送88 TRX！
""".strip()

TRX_EXCHANGE_TEXT = """
【✅ TRX闪兑】

请点击下方按钮进入兑换网站。
进入网站后，请先核对网址、兑换数量、手续费和收款地址，再确认操作。

🎁 限时活动注册就送88 TRX！
""".strip()

HELP_TEXT = """
【❓帮助说明】

1. 点击“✏️笔数套餐”查看按笔计费说明。
2. 点击“⚡️能量租赁”查看闪租价格和收款地址。
3. 点击“💎代开会员”，选择会员时长后输入需要开通的用户名。
4. 点击“✅ TRX闪兑”进入兑换网站。
5. 遇到订单或到账问题，请点击“💬联系客服”。

发送 /cancel 可以取消正在填写的会员订单。

⚠️ 链上转账通常无法撤回，付款前请仔细核对币种、网络和地址。

🎁 限时活动注册就送88 TRX！
""".strip()


# =========================================================
# 主菜单
# =========================================================

MENU_PROMO = "🔴 限时活动｜注册即送88TRX 🔴"
MENU_PACKAGE = "✏️ 笔数套餐"
MENU_ENERGY = "⚡️ 能量租赁"
MENU_EXCHANGE = "✅ TRX闪兑"
MENU_MEMBERSHIP = "💎 代开会员"
MENU_HELP = "❓ 帮助说明"
MENU_SERVICE = "💬 联系客服"

MENU_ROWS = [
    [MENU_PROMO],
    [MENU_PACKAGE, MENU_ENERGY, MENU_EXCHANGE],
    [MENU_MEMBERSHIP, MENU_HELP, MENU_SERVICE],
]

MENU_BUTTONS = {button for row in MENU_ROWS for button in row}

MEMBERSHIP_PLANS = {
    "3": {"name": "3个月会员", "price": "10 U"},
    "6": {"name": "6个月会员", "price": "15 U"},
    "12": {"name": "1年会员", "price": "30 U"},
}


# =========================================================
# 日志
# =========================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# =========================================================
# 键盘
# =========================================================


def main_menu() -> ReplyKeyboardMarkup:
    """底部主菜单。"""
    return ReplyKeyboardMarkup(
        keyboard=MENU_ROWS,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="请选择功能……",
    )


def website_keyboard(button_text: str = "🎁 限时活动注册就送88TRX") -> InlineKeyboardMarkup:
    """打开网站的按钮。"""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=button_text, url=WEBSITE_URL)]]
    )


def energy_keyboard() -> InlineKeyboardMarkup:
    """能量闪租：复制地址和打开网站。"""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="📋 点击复制闪租收款地址",
                    copy_text=CopyTextButton(text=TRX_ADDRESS),
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔥 查看其他能量模式｜注册送88TRX",
                    url=WEBSITE_URL,
                )
            ],
        ]
    )


def membership_keyboard() -> InlineKeyboardMarkup:
    """会员套餐按钮。"""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="3个月会员｜10 U",
                    callback_data="member:3",
                )
            ],
            [
                InlineKeyboardButton(
                    text="6个月会员｜15 U",
                    callback_data="member:6",
                )
            ],
            [
                InlineKeyboardButton(
                    text="1年会员｜30 U",
                    callback_data="member:12",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎁 限时活动注册就送88TRX",
                    url=WEBSITE_URL,
                )
            ],
        ]
    )


def payment_keyboard() -> InlineKeyboardMarkup:
    """会员付款：复制地址、联系客户和打开网站。"""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="📋 点击复制会员收款地址",
                    copy_text=CopyTextButton(text=TRX_ADDRESS),
                )
            ],
            [
                InlineKeyboardButton(
                    text="💬 联系客服",
                    url=f"https://t.me/{CUSTOMER_SERVICE_USERNAME}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎁 限时活动注册就送88TRX",
                    url=WEBSITE_URL,
                )
            ],
        ]
    )


def service_keyboard() -> InlineKeyboardMarkup:
    """联系客服和网站按钮。"""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="💬 点击联系 @TRX00B",
                    url=f"https://t.me/{CUSTOMER_SERVICE_USERNAME}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎁 限时活动注册就送88TRX",
                    url=WEBSITE_URL,
                )
            ],
        ]
    )


# =========================================================
# 命令处理
# =========================================================


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /start。"""
    if not update.message:
        return

    # 开始时清除未完成的会员输入状态
    context.user_data.pop("membership_plan", None)

    user = update.effective_user
    name = user.first_name if user and user.first_name else "用户"

    await update.message.reply_text(
        WELCOME_TEXT.format(name=html.escape(name)),
        reply_markup=main_menu(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /help。"""
    if not update.message:
        return

    await update.message.reply_text(
        HELP_TEXT,
        reply_markup=website_keyboard(),
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """取消会员用户名输入。"""
    if not update.message:
        return

    had_pending_order = context.user_data.pop("membership_plan", None) is not None

    if had_pending_order:
        text = "已取消当前会员订单，请重新选择功能。"
    else:
        text = "当前没有需要取消的订单，请点击下方菜单选择功能。"

    await update.message.reply_text(text, reply_markup=main_menu())


# =========================================================
# 会员按钮和用户名处理
# =========================================================


async def select_membership(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """用户点击会员时长按钮。"""
    query = update.callback_query
    if not query:
        return

    await query.answer()

    callback_data = query.data or ""
    plan_key = callback_data.split(":", maxsplit=1)[-1]
    plan = MEMBERSHIP_PLANS.get(plan_key)

    if not plan:
        await query.message.reply_text("套餐不存在，请重新选择。")
        return

    context.user_data["membership_plan"] = plan_key

    await query.message.reply_text(
        f"✅ 您选择的是：<b>{plan['name']}</b>\n"
        f"💰 价格：<b>{plan['price']}</b>\n\n"
        "请直接发送需要开通会员的 Telegram 用户名。\n"
        "例如：<code>@username</code>\n\n"
        "发送 /cancel 可取消。",
        parse_mode=ParseMode.HTML,
    )


async def receive_membership_username(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    username_text: str,
) -> None:
    """接收用户输入的会员用户名并展示付款信息。"""
    plan_key = context.user_data.get("membership_plan")
    plan = MEMBERSHIP_PLANS.get(plan_key)

    if not plan:
        return

    username_text = username_text.strip()
    if not username_text:
        await update.message.reply_text("用户名不能为空，请重新输入。")
        return

    # 最多保留100个字符，避免用户发送超长内容刷屏
    username_text = username_text[:100]
    safe_username = html.escape(username_text)

    # 完成后清除等待状态
    context.user_data.pop("membership_plan", None)

    await update.message.reply_text(
        "【💎会员订单信息】\n\n"
        f"✅ 已选择：<b>{plan['name']}</b>\n"
        f"💰 应付金额：<b>{plan['price']}</b>\n"
        f"👤 开通用户名：<code>{safe_username}</code>\n\n"
        "🔸会员收款地址：\n"
        f"<code>{TRX_ADDRESS}</code>\n\n"
        "📋 请点击下方“复制会员收款地址”按钮即可复制。\n"
        "付款前请再次核对套餐、用户名、币种、网络和收款地址。\n"
        "付款后请联系客服，并提供交易哈希。",
        parse_mode=ParseMode.HTML,
        reply_markup=payment_keyboard(),
    )


# =========================================================
# 主菜单文本处理
# =========================================================


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理主菜单点击和会员用户名输入。"""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    # 用户点击主菜单时，优先切换功能并取消上一次未完成的会员输入
    if text in MENU_BUTTONS:
        context.user_data.pop("membership_plan", None)

        logger.info(
            "用户 %s 点击菜单：%s",
            update.effective_user.id if update.effective_user else "未知",
            text,
        )

        if text == MENU_PROMO:
            await update.message.reply_text(
                "🔴 <b>限时活动</b> 🔴\n\n"
                "🎁 注册即送 <b>88TRX</b>！\n\n"
                "点击下方按钮立即注册领取。",
                parse_mode=ParseMode.HTML,
                reply_markup=website_keyboard("🔴 立即注册领取88TRX"),
            )
            return

        if text == MENU_PACKAGE:
            await update.message.reply_text(
                PACKAGE_TEXT,
                reply_markup=website_keyboard(),
            )
            return

        if text == MENU_ENERGY:
            await update.message.reply_text(
                ENERGY_TEXT,
                parse_mode=ParseMode.HTML,
                reply_markup=energy_keyboard(),
            )
            return

        if text == MENU_EXCHANGE:
            await update.message.reply_text(
                TRX_EXCHANGE_TEXT,
                reply_markup=website_keyboard("✅ 打开TRX闪兑网站｜注册送88TRX"),
            )
            return

        if text == MENU_MEMBERSHIP:
            await update.message.reply_text(
                MEMBERSHIP_TEXT,
                reply_markup=membership_keyboard(),
            )
            return

        if text == MENU_HELP:
            await update.message.reply_text(
                HELP_TEXT,
                reply_markup=website_keyboard(),
            )
            return

        if text == MENU_SERVICE:
            await update.message.reply_text(
                "遇到订单、付款或到账问题，请点击下方按钮联系客服。\n\n"
                "客服用户名：@TRX00B\n\n"
                f"{PROMO_LINE}",
                reply_markup=service_keyboard(),
            )
            return

    # 正在等待会员用户名时，把这条普通文本作为用户名处理
    if context.user_data.get("membership_plan"):
        await receive_membership_username(update, context, text)
        return

    await update.message.reply_text(
        "请点击下方菜单选择功能。",
        reply_markup=main_menu(),
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """记录错误。"""
    logger.exception("机器人处理消息时出现错误", exc_info=context.error)


# =========================================================
# 启动
# =========================================================


def run() -> None:
    """启动机器人。"""
    if (
        not BOT_TOKEN
        or BOT_TOKEN == "请在这里粘贴BotFather新生成的Token"
        or ":" not in BOT_TOKEN
    ):
        raise ValueError(
            "请打开 bot_complete.py，在 BOT_TOKEN 中粘贴 BotFather 新生成的 Token。"
        )

    if not WEBSITE_URL.startswith(("https://", "http://")):
        raise ValueError("WEBSITE_URL 必须以 https:// 或 http:// 开头。")

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cancel", cancel))

    application.add_handler(
        CallbackQueryHandler(
            select_membership,
            pattern=r"^member:(3|6|12)$",
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text,
        )
    )

    application.add_error_handler(error_handler)

    print("机器人已经启动，按 Ctrl+C 停止。")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    run()