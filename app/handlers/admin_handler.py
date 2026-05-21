from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.services.ticket_service import get_all_tickets, update_ticket
from app.config import ADMIN_ID

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    tickets = get_all_tickets()

    for t in tickets:
        keyboard = [
            [
                InlineKeyboardButton("🔄", callback_data=f"prog_{t.id}"),
                InlineKeyboardButton("⏳", callback_data=f"wait_{t.id}"),
                InlineKeyboardButton("✅", callback_data=f"done_{t.id}")
            ]
        ]

        await update.message.reply_text(
            f"🎫 ID {t.id}\n{t.description}\nStatus: {t.status}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def update_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action, ticket_id = query.data.split("_")
    ticket_id = int(ticket_id)

    if action == "prog":
        status = "IN PROGRESS"
    elif action == "wait":
        status = "WAITING USER"
    else:
        status = "DONE"

    update_ticket(ticket_id, status)

    await query.message.reply_text(
        f"✅ Tiket {ticket_id} → {status}"
    )
