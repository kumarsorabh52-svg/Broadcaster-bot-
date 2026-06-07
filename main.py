from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import BOT_TOKEN, ADMIN_IDS
from db import save_user, save_group, get_groups

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Broadcaster Bot Active")

async def connect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text("Use in a group.")
        return
    chats=set(load_chats())
    chats.add(update.effective_chat.id)
    save_chats(list(chats))
    await update.message.reply_text("Connected.")
async def myid(update: Update, context):
    await update.message.reply_text(
        f"Your ID: {update.effective_user.id}"
    )
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    msg=" ".join(context.args)
    chats=load_chats()
    sent=0
    for cid in chats:
        try:
            await context.bot.send_message(cid,msg)
            sent+=1
        except Exception:
            pass
    await update.message.reply_text(f"Sent to {sent} chats")

app=Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(CommandHandler("connect",connect))
app.add_handler(CommandHandler("broadcast",broadcast))

if __name__=="__main__":
    app.run_polling()
