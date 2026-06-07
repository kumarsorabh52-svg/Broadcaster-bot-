from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from config import BOT_TOKEN, ADMIN_IDS
from db import load_chats, save_chats


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["🆔 My ID"],
        ["🔗 Connect Group"],
        ["📊 Stats"],
        ["📢 Broadcast Help"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "🤖 Broadcaster Bot\n\nChoose an option:",
        reply_markup=reply_markup
    )


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        f"Your ID: {update.effective_user.id}"
    )


async def connect(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type == "private":

        await update.message.reply_text(
            "Use /connect inside a group."
        )

        return

    chats = set(load_chats())

    chats.add(update.effective_chat.id)

    save_chats(list(chats))

    await update.message.reply_text(
        "✅ Group Connected Successfully"
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chats = load_chats()

    await update.message.reply_text(
        f"📊 Total Connected Groups: {len(chats)}"
    )


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

            await context.bot.send_message(
                chat_id=cid,
                text=msg
            )

            sent += 1

        except:
            pass

    await update.message.reply_text(
        f"✅ Sent to {sent} chats."
    )


async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text

    if text == "🆔 My ID":

        await myid(update, context)

    elif text == "🔗 Connect Group":

        await update.message.reply_text(
            "Go to your group and send /connect"
        )

    elif text == "📊 Stats":

        await stats(update, context)

    elif text == "📢 Broadcast Help":

        await update.message.reply_text(
            "Use:\n/broadcast Your Message"
        )


app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("id", myid))
app.add_handler(CommandHandler("connect", connect))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("broadcast", broadcast))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        button_handler
    )
)

if __name__ == "__main__":
    app.run_polling()
