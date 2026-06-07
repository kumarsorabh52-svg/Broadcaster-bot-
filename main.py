from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import BOT_TOKEN, ADMIN_IDS
from db import load_chats, save_chats


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
🤖 Broadcaster Bot

Commands:

/id - Your Telegram ID
/connect - Connect Group
/stats - Total Connected Groups
/broadcast MESSAGE - Send Broadcast
"""
    await update.message.reply_text(text)


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"
