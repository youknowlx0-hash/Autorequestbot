import os
import json
import asyncio
from flask import Flask, request, render_template_string, redirect
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
PANEL_PASS = os.getenv("PANEL_PASS", "1234")

DB_FILE = "data.json"

# ---------- DB ----------
def load():
    try:
        return json.load(open(DB_FILE))
    except:
        return {"chats": {}, "stats": {}}

def save(db):
    json.dump(db, open(DB_FILE, "w"), indent=2)

db = load()

def get_chat(chat_id):
    if chat_id not in db["chats"]:
        db["chats"][chat_id] = {
            "time": 5,
            "enabled": False,
            "links": True,
            "media": True,
            "text": False,
            "ignore": []
        }
    return db["chats"][chat_id]

# ---------- WEB PANEL ----------
app_web = Flask(__name__)

LOGIN_HTML = """
<h2>🔐 Login</h2>
<form method="post">
Password: <input name="pass">
<input type="submit">
</form>
"""

PANEL_HTML = """
<h2>💀 FINAL BOSS PANEL</h2>
<form method="post">
Chat ID: <input name="chat"><br>
Time: <input name="time"><br>
Enabled(True/False): <input name="enabled"><br>
Links(True/False): <input name="links"><br>
Media(True/False): <input name="media"><br>
Text(True/False): <input name="text"><br>
<input type="submit">
</form>
<hr>
<h3>📊 Stats</h3>
<pre>{{stats}}</pre>
"""

logged = False

@app_web.route("/", methods=["GET", "POST"])
def login():
    global logged
    if not logged:
        if request.method == "POST":
            if request.form["pass"] == PANEL_PASS:
                logged = True
                return redirect("/panel")
        return LOGIN_HTML
    return redirect("/panel")

@app_web.route("/panel", methods=["GET", "POST"])
def panel():
    if request.method == "POST":
        chat = request.form["chat"]
        data = get_chat(chat)

        data["time"] = int(request.form["time"])
        data["enabled"] = request.form["enabled"] == "True"
        data["links"] = request.form["links"] == "True"
        data["media"] = request.form["media"] == "True"
        data["text"] = request.form["text"] == "True"

        save(db)

    return render_template_string(PANEL_HTML, stats=db["stats"])

# ---------- TELEGRAM COMMANDS ----------
async def panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌐 Open your Railway URL for panel")

async def set_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    data = get_chat(chat_id)
    data["time"] = int(context.args[0])
    save(db)
    await update.message.reply_text("⏱️ Time updated")

async def toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    data = get_chat(chat_id)
    data["enabled"] = not data["enabled"]
    save(db)
    await update.message.reply_text(f"⚡ Enabled: {data['enabled']}")

# ---------- AUTO DELETE ----------
async def auto_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    chat_id = str(update.effective_chat.id)
    user_id = update.message.from_user.id
    data = get_chat(chat_id)

    if not data["enabled"]:
        return

    member = await context.bot.get_chat_member(chat_id, user_id)
    if member.status in ["administrator", "creator"]:
        return

    msg = update.message
    delete = False

    if data["links"] and msg.text and ("http" in msg.text or "t.me" in msg.text):
        delete = True

    if data["media"] and (msg.photo or msg.video or msg.document):
        delete = True

    if data["text"] and msg.text:
        delete = True

    if delete:
        await asyncio.sleep(data["time"])
        try:
            await msg.delete()
            db["stats"][chat_id] = db["stats"].get(chat_id, 0) + 1
            save(db)
        except:
            pass

# ---------- RUN ----------
def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("panel", panel_cmd))
    app.add_handler(CommandHandler("settime", set_time))
    app.add_handler(CommandHandler("toggle", toggle))

    app.add_handler(MessageHandler(filters.ALL, auto_delete))

    app.run_polling()

# ---------- START ----------
if __name__ == "__main__":
    import threading
    threading.Thread(target=run_bot).start()
    app_web.run(host="0.0.0.0", port=8080)
