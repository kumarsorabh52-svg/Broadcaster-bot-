from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from config import BOT_TOKEN

from db import (
    get_user_chats,
    save_user_chats,
    add_group
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["🆔 My ID"],
        ["🔗 Connect Group"],
        ["📊 My Groups"],
        ["📢 Broadcast Help"]
    ]

    await update.message.reply_text(
        "🤖 Multi User Broadcaster\n\nChoose an option:",
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
            "❌ Use /connect inside a group."
        )

        return

    user_id = update.effective_user.id
    group_id = update.effective_chat.id

    add_group(user_id, group_id)

    await update.message.reply_text(
        "✅ Group Connected Successfully"
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    chats = get_user_chats(user_id)

    await update.message.reply_text(
        f"📊 Your Connected Groups: {len(chats)}"
    )


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    msg = " ".join(context.args)

    if not msg:

        await update.message.reply_text(
            "Usage:\n/broadcast Hello World"
        )

        return

    chats = get_user_chats(user_id)

    if not chats:

        await update.message.reply_text(
            "❌ No groups connected."
        )

        return

    sent = 0

    for cid in chats:

        try:

            await context.bot.send_message(
                chat_id=cid,
                text=msg
            )

            sent += 1

        except Exception:
            pass

    await update.message.reply_text(
        f"✅ Broadcast sent to {sent} groups."
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
            "Add the bot to your group and run:\n/connect"
        )

    elif text == "📊 My Groups":

        await stats(update, context)

    elif text == "📢 Broadcast Help":

        await update.message.reply_text(
            "/broadcast Your Message"
        )


def main():

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

    print("Bot Started...")

    app.run_polling()


if __name__ == "__main__":
    main()
