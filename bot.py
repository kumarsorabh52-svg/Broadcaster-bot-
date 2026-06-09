import logging
import asyncio
import json
import os
from datetime import datetime
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    Bot
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
import pytz

# ─── LOGGING ────────────────────────────────────────────────────────────────
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── CONFIG ─────────────────────────────────────────────────────────────────
from config import BOT_TOKEN, ADMIN_IDS, TIMEZONE, DATA_FILE

# ─── STATES ─────────────────────────────────────────────────────────────────
(
    MAIN_MENU,
    SELECT_GROUPS,
    WRITE_MESSAGE,
    ADD_BUTTONS,
    BUTTON_TEXT,
    BUTTON_URL,
    MORE_BUTTONS,
    SCHEDULE_CHOICE,
    SCHEDULE_TIME,
    CONFIRM_SEND,
) = range(10)

# ─── DATA HELPERS ────────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"groups": {}, "scheduled": []}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─── SCHEDULER ───────────────────────────────────────────────────────────────
scheduler = AsyncIOScheduler(timezone=TIMEZONE)

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def groups_keyboard(selected: list, all_groups: dict):
    keyboard = []
    for gid, gname in all_groups.items():
        check = "✅" if gid in selected else "⬜"
        keyboard.append([InlineKeyboardButton(
            f"{check} {gname}", callback_data=f"grp_{gid}"
        )])
    keyboard.append([
        InlineKeyboardButton("🔘 Select All", callback_data="grp_all"),
        InlineKeyboardButton("🔲 Deselect All", callback_data="grp_none"),
    ])
    keyboard.append([InlineKeyboardButton("✅ Done", callback_data="grp_done")])
    return InlineKeyboardMarkup(keyboard)

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📢 New Announcement", callback_data="new_announcement")],
        [InlineKeyboardButton("⏰ Scheduled Messages", callback_data="view_scheduled")],
        [InlineKeyboardButton("👥 Registered Groups", callback_data="view_groups")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ─── COMMANDS ────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("⛔ Aap admin nahi hain.")
        return ConversationHandler.END

    await update.message.reply_text(
        f"👋 Namaste, <b>{user.first_name}</b>!\n\n"
        "🤖 <b>Announcement Bot</b> ready hai.\n"
        "Kya karna chahte hain?",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard()
    )
    return MAIN_MENU

async def register_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jab bot group mein add hota hai, group register hota hai"""
    chat = update.effective_chat
    if chat.type in ("group", "supergroup"):
        data = load_data()
        data["groups"][str(chat.id)] = chat.title or "Unknown Group"
        save_data(data)
        logger.info(f"Group registered: {chat.title} ({chat.id})")

# ─── MAIN MENU ────────────────────────────────────────────────────────────────
async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "new_announcement":
        return await start_announcement(update, context)
    elif query.data == "view_scheduled":
        return await view_scheduled(update, context)
    elif query.data == "view_groups":
        return await view_groups(update, context)

async def view_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = load_data()
    groups = data.get("groups", {})
    if not groups:
        text = "❌ Koi group registered nahi hai.\n\nBot ko group mein add karein aur /start karein."
    else:
        lines = [f"👥 <b>Registered Groups ({len(groups)}):</b>\n"]
        for gid, gname in groups.items():
            lines.append(f"• {gname} (<code>{gid}</code>)")
        text = "\n".join(lines)

    await query.edit_message_text(
        text, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data="back_main")
        ]])
    )
    return MAIN_MENU

async def view_scheduled(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = load_data()
    scheduled = data.get("scheduled", [])

    if not scheduled:
        text = "⏰ Koi scheduled message nahi hai."
    else:
        lines = [f"⏰ <b>Scheduled Messages ({len(scheduled)}):</b>\n"]
        for i, item in enumerate(scheduled, 1):
            lines.append(
                f"{i}. 📅 <b>{item['time']}</b>\n"
                f"   📝 {item['message'][:50]}...\n"
                f"   👥 Groups: {len(item['groups'])}\n"
            )
        text = "\n".join(lines)

    keyboard = []
    for i, item in enumerate(scheduled):
        keyboard.append([InlineKeyboardButton(
            f"🗑 Cancel #{i+1}", callback_data=f"cancel_scheduled_{i}"
        )])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_main")])

    await query.edit_message_text(
        text, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN_MENU

async def cancel_scheduled_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split("_")[-1])
    data = load_data()
    if 0 <= idx < len(data["scheduled"]):
        removed = data["scheduled"].pop(idx)
        save_data(data)
        job_id = removed.get("job_id")
        if job_id and scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        await query.answer("✅ Scheduled message cancel ho gaya!", show_alert=True)
    await view_scheduled(update, context)

async def back_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📋 Main Menu:",
        reply_markup=main_menu_keyboard()
    )
    return MAIN_MENU

# ─── ANNOUNCEMENT FLOW ────────────────────────────────────────────────────────
async def start_announcement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = load_data()
    groups = data.get("groups", {})

    if not groups:
        await query.edit_message_text(
            "❌ Koi group registered nahi hai!\n\n"
            "Pehle bot ko group mein add karein.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="back_main")
            ]])
        )
        return MAIN_MENU

    context.user_data['selected_groups'] = []
    context.user_data['buttons'] = []

    await query.edit_message_text(
        "👥 <b>Groups Select Karein:</b>\n\n"
        "Jin groups mein announcement bhejna hai unhe select karein:",
        parse_mode="HTML",
        reply_markup=groups_keyboard([], groups)
    )
    return SELECT_GROUPS

async def group_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    groups = data.get("groups", {})
    selected = context.user_data.get('selected_groups', [])

    if query.data == "grp_all":
        selected = list(groups.keys())
    elif query.data == "grp_none":
        selected = []
    elif query.data == "grp_done":
        if not selected:
            await query.answer("⚠️ Kam se kam ek group select karein!", show_alert=True)
            return SELECT_GROUPS
        context.user_data['selected_groups'] = selected
        await query.edit_message_text(
            f"✅ <b>{len(selected)} group(s) selected.</b>\n\n"
            "📝 Ab announcement message type karein:",
            parse_mode="HTML"
        )
        return WRITE_MESSAGE
    else:
        gid = query.data.replace("grp_", "")
        if gid in selected:
            selected.remove(gid)
        else:
            selected.append(gid)

    context.user_data['selected_groups'] = selected
    await query.edit_message_reply_markup(
        reply_markup=groups_keyboard(selected, groups)
    )
    return SELECT_GROUPS

async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data['message'] = text

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Inline Button Add Karein", callback_data="add_btn")],
        [InlineKeyboardButton("⏭ Skip (No Buttons)", callback_data="skip_btn")],
    ])
    await update.message.reply_text(
        f"📝 <b>Message saved!</b>\n\n"
        f"<i>{text[:200]}</i>\n\n"
        "Inline buttons add karne hain?",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    return ADD_BUTTONS

async def add_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "skip_btn":
        return await ask_schedule(update, context)
    elif query.data == "add_btn":
        await query.edit_message_text(
            "🔘 <b>Button ka text likhein:</b>\n\n"
            "Jaise: <code>🌐 Visit Website</code>",
            parse_mode="HTML"
        )
        return BUTTON_TEXT

async def receive_button_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['temp_btn_text'] = update.message.text
    await update.message.reply_text(
        "🔗 <b>Button ka URL likhein:</b>\n\n"
        "Jaise: <code>https://example.com</code>",
        parse_mode="HTML"
    )
    return BUTTON_URL

async def receive_button_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith(("http://", "https://", "t.me/")):
        await update.message.reply_text("⚠️ Valid URL likhein (http:// ya https:// se shuru):")
        return BUTTON_URL

    btn_text = context.user_data.get('temp_btn_text', 'Button')
    buttons = context.user_data.get('buttons', [])
    buttons.append({"text": btn_text, "url": url})
    context.user_data['buttons'] = buttons

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Aur Button Add Karein", callback_data="add_btn")],
        [InlineKeyboardButton("✅ Done", callback_data="skip_btn")],
    ])
    await update.message.reply_text(
        f"✅ Button added! Total: <b>{len(buttons)}</b>\n\n"
        f"Aur buttons chahiye?",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    return ADD_BUTTONS

async def ask_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query if update.callback_query else None

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 Abhi Bhejo", callback_data="send_now")],
        [InlineKeyboardButton("⏰ Schedule Karein", callback_data="schedule_later")],
    ])
    text = "⏰ <b>Kab bhejna hai?</b>"

    if query:
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)

    return SCHEDULE_CHOICE

async def schedule_choice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "send_now":
        context.user_data['schedule_time'] = None
        return await confirm_send(update, context)
    elif query.data == "schedule_later":
        tz = pytz.timezone(TIMEZONE)
        now = datetime.now(tz).strftime("%Y-%m-%d %H:%M")
        await query.edit_message_text(
            f"📅 <b>Schedule time likhein:</b>\n\n"
            f"Format: <code>YYYY-MM-DD HH:MM</code>\n"
            f"Example: <code>2025-01-15 14:30</code>\n\n"
            f"⏰ Current time ({TIMEZONE}): <code>{now}</code>",
            parse_mode="HTML"
        )
        return SCHEDULE_TIME

async def receive_schedule_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time_str = update.message.text.strip()
    try:
        tz = pytz.timezone(TIMEZONE)
        schedule_dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        schedule_dt = tz.localize(schedule_dt)
        now = datetime.now(tz)
        if schedule_dt <= now:
            await update.message.reply_text("⚠️ Future ka time likhein!")
            return SCHEDULE_TIME
        context.user_data['schedule_time'] = schedule_dt.isoformat()
        return await confirm_send_message(update, context)
    except ValueError:
        await update.message.reply_text(
            "⚠️ Format galat hai!\n"
            "Sahi format: <code>YYYY-MM-DD HH:MM</code>\n"
            "Example: <code>2025-01-15 14:30</code>",
            parse_mode="HTML"
        )
        return SCHEDULE_TIME

async def confirm_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    message = context.user_data.get('message', '')
    selected = context.user_data.get('selected_groups', [])
    buttons = context.user_data.get('buttons', [])
    data = load_data()
    groups = data.get("groups", {})
    group_names = [groups.get(g, g) for g in selected]

    text = (
        f"📋 <b>Confirm Karein:</b>\n\n"
        f"📝 <b>Message:</b>\n{message[:300]}\n\n"
        f"👥 <b>Groups ({len(selected)}):</b>\n" +
        "\n".join(f"• {n}" for n in group_names) + "\n\n"
        f"🔘 <b>Buttons:</b> {len(buttons)}\n"
        f"⏰ <b>Time:</b> Abhi"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Bhejo!", callback_data="confirm_yes"),
            InlineKeyboardButton("❌ Cancel", callback_data="confirm_no"),
        ]
    ])
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)
    return CONFIRM_SEND

async def confirm_send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = context.user_data.get('message', '')
    selected = context.user_data.get('selected_groups', [])
    buttons = context.user_data.get('buttons', [])
    schedule_time = context.user_data.get('schedule_time')
    data = load_data()
    groups = data.get("groups", {})
    group_names = [groups.get(g, g) for g in selected]

    text = (
        f"📋 <b>Confirm Karein:</b>\n\n"
        f"📝 <b>Message:</b>\n{message[:300]}\n\n"
        f"👥 <b>Groups ({len(selected)}):</b>\n" +
        "\n".join(f"• {n}" for n in group_names) + "\n\n"
        f"🔘 <b>Buttons:</b> {len(buttons)}\n"
        f"⏰ <b>Scheduled:</b> {schedule_time or 'Abhi'}"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirm!", callback_data="confirm_yes"),
            InlineKeyboardButton("❌ Cancel", callback_data="confirm_no"),
        ]
    ])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)
    return CONFIRM_SEND

async def confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_no":
        await query.edit_message_text("❌ Cancelled.", reply_markup=main_menu_keyboard())
        return MAIN_MENU

    message = context.user_data.get('message', '')
    selected = context.user_data.get('selected_groups', [])
    buttons = context.user_data.get('buttons', [])
    schedule_time = context.user_data.get('schedule_time')

    if schedule_time:
        # Schedule karo
        job_id = f"sched_{datetime.now().timestamp()}"
        tz = pytz.timezone(TIMEZONE)
        send_dt = datetime.fromisoformat(schedule_time)

        # Save to data
        data = load_data()
        data["scheduled"].append({
            "job_id": job_id,
            "message": message,
            "groups": selected,
            "buttons": buttons,
            "time": schedule_time,
        })
        save_data(data)

        scheduler.add_job(
            send_announcement,
            trigger=DateTrigger(run_date=send_dt),
            args=[context.application, selected, message, buttons, job_id],
            id=job_id
        )

        await query.edit_message_text(
            f"✅ <b>Scheduled!</b>\n\n"
            f"⏰ {schedule_time}\n"
            f"👥 {len(selected)} groups\n\n"
            "Message time par automatically bheja jayega! ✨",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard()
        )
    else:
        # Abhi bhejo
        await query.edit_message_text("⏳ Bhejna shuru ho raha hai...", parse_mode="HTML")
        success, fail = await send_announcement(
            context.application, selected, message, buttons
        )
        await query.edit_message_text(
            f"✅ <b>Announcement Bhej Di!</b>\n\n"
            f"✔️ Success: {success} groups\n"
            f"❌ Failed: {fail} groups",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard()
        )
    return MAIN_MENU

# ─── SEND FUNCTION ────────────────────────────────────────────────────────────
async def send_announcement(app, group_ids, message, buttons, job_id=None):
    success = 0
    fail = 0

    # Build inline keyboard from buttons
    reply_markup = None
    if buttons:
        rows = []
        for btn in buttons:
            rows.append([InlineKeyboardButton(btn["text"], url=btn["url"])])
        reply_markup = InlineKeyboardMarkup(rows)

    for gid in group_ids:
        try:
            await app.bot.send_message(
                chat_id=int(gid),
                text=message,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
            success += 1
            await asyncio.sleep(0.3)  # Flood avoid
        except Exception as e:
            logger.error(f"Failed to send to {gid}: {e}")
            fail += 1

    # Remove from scheduled if it was scheduled
    if job_id:
        data = load_data()
        data["scheduled"] = [s for s in data["scheduled"] if s.get("job_id") != job_id]
        save_data(data)

    return success, fail

# ─── CANCEL COMMAND ───────────────────────────────────────────────────────────
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Cancel ho gaya.",
        reply_markup=main_menu_keyboard()
    )
    return MAIN_MENU

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Conversation handler
    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(main_menu_callback, pattern="^(new_announcement|view_scheduled|view_groups)$"),
        ],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(main_menu_callback, pattern="^(new_announcement|view_scheduled|view_groups)$"),
                CallbackQueryHandler(back_main_callback, pattern="^back_main$"),
                CallbackQueryHandler(cancel_scheduled_callback, pattern="^cancel_scheduled_"),
            ],
            SELECT_GROUPS: [
                CallbackQueryHandler(group_selection_callback, pattern="^grp_"),
            ],
            WRITE_MESSAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message),
            ],
            ADD_BUTTONS: [
                CallbackQueryHandler(add_button_callback, pattern="^(add_btn|skip_btn)$"),
            ],
            BUTTON_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_button_text),
            ],
            BUTTON_URL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_button_url),
                CallbackQueryHandler(add_button_callback, pattern="^(add_btn|skip_btn)$"),
            ],
            SCHEDULE_CHOICE: [
                CallbackQueryHandler(schedule_choice_callback, pattern="^(send_now|schedule_later)$"),
            ],
            SCHEDULE_TIME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_schedule_time),
            ],
            CONFIRM_SEND: [
                CallbackQueryHandler(confirm_callback, pattern="^confirm_"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        allow_reentry=True,
    )

    app.add_handler(conv)

    # Group register handler
    app.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.ChatType.GROUPS,
        register_group
    ))

    # Start scheduler
    scheduler.start()

    # Restore scheduled jobs on startup
    data = load_data()
    for item in data.get("scheduled", []):
        try:
            tz = pytz.timezone(TIMEZONE)
            send_dt = datetime.fromisoformat(item["time"])
            if send_dt > datetime.now(tz):
                scheduler.add_job(
                    send_announcement,
                    trigger=DateTrigger(run_date=send_dt),
                    args=[app, item["groups"], item["message"], item["buttons"], item["job_id"]],
                    id=item["job_id"]
                )
        except Exception as e:
            logger.error(f"Failed to restore job: {e}")

    logger.info("🤖 Bot starting...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
