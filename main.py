from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import asyncio
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

# /del → reply to delete message
async def delete_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        try:
            await update.message.reply_to_message.delete()
            await update.message.delete()
        except:
            await update.message.reply_text("❌ Can't delete")
    else:
        await update.message.reply_text("Reply karo kisi message pe")

# /autodel 5 → delete own message after delay
async def auto_self_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sec = int(context.args[0])
        msg = await update.message.reply_text(f"⏱️ Deleting in {sec}s...")
        await asyncio.sleep(sec)
        await msg.delete()
        await update.message.delete()
    except:
        await update.message.reply_text("Use: /autodel 5")

# Auto delete EVERY user message (optional ON)
async def auto_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await asyncio.sleep(5)
        await update.message.delete()
    except:
        pass

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("del", delete_cmd))
    app.add_handler(CommandHandler("autodel", auto_self_delete))

    # optional: enable if sab auto delete karna hai
    # app.add_handler(MessageHandler(filters.ALL, auto_delete))

    print("User Control Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()ort=8080)
