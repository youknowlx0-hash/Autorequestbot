import json
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from configparser import ConfigParser
import os

# Load .env config
from dotenv import load_dotenv
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
UPDATE_CHANNEL = os.getenv("UPDATE_CHANNEL")

db_file = "database.json"

def load_db():
    try:
        with open(db_file, "r") as f:
            return json.load(f)
    except:
        return {"channels": {}}

def save_db(data):
    with open(db_file, "w") as f:
        json.dump(data, f, indent=4)

app = Client("Autorequestbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ---------- Start Command ----------
@app.on_message(filters.command("start"))
async def start(_, message: Message):
    text = (
        "🤖 **Welcome to 𝐇𝐄𝐗 𝐒𝐇𝐀𝐃𝐎𝐖 𝐁𝐨𝐭𝐬 Auto Join‑Accept Bot!**\n\n"
        "This bot automatically approves join requests in your channel or group.\n\n"
        f"👉 Important: To use me, you must first join our update channel:\n"
        f"🔔 Join {UPDATE_CHANNEL}\n\n"
        "Once you're a member, click the button below to add me to your channel."
    )

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("➕ Add Your Channel", url="https://t.me/YourBotUsername?start=add")]]
    )
    await message.reply_text(text, reply_markup=keyboard, disable_web_page_preview=True)

# ---------- Auto Approve Join Requests ----------
@app.on_message(filters.chat_type.groups & filters.status_update.new_chat_members)
async def approve_request(_, message: Message):
    try:
        for member in message.new_chat_members:
            if member.is_bot:
                continue
            await message.chat.promote_member(
                member.id,
                can_change_info=True,
                can_post_messages=True,
                can_edit_messages=True,
                can_delete_messages=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_manage_topics=True
            )
    except Exception as e:
        print(f"Error approving join request: {e}")

# ---------- Admin Panel ----------
@app.on_message(filters.user(ADMIN_ID) & filters.command("broadcast"))
async def broadcast(_, message: Message):
    db = load_db()
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        await message.reply("Send a message after /broadcast to send to all channels.")
        return

    for channel_id in db["channels"]:
        try:
            await app.send_message(int(channel_id), text)
        except Exception as e:
            print(f"Failed to send to {channel_id}: {e}")

    await message.reply("✅ Broadcast sent to all channels!")

# ---------- Add Channel ----------
@app.on_message(filters.command("addchannel"))
async def add_channel(_, message: Message):
    db = load_db()
    try:
        channel_id = message.chat.id
        db["channels"][str(channel_id)] = {"title": message.chat.title}
        save_db(db)
        await message.reply(f"✅ Channel **{message.chat.title}** added to auto-approve list.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# ---------- Fallback for unwanted messages ----------
@app.on_message(filters.private)
async def fallback(_, message: Message):
    await message.reply("Use /start to interact with me!")

# ---------- Run the Bot ----------
print("H3x Shadow Auto Accept Bot is running...")
app.run()
