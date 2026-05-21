from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.services.ticket_service import create_ticket, get_user_tickets

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Buat Tiket", callback_data="create_ticket")],
        [InlineKeyboardButton("📊 Status Tiket Saya", callback_data="my_ticket")]
    ]

    await update.message.reply_text(
        "✨ ERP Helpdesk System",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def create_ticket_ui(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("⚙️ ERP", callback_data="cat_erp")],
        [InlineKeyboardButton("📊 Report", callback_data="cat_report")],
        [InlineKeyboardButton("🐞 Bug", callback_data="cat_bug")]
    ]

    await query.message.reply_text(
        "Pilih kategori:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["category"] = query.data.replace("cat_", "")
    context.user_data["step"] = "desc"

    await query.message.reply_text("Jelaskan kendala:")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("step") == "desc":
        ticket_id = create_ticket(
            update.message.from_user.id,
            update.message.from_user.username,
            context.user_data["category"],
            update.message.text
        )

        await update.message.reply_text(
            f"✅ Tiket dibuat!\nID: {ticket_id}"
        )

        context.user_data.clear()

async def my_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    tickets = get_user_tickets(query.from_user.id)

    if not tickets:
        await query.message.reply_text("Tidak ada tiket")
        return

    msg = "\n".join([f"ID {t.id} - {t.status}" for t in tickets])
    await query.message.reply_text(msg)
