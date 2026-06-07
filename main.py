from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
Application,
CommandHandler,
ContextTypes,
CallbackQueryHandler
)

from config import BOT_TOKEN, ADMIN_IDS
from db import load_chats, save_chats

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
keyboard = [
[InlineKeyboardButton("📊 Stats", callback_data="stats")],
[InlineKeyboardButton("🗑 Clear", callback_data="clear")],
]

await update.message.reply_text(
    "🤖 Broadcaster Admin Panel",
    reply_markup=InlineKeyboardMarkup(keyboard)
)

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
f"Your ID: {update.effective_user.id}"
)

async def connect(update: Update, context: ContextTypes.DEFAULT_TYPE):
if update.effective_chat.type == "private":
await update.message.reply_text(
"Use this command inside a group."
)
return

chats = set(load_chats())
chats.add(update.effective_chat.id)
save_chats(list(chats))

await update.message.reply_text("✅ Connected")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
if update.effective_user.id not in ADMIN_IDS:
return

msg = " ".join(context.args)

if not msg:
    await update.message.reply_text(
        "Usage:\n/broadcast Hello"
    )
    return

chats = load_chats()
sent = 0

for cid in chats:
    try:
        await context.bot.send_message(cid, msg)
        sent += 1
    except:
        pass

await update.message.reply_text(
    f"✅ Sent to {sent} chats."
)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()

if query.from_user.id not in ADMIN_IDS:
    return

if query.data == "stats":
    chats = load_chats()

    keyboard = [
        [InlineKeyboardButton("🏠 Main Menu", callback_data="home")]
    ]

    await query.edit_message_text(
        f"📊 Total Groups: {len(chats)}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

elif query.data == "clear":
    save_chats([])

    keyboard = [
        [InlineKeyboardButton("🏠 Main Menu", callback_data="home")]
    ]

    await query.edit_message_text(
        "🗑 All groups cleared.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

elif query.data == "home":
    keyboard = [
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("🗑 Clear", callback_data="clear")]
    ]

    await query.edit_message_text(
        "🤖 Broadcaster Admin Panel",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("id", myid))
app.add_handler(CommandHandler("connect", connect))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CallbackQueryHandler(button))

if name == "main":
app.run_polling()
