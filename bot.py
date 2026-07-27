import hashlib
import html
import logging
import os

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
# 机器人版本
# =========================================================

BOT_VERSION = "2026-07-27-v6-text-only"


# =========================================================
# Render 环境变量
# =========================================================

# 必须在 Render -> Environment 中设置 BOT_TOKEN
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

WEBSITE_URL = os.getenv(
    "WEBSITE_URL",
    "https://gxtrx88.xyz/?id=888",
).strip()

CUSTOMER_SERVICE_USERNAME = os.getenv(
    "CUSTOMER_SERVICE_USERNAME",
    "TRX88898",
).strip().lstrip("@")

# Render Web Service 使用 webhook；本地运行可使用 polling
DEPLOY_MODE = os.getenv("DEPLOY_MODE", "").strip().lower()

WEBHOOK_BASE_URL = os.getenv(
    "WEBHOOK_BASE_URL",
    os.getenv("RENDER_EXTERNAL_URL", ""),
).strip().rstrip("/")

WEBHOOK_PATH = os.getenv(
    "WEBHOOK_PATH",
    "telegram-webhook",
).strip().strip("/")

WEBHOOK_SECRET = os.getenv(
    "WEBHOOK_SECRET",
    "",
).strip()


# =========================================================
# 固定地址
# 不再读取旧的 TRX_ADDRESS，避免旧环境变量覆盖
# =========================================================

ENERGY_ORDER_ADDRESS = "TLihmgj5j2PtafZvVSi1A2FHYw7fp3eXhe"
PACKAGE_PAYMENT_ADDRESS = "TEGdS6nyPqPdN6GW7YnmqVPHWRffffffff"
EXCHANGE_AUTO_ADDRESS = "TNVt5b3stodrAihbKJBNiYGp2Z11111111"
MEMBERSHIP_PAYMENT_ADDRESS = "TVVJrXXdqVswUQBWTkHK6gbPaaJSB7UcFx"


# =========================================================
# 日志
# =========================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# =========================================================
# 固定文案
# =========================================================

PROMO_LINE = "🎁 限时活动注册就送88 TRX！点击下面👇领取活动~"

WELCOME_TEXT = """
🎉 欢迎使用 TRX 能量租赁机器人！

👋 你好，{name}！

🚀 主要功能：
✏️ 笔数套餐
⚡️ 能量租用
✅ TRX闪兑
💎 代开会员
❓ 帮助说明
💬 联系客服

请点击下方菜单选择需要的服务。

🎁 限时活动注册就送88 TRX！
""".strip()

PACKAGE_TEXT = f"""
👉每笔单价：1 USDT
✅支付地址：
<code>{PACKAGE_PAYMENT_ADDRESS}</code>

👆请点击下方复制按钮，直接转入USDT，如转入100USDT，可获得100次免费转账次数

🔶赠送350带宽到地址，从此不再消耗0.35TRX
🔶按笔数计费的能量租用方式。
🔶每笔发送131K能量，对方地址无U也是扣一笔

🔶不限时，24小时内有一笔以上转账，不额外扣费！
1. 24小时内未转账，会扣除一笔计数。
2. 长时间不转账，可以在地址列表关闭笔数套餐

🔥【真】【假】笔数套餐科普：
✅无论65K或者131K（对方地址是否有U），只扣一笔！

👆最少10笔起购买
👆最大可获得500笔免费转账次数

❗️带宽兜底保护：
地址没有TRX并且没有带宽情况下，给地址发送350带宽或者0.35TRX，防止转账卡壳，地址从此不再预留TRX。

👆满足以上条件，才可称之为：【✏️笔数套餐】

🎁 限时活动注册就送88 TRX！点击下面👇领取活动~
""".strip()

ENERGY_TEXT = f"""
能量租用：
往下单地址转入相应的TRX

➖➖➖➖➖➖➖➖➖➖➖
转0.4TRX = 1笔转账对面有U
转0.8TRX = 2笔转账对面有U
（无U地址或者交易所翻倍）

➖➖➖➖➖➖➖➖➖➖➖
闪租能量下单地址：
<code>{ENERGY_ORDER_ADDRESS}</code>

👆请点击下方按钮复制地址

➖➖➖➖➖➖➖➖➖➖➖
1小时内有效，到时间能量自动回收

注明：如出现不返能量，需转一笔2.5TRX

🎁 限时活动注册就送88 TRX！点击下面👇领取活动~
""".strip()

TRX_EXCHANGE_TEXT = f"""
2.96 TRX
U换TRX 1USDT起换❗️

〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️
自动兑换地址：
<code>{EXCHANGE_AUTO_ADDRESS}</code>

👆请点击下方按钮复制地址

〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️
请不要使用交易所转账❗️
切记切记，否则丢失自负❗️
转账即兑，全自动返，等值1U起换❗️

请点击下方按钮进入兑换网站。
进入网站后，请先核对网址、兑换数量、手续费和收款地址，再确认操作。

🎁 限时活动注册就送88 TRX！点击下面👇领取活动~
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

HELP_TEXT = """
【❓帮助说明】

1. 点击“✏️笔数套餐”查看按笔计费说明。
2. 点击“⚡️能量租用”查看闪租价格和下单地址。
3. 点击“💎代开会员”，选择会员时长后输入需要开通的用户名。
4. 点击“✅ TRX闪兑”查看自动兑换地址。
5. 遇到订单、付款或到账问题，请点击“💬联系客服”。

发送 /cancel 可以取消正在填写的会员订单。
发送 /version 可以查看当前机器人版本。

⚠️ 链上转账通常无法撤回，付款前请仔细核对币种、网络和地址。

🎁 限时活动注册就送88 TRX！
""".strip()


# =========================================================
# 主菜单
# =========================================================

MENU_PROMO = "🔴 限时活动｜注册即送88TRX 🔴"
MENU_PACKAGE = "✏️ 笔数套餐"
MENU_ENERGY = "⚡️ 能量租用"

# 兼容用户手机上之前残留的旧按钮
MENU_ENERGY_OLD = "⚡️ 能量租赁"

MENU_EXCHANGE = "✅ TRX闪兑"
MENU_MEMBERSHIP = "💎 代开会员"
MENU_HELP = "❓ 帮助说明"
MENU_SERVICE = "💬 联系客服"

MENU_ROWS = [
    [MENU_PROMO],
    [MENU_PACKAGE, MENU_ENERGY, MENU_EXCHANGE],
    [MENU_MEMBERSHIP, MENU_HELP, MENU_SERVICE],
]

MENU_BUTTONS = {
    MENU_PROMO,
    MENU_PACKAGE,
    MENU_ENERGY,
    MENU_ENERGY_OLD,
    MENU_EXCHANGE,
    MENU_MEMBERSHIP,
    MENU_HELP,
    MENU_SERVICE,
}

MEMBERSHIP_PLANS = {
    "3": {"name": "3个月会员", "price": "10 U"},
    "6": {"name": "6个月会员", "price": "15 U"},
    "12": {"name": "1年会员", "price": "30 U"},
}


# =========================================================
# 键盘
# =========================================================


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=MENU_ROWS,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="请选择功能……",
    )


def website_keyboard(
    button_text: str = "🎁 限时活动注册就送88TRX",
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=button_text, url=WEBSITE_URL)]]
    )


def package_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="📋 点击复制笔数套餐支付地址",
                    copy_text=CopyTextButton(text=PACKAGE_PAYMENT_ADDRESS),
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎁 点击领取注册活动",
                    url=WEBSITE_URL,
                )
            ],
        ]
    )


def energy_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="📋 点击复制闪租下单地址",
                    copy_text=CopyTextButton(text=ENERGY_ORDER_ADDRESS),
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎁 点击领取注册活动",
                    url=WEBSITE_URL,
                )
            ],
        ]
    )


def exchange_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="📋 点击复制自动兑换地址",
                    copy_text=CopyTextButton(text=EXCHANGE_AUTO_ADDRESS),
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ 打开TRX闪兑网站｜注册送88TRX",
                    url=WEBSITE_URL,
                )
            ],
        ]
    )


def membership_keyboard() -> InlineKeyboardMarkup:
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


def membership_payment_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="📋 点击复制会员收款地址",
                    copy_text=CopyTextButton(text=MEMBERSHIP_PAYMENT_ADDRESS),
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
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=f"💬 点击联系 @{CUSTOMER_SERVICE_USERNAME}",
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


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message:
        return

    context.user_data.pop("membership_plan", None)

    user = update.effective_user
    name = html.escape(user.first_name) if user and user.first_name else "用户"

    await update.message.reply_text(
        WELCOME_TEXT.format(name=name),
        reply_markup=main_menu(),
    )


async def version_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message:
        return

    await update.message.reply_text(
        f"当前版本：{BOT_VERSION}\n\n"
        f"能量地址：\n{ENERGY_ORDER_ADDRESS}\n\n"
        f"笔数地址：\n{PACKAGE_PAYMENT_ADDRESS}\n\n"
        f"闪兑地址：\n{EXCHANGE_AUTO_ADDRESS}"
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message:
        return

    await update.message.reply_text(
        HELP_TEXT,
        reply_markup=website_keyboard(),
    )


async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message:
        return

    had_pending_order = context.user_data.pop("membership_plan", None) is not None

    if had_pending_order:
        text = "已取消当前会员订单，请重新选择功能。"
    else:
        text = "当前没有需要取消的订单，请点击下方菜单选择功能。"

    await update.message.reply_text(
        text,
        reply_markup=main_menu(),
    )


# =========================================================
# 会员处理
# =========================================================


async def select_membership(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    if not query:
        return

    await query.answer()

    callback_data = query.data or ""
    plan_key = callback_data.split(":", maxsplit=1)[-1]
    plan = MEMBERSHIP_PLANS.get(plan_key)

    if not plan:
        if query.message:
            await query.message.reply_text("套餐不存在，请重新选择。")
        return

    context.user_data["membership_plan"] = plan_key

    if not query.message:
        return

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
    if not update.message:
        return

    plan_key = context.user_data.get("membership_plan")
    plan = MEMBERSHIP_PLANS.get(plan_key)

    if not plan:
        return

    username_text = username_text.strip()

    if not username_text:
        await update.message.reply_text("用户名不能为空，请重新输入。")
        return

    safe_username = html.escape(username_text[:100])
    context.user_data.pop("membership_plan", None)

    await update.message.reply_text(
        "【💎会员订单信息】\n\n"
        f"✅ 已选择：<b>{plan['name']}</b>\n"
        f"💰 应付金额：<b>{plan['price']}</b>\n"
        f"👤 开通用户名：<code>{safe_username}</code>\n\n"
        "🔸会员收款地址：\n"
        f"<code>{MEMBERSHIP_PAYMENT_ADDRESS}</code>\n\n"
        "📋 请点击下方按钮复制会员收款地址。\n"
        "付款前请再次核对套餐、用户名、币种、网络和收款地址。\n"
        "付款后请联系客服，并提供交易哈希。",
        parse_mode=ParseMode.HTML,
        reply_markup=membership_payment_keyboard(),
    )


# =========================================================
# 主菜单文本处理
# =========================================================


async def handle_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

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
                parse_mode=ParseMode.HTML,
                reply_markup=package_keyboard(),
            )
            return

        if text in (MENU_ENERGY, MENU_ENERGY_OLD):
            await update.message.reply_text(
                ENERGY_TEXT,
                parse_mode=ParseMode.HTML,
                reply_markup=energy_keyboard(),
            )
            return

        if text == MENU_EXCHANGE:
            await update.message.reply_text(
                TRX_EXCHANGE_TEXT,
                parse_mode=ParseMode.HTML,
                reply_markup=exchange_keyboard(),
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
                f"客服用户名：@{CUSTOMER_SERVICE_USERNAME}\n\n"
                f"{PROMO_LINE}",
                reply_markup=service_keyboard(),
            )
            return

    if context.user_data.get("membership_plan"):
        await receive_membership_username(
            update=update,
            context=context,
            username_text=text,
        )
        return

    await update.message.reply_text(
        "请点击下方菜单选择功能。",
        reply_markup=main_menu(),
    )


# =========================================================
# 错误处理
# =========================================================


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if context.error:
        logger.error(
            "机器人处理消息时出现错误",
            exc_info=(
                type(context.error),
                context.error,
                context.error.__traceback__,
            ),
        )
    else:
        logger.error("机器人处理消息时出现未知错误")


# =========================================================
# 配置检查
# =========================================================


def validate_config() -> None:
    if not BOT_TOKEN or ":" not in BOT_TOKEN:
        raise ValueError(
            "缺少有效的 BOT_TOKEN，请到 Render Environment 添加。"
        )

    if not WEBSITE_URL.startswith(("https://", "http://")):
        raise ValueError("WEBSITE_URL 必须以 https:// 或 http:// 开头。")

    if not CUSTOMER_SERVICE_USERNAME:
        raise ValueError("CUSTOMER_SERVICE_USERNAME 不能为空。")


# =========================================================
# 创建 Application
# =========================================================


def build_application() -> Application:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("version", version_command))
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

    return application


# =========================================================
# Webhook 模式
# =========================================================


def run_webhook(application: Application) -> None:
    if not WEBHOOK_BASE_URL:
        raise ValueError(
            "Webhook 模式缺少 WEBHOOK_BASE_URL；Render 应自动提供 RENDER_EXTERNAL_URL。"
        )

    if not WEBHOOK_PATH:
        raise ValueError("WEBHOOK_PATH 不能为空。")

    if not WEBHOOK_SECRET:
        raise ValueError("Webhook 模式必须设置 WEBHOOK_SECRET。")

    telegram_secret = hashlib.sha256(
        WEBHOOK_SECRET.encode("utf-8")
    ).hexdigest()

    try:
        port = int(os.getenv("PORT", "10000"))
    except ValueError as exc:
        raise ValueError("PORT 必须是整数。") from exc

    webhook_url = f"{WEBHOOK_BASE_URL}/{WEBHOOK_PATH}"

    logger.info("机器人代码版本：%s", BOT_VERSION)
    logger.info("以 webhook 模式启动：%s", webhook_url)

    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=WEBHOOK_PATH,
        webhook_url=webhook_url,
        secret_token=telegram_secret,
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


# =========================================================
# Polling 模式
# =========================================================


def run_polling(application: Application) -> None:
    logger.info("机器人代码版本：%s", BOT_VERSION)
    logger.info("以 polling 模式启动。")

    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


# =========================================================
# 启动
# =========================================================


def run() -> None:
    validate_config()

    application = build_application()

    mode = DEPLOY_MODE

    if not mode:
        mode = "webhook" if WEBHOOK_BASE_URL else "polling"

    if mode == "webhook":
        run_webhook(application)
        return

    if mode == "polling":
        run_polling(application)
        return

    raise ValueError("DEPLOY_MODE 只能填写 webhook 或 polling。")


if __name__ == "__main__":
    run()
