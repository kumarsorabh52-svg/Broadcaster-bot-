from telegram import (
Update,
ReplyKeyboardMarkup,
ReplyKeyboardRemove
)

from telegram.ext import (
Application,
CommandHandler,
ContextTypes,
MessageHandler,
filters,
)

from config import BOT_TOKEN, ADMIN_IDS
from db import load_chats, save_chats

broadcast_mode = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

keyboard = [
    ["📢 Broadcast"],
    ["📂 Groups", "📊 Stats"],
    ["🆔 My ID", "🗑 Clear Menu"]
]

await update.message.reply_text(
    "╔════════════════════╗\n"
    " 📢 BROADCAST PANEL\n"
    "╚════════════════════╝\n\n"
    "Welcome Admin!",
    reply_markup=ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )
)

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):

await update.message.reply_text(
    f"🆔 Your ID:\n{update.effective_user.id}"
)

async def connect(update: Update, context: ContextTypes.DEFAULT_TYPE):

if update.effective_chat.type == "private":

    await update.message.reply_text(
        "Use /connect inside a group."
    )

    return

chats = set(load_chats())

chats.add(
    update.effective_chat.id
)

save_chats(list(chats))

await update.message.reply_text(
    "✅ Group Connected Successfully"
)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

if update.effective_user.id not in ADMIN_IDS:
    return

chats = load_chats()

await update.message.reply_text(
    f"📊 Total Connected Groups: {len(chats)}"
)

async def groups(update: Update, context: ContextTypes.DEFAULT_TYPE):

if update.effective_user.id not in ADMIN_IDS:
    return

chats = load_chats()

if not chats:

    await update.message.reply_text(
        "📂 No groups connected."
    )

    return

text = "📂 Connected Groups\n\n"

for i, chat in enumerate(chats, start=1):
    text += f"{i}. {chat}\n"

await update.message.reply_text(text)

async def handle_buttons(
update: Update,
context: ContextTypes.DEFAULT_TYPE
):

if update.effective_user.id not in ADMIN_IDS:
    return

text = update.message.text

if text == "🆔 My ID":

    await myid(update, context)

elif text == "📊 Stats":

    await stats(update, context)

elif text == "📂 Groups":

    await groups(update, context)

elif text == "📢 Broadcast":

    broadcast_mode.add(
        update.effective_user.id
    )

    await update.message.reply_text(
        "✍️ Send message for broadcast."
    )

elif text == "🗑 Clear Menu":

    await update.message.reply_text(
        "Menu Removed",
        reply_markup=ReplyKeyboardRemove()
    )

elif update.effective_user.id in broadcast_mode:

    chats = load_chats()

    sent = 0

    for cid in chats:

        try:

            await context.bot.send_message(
                cid,
                text
            )

            sent += 1

        except:
            pass

    broadcast_mode.remove(
        update.effective_user.id
    )

    await update.message.reply_text(
        f"✅ Sent to {sent} chats."
    )

app = Application.builder().token(
BOT_TOKEN
).build()

app.add_handler(
CommandHandler("start", start)
)

app.add_handler(
CommandHandler("id", myid)
)

app.add_handler(
CommandHandler("connect", connect)
)

app.add_handler(
CommandHandler("stats", stats)
)

app.add_handler(
MessageHandler(
filters.TEXT & ~filters.COMMAND,
handle_buttons
)
)

if name == "main":
app.run_polling()
