import os
from datetime import datetime, time
import pytz
from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)

# =========================
# LOAD ENV
# =========================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# =========================
# TIMEZONE (WIB)
# =========================
WIB = pytz.timezone("Asia/Jakarta")

# =========================
# DATABASE SEDERHANA
# =========================
tickets = []
ticket_counter = 1

# =========================
# STATE FORM
# =========================
NAMA, DEPARTEMEN, ISSUE = range(3)

# =========================
# START MENU
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Buat Tiket", callback_data="buat_tiket")],
        [InlineKeyboardButton("📊 Status Ticket", callback_data="status")],
        [InlineKeyboardButton("🔄 Follow Up", callback_data="followup")],
        [InlineKeyboardButton("✅ Close Ticket", callback_data="close")],
    ]

    await update.message.reply_text(
        "Selamat datang di ERP Helpdesk Bot 🚀",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================
# BUTTON HANDLER
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "buat_tiket":
        await query.message.reply_text("Masukkan Nama Anda:")
        return NAMA

    elif query.data == "status":
        user_id = query.from_user.id
        user_tickets = [t for t in tickets if t["user_id"] == user_id]

        if not user_tickets:
            await query.message.reply_text("Belum ada tiket.")
            return

        msg = "📊 Status Tiket Anda:\n\n"
        for t in user_tickets:
            msg += f"{t['kode']} - {t['status']}\n"

        await query.message.reply_text(msg)

    elif query.data == "followup":
        await query.message.reply_text("Ketik pesan follow up Anda")

    elif query.data == "close":
        user_id = query.from_user.id
        for t in tickets:
            if t["user_id"] == user_id and t["status"] == "OPEN":
                t["status"] = "CLOSED"

        await query.message.reply_text("✅ Semua tiket Anda ditutup")

    return ConversationHandler.END


# =========================
# FORM INPUT
# =========================
async def input_nama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["nama"] = update.message.text
    await update.message.reply_text("Masukkan Departemen:")
    return DEPARTEMEN


async def input_departemen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["departemen"] = update.message.text
    await update.message.reply_text("Tuliskan Issue Anda:")
    return ISSUE


async def input_issue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ticket_counter

    user = update.message.from_user

    ticket_code = f"TCK-{ticket_counter:03d}"
    ticket_counter += 1

    ticket = {
        "kode": ticket_code,
        "nama": context.user_data["nama"],
        "departemen": context.user_data["departemen"],
        "issue": update.message.text,
        "user_id": user.id,
        "status": "OPEN",
        "created_at": datetime.now(WIB)
    }

    tickets.append(ticket)

    # kirim ke admin
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"""
📢 TIKET BARU

🎫 {ticket_code}
👤 {ticket['nama']}
🏢 {ticket['departemen']}
📝 {ticket['issue']}
🕒 {ticket['created_at'].strftime('%Y-%m-%d %H:%M:%S')}
"""
    )

    await update.message.reply_text(f"✅ Tiket berhasil dibuat: {ticket_code}")

    return ConversationHandler.END


# =========================
# FOLLOW UP
# =========================
async def handle_followup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"""
🔄 FOLLOW UP

👤 {user.first_name}
💬 {update.message.text}
🕒 {datetime.now(WIB).strftime('%Y-%m-%d %H:%M:%S')}
"""
    )


# =========================
# AUTO REPORT KE ADMIN
# =========================
async def send_daily_report(context: ContextTypes.DEFAULT_TYPE):
    open_tickets = [t for t in tickets if t["status"] == "OPEN"]

    if not open_tickets:
        message = "✅ Tidak ada tiket OPEN"
    else:
        message = "📊 LIST TIKET BELUM SELESAI:\n\n"
        for t in open_tickets:
            message += f"{t['kode']} - {t['nama']} ({t['departemen']})\n"

    await context.bot.send_message(chat_id=ADMIN_ID, text=message)


# =========================
# MAIN
# =========================
def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Conversation
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="buat_tiket")],
        states={
            NAMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_nama)],
            DEPARTEMEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_departemen)],
            ISSUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_issue)],
        },
        fallbacks=[],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_followup))

    # =========================
    # SCHEDULER (WIB)
    # =========================
    job_queue = app.job_queue

    job_queue.run_daily(
        send_daily_report,
        time=time(hour=8, minute=0, tzinfo=WIB)
    )

    job_queue.run_daily(
        send_daily_report,
        time=time(hour=13, minute=0, tzinfo=WIB)
    )

    print("Bot jalan + scheduler WIB aktif...")
    app.run_polling()
