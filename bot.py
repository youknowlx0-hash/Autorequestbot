from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Message auto delete function
async def delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.delete()
    except:
        pass

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Har message ko delete karega
    app.add_handler(MessageHandler(filters.ALL, delete_message))

    print("Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
