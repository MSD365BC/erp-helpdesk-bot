from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from app.config import BOT_TOKEN
from app.handlers.user_handler import (
    start,
    create_ticket_ui,
    handle_category,
    handle_text,
    my_ticket
)
from app.handlers.admin_handler import (
    admin_menu,
    update_status
)

def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_menu))

    app.add_handler(CallbackQueryHandler(create_ticket_ui, pattern="create_ticket"))
    app.add_handler(CallbackQueryHandler(my_ticket, pattern="my_ticket"))
    app.add_handler(CallbackQueryHandler(handle_category, pattern="cat_"))
    app.add_handler(CallbackQueryHandler(update_status, pattern="prog_|wait_|done_"))

    app.add_handler(MessageHandler(filters.TEXT, handle_text))

    app.run_polling()
