from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

BOT_TOKEN = "7684673083:AAG_hu6hC1Em6osAEg5FjlEmfUdtalhNJvA"

user_status = {}

# ---------------------------------------------------------
# CHECK-IN
# ---------------------------------------------------------
async def checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    full_name = update.effective_user.full_name

    if user_id in user_status and user_status[user_id].get("checkin_time"):
        start = user_status[user_id]["checkin_time"].strftime("%Y-%m-%d %H:%M:%S")
        await update.message.reply_text(
            f"❌ You already checked in at **{start}**.\nPlease /checkout first.",
            parse_mode="Markdown"
        )
        return

    now = datetime.now()
    user_status[user_id] = {
        "checkin_time": now,
        "wc_start": None,
        "eat_start": None,
        "smoke_start": None
    }

    await update.message.reply_text(
        f"✔️ Check-in successful!\n👤 {full_name}\n🕒 {now.strftime('%Y-%m-%d %H:%M:%S')}"
    )


# ---------------------------------------------------------
# CHECK-OUT
# ---------------------------------------------------------
async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    full_name = update.effective_user.full_name

    if user_id not in user_status or user_status[user_id]["checkin_time"] is None:
        await update.message.reply_text("❌ You have not checked in.")
        return

    checkin_time = user_status[user_id]["checkin_time"]
    checkout_time = datetime.now()

    duration = checkout_time - checkin_time
    hours = duration.seconds // 3600
    minutes = (duration.seconds % 3600) // 60

    # Reset
    user_status[user_id] = {
        "checkin_time": None,
        "wc_start": None,
        "eat_start": None,
        "smoke_start": None
    }

    await update.message.reply_markdown(
        f"✔️ **Check-out complete!**\n\n"
        f"👤 *{full_name}*\n"
        f"🟢 Check-in: {checkin_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"🔴 Check-out: {checkout_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"⏳ **Total time:** {hours}h {minutes}m"
    )


# ---------------------------------------------------------
# WC START
# ---------------------------------------------------------
async def wc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    full_name = update.effective_user.full_name

    if user_id not in user_status or user_status[user_id]["checkin_time"] is None:
        await update.message.reply_text("❌ You must /checkin before using WC.")
        return

    if user_status[user_id].get("eat_start"):
        await update.message.reply_text("❌ You are currently eating. Use /back first.")
        return

    if user_status[user_id].get("smoke_start"):
        await update.message.reply_text("❌ You are smoking. Use /back first.")
        return

    if user_status[user_id].get("wc_start"):
        await update.message.reply_text("❌ You are already in WC. Use /back to end it.")
        return

    now = datetime.now()
    user_status[user_id]["wc_start"] = now

    await update.message.reply_text(
        f"🚾\n👤 {full_name}\n WC started at {now.strftime('%Y-%m-%d %H:%M:%S')}"
    )


# ---------------------------------------------------------
# EAT START
# ---------------------------------------------------------
async def eat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    full_name = update.effective_user.full_name

    if user_id not in user_status or user_status[user_id]["checkin_time"] is None:
        await update.message.reply_text("❌ You must /checkin before eating.")
        return

    if user_status[user_id].get("wc_start"):
        await update.message.reply_text("❌ You are currently in WC. Use /back first.")
        return

    if user_status[user_id].get("smoke_start"):
        await update.message.reply_text("❌ You are smoking. Use /back first.")
        return

    if user_status[user_id].get("eat_start"):
        await update.message.reply_text("❌ You are already eating. Use /back to end it.")
        return

    now = datetime.now()
    user_status[user_id]["eat_start"] = now

    await update.message.reply_text(
        f"🍽\n👤 {full_name}\n Eating started at {now.strftime('%Y-%m-%d %H:%M:%S')}"
    )


# ---------------------------------------------------------
# SMOKING
# ---------------------------------------------------------
async def smoke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    full_name = update.effective_user.full_name

    if user_id not in user_status or user_status[user_id]["checkin_time"] is None:
        await update.message.reply_text("❌ You must /checkin before smoking.")
        return

    if user_status[user_id].get("wc_start"):
        await update.message.reply_text("❌ You are currently in WC. Please /back first.")
        return

    if user_status[user_id].get("eat_start"):
        await update.message.reply_text("❌ You are currently eating. Please /back first.")
        return

    if user_status[user_id].get("smoke_start"):
        await update.message.reply_text("❌ You are already smoking. Use /back to end it.")
        return

    now = datetime.now()
    user_status[user_id]["smoke_start"] = now

    await update.message.reply_text(
        f"🚬\n👤 {full_name}\n Smoking started at {now.strftime('%Y-%m-%d %H:%M:%S')}."
    )


# ---------------------------------------------------------
# BACK (END ANY BREAK)
# ---------------------------------------------------------
async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    full_name = update.effective_user.full_name
    now = datetime.now()

    # WC
    if user_status[user_id].get("wc_start"):
        start = user_status[user_id]["wc_start"]
        diff = now - start
        minutes = diff.seconds // 60
        warning = "⚠️ WC exceeded 15 minutes!" if minutes > 15 else "👍 Within 15 minutes."
        await update.message.reply_text(f"🚾 WC ended. Duration: {minutes} min.\n{warning}")
        user_status[user_id]["wc_start"] = None
        return

    # Eating
    if user_status[user_id].get("eat_start"):
        start = user_status[user_id]["eat_start"]
        diff = now - start
        minutes = diff.seconds // 60
        warning = "⚠️ Eating exceeded 30 minutes!" if minutes > 30 else "👍 Within 30 minutes."
        await update.message.reply_text(f"🍽 Eating ended. Duration: {minutes} min.\n{warning}")
        user_status[user_id]["eat_start"] = None
        return

    # Smoking
    if user_status[user_id].get("smoke_start"):
        start = user_status[user_id]["smoke_start"]
        diff = now - start
        minutes = diff.seconds // 60
        warning = "⚠️ Smoking exceeded 15 minutes!" if minutes > 15 else "👍 Within 15 minutes."
        await update.message.reply_text(f"🚬 Smoking ended. Duration: {minutes} min.\n{warning}")
        user_status[user_id]["smoke_start"] = None
        return

    await update.message.reply_text("❌ You are not in WC, Eating, or Smoking.")


# ---------------------------------------------------------
# BOT SETUP
# ---------------------------------------------------------
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("checkin", checkin))
app.add_handler(CommandHandler("checkout", checkout))
app.add_handler(CommandHandler("wc", wc))
app.add_handler(CommandHandler("eat", eat))
app.add_handler(CommandHandler("smoke", smoke))
app.add_handler(CommandHandler("back", back))

app.run_polling()
