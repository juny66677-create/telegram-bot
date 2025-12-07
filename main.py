from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime
import pytz

BOT_TOKEN = "8584678889:AAEWEULd7PAdXsKtyvs3nio2LWQdkeiz05M"

# Cambodia timezone
KH_TZ = pytz.timezone("Asia/Phnom_Penh")

user_status = {}


# ---------------------------------------------------------
# KEYBOARD BUTTONS
# ---------------------------------------------------------
def get_keyboard():
    keyboard = [
        ["Start Work", "Off Work"],
        ["WC", "Eat", "Smoke"],
        ["Back"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ---------------------------------------------------------
# START WORK
# ---------------------------------------------------------
async def startwork(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    full_name = update.effective_user.full_name

    if user_id in user_status and user_status[user_id].get("startwork_time"):
        start = user_status[user_id]["startwork_time"].strftime("%Y-%m-%d %H:%M:%S")
        await update.message.reply_text(
            f"❌ You already checked in at **{start}**.\nPlease offwork first.",
            parse_mode="Markdown"
        )
        return

    now = datetime.now(KH_TZ)
    user_status[user_id] = {
        "startwork_time": now,
        "wc_start": None,
        "eat_start": None,
        "smoke_start": None
    }

    await update.message.reply_text(
        f"✔️ Start Work Successful!\n👤 {full_name}\n🕒 {now.strftime('%Y-%m-%d %H:%M:%S')}",
        reply_markup=get_keyboard()
    )


# ---------------------------------------------------------
# OFF WORK
# ---------------------------------------------------------
async def offwork(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    full_name = update.effective_user.full_name

    if user_id not in user_status or user_status[user_id]["startwork_time"] is None:
        await update.message.reply_text("❌ You have not checked in.")
        return

    start_time = user_status[user_id]["startwork_time"]
    end_time = datetime.now(KH_TZ)

    duration = end_time - start_time
    hours = duration.seconds // 3600
    minutes = (duration.seconds % 3600) // 60

    user_status[user_id] = {
        "startwork_time": None,
        "wc_start": None,
        "eat_start": None,
        "smoke_start": None
    }

    await update.message.reply_markdown(
        f"✔️ **Work Finished!**\n\n"
        f"👤 *{full_name}*\n"
        f"🟢 Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"🔴 End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"⏳ **Total:** {hours}h {minutes}m"
    )


# ---------------------------------------------------------
# WC
# ---------------------------------------------------------
async def wc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_status or user_status[user_id]["startwork_time"] is None:
        await update.message.reply_text("❌ You must Start Work first.")
        return

    if user_status[user_id]["eat_start"] or user_status[user_id]["smoke_start"]:
        await update.message.reply_text("❌ You must return Back first.")
        return

    if user_status[user_id]["wc_start"]:
        await update.message.reply_text("❌ Already in WC. Press Back.")
        return

    now = datetime.now(KH_TZ)
    user_status[user_id]["wc_start"] = now

    await update.message.reply_text(f"🚾 WC started at {now.strftime('%Y-%m-%d %H:%M:%S')}")


# ---------------------------------------------------------
# EATING
# ---------------------------------------------------------
async def eat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_status or user_status[user_id]["startwork_time"] is None:
        await update.message.reply_text("❌ You must Start Work first.")
        return

    if user_status[user_id]["wc_start"] or user_status[user_id]["smoke_start"]:
        await update.message.reply_text("❌ You must return Back first.")
        return

    if user_status[user_id]["eat_start"]:
        await update.message.reply_text("❌ You are already eating.")
        return

    now = datetime.now(KH_TZ)
    user_status[user_id]["eat_start"] = now
    await update.message.reply_text(f"🍽 Eating started at {now.strftime('%Y-%m-%d %H:%M:%S')}")


# ---------------------------------------------------------
# SMOKING
# ---------------------------------------------------------
async def smoke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_status or user_status[user_id]["startwork_time"] is None:
        await update.message.reply_text("❌ You must Start Work first.")
        return

    if user_status[user_id]["wc_start"] or user_status[user_id]["eat_start"]:
        await update.message.reply_text("❌ You must return Back first.")
        return

    if user_status[user_id]["smoke_start"]:
        await update.message.reply_text("❌ Already smoking.")
        return

    now = datetime.now(KH_TZ)
    user_status[user_id]["smoke_start"] = now
    await update.message.reply_text(f"🚬 Smoking started at {now.strftime('%Y-%m-%d %H:%M:%S')}")


# ---------------------------------------------------------
# BACK (END BREAK)
# ---------------------------------------------------------
async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = datetime.now(KH_TZ)

    # WC
    if user_status[user_id]["wc_start"]:
        start = user_status[user_id]["wc_start"]
        mins = int((now - start).seconds / 60)
        warn = "⚠️ Exceeded 15 minutes!" if mins > 15 else "👍 Within time."
        user_status[user_id]["wc_start"] = None
        await update.message.reply_text(f"🚾 WC ended — {mins} min\n{warn}")
        return

    # Eating
    if user_status[user_id]["eat_start"]:
        start = user_status[user_id]["eat_start"]
        mins = int((now - start).seconds / 60)
        warn = "⚠️ Exceeded 30 minutes!" if mins > 30 else "👍 Within time."
        user_status[user_id]["eat_start"] = None
        await update.message.reply_text(f"🍽 Eating ended — {mins} min\n{warn}")
        return

    # Smoking
    if user_status[user_id]["smoke_start"]:
        start = user_status[user_id]["smoke_start"]
        mins = int((now - start).seconds / 60)
        warn = "⚠️ Exceeded 15 minutes!" if mins > 15 else "👍 Within time."
        user_status[user_id]["smoke_start"] = None
        await update.message.reply_text(f"🚬 Smoking ended — {mins} min\n{warn}")
        return

    await update.message.reply_text("❌ You are not in break.")


# ---------------------------------------------------------
# BUTTON HANDLER (TEXT -> COMMAND)
# ---------------------------------------------------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if text == "start work":      return await startwork(update, context)
    if text == "off work":        return await offwork(update, context)
    if text == "wc":              return await wc(update, context)
    if text == "eat":             return await eat(update, context)
    if text == "smoke":           return await smoke(update, context)
    if text == "back":            return await back(update, context)


# ---------------------------------------------------------
# BOT SETUP
# ---------------------------------------------------------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("startwork", startwork))
app.add_handler(CommandHandler("offwork", offwork))
app.add_handler(CommandHandler("wc", wc))
app.add_handler(CommandHandler("eat", eat))
app.add_handler(CommandHandler("smoke", smoke))
app.add_handler(CommandHandler("back", back))

# Buttons
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

app.run_polling()
