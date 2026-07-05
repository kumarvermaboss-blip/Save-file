import os, requests
from telethon import TelegramClient, events, Button

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN") # BotFather wala token
GOFILE_TOKEN = os.getenv("GOFILE_TOKEN")

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
os.makedirs("downloads", exist_ok=True)

def upload_gofile(path):
    try:
        url = "https://upload.gofile.io/uploadfile"
        files = {'file': open(path, 'rb')}
        data = {'token': GOFILE_TOKEN}
        res = requests.post(url, data=data, files=files).json()
        if res['status'] == 'ok':
            return f"https://gofile.io/d/{res['data']['code']}"
        return "Upload failed: " + str(res)
    except Exception as e:
        return "Error: " + str(e)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply(
        "**👋 Gofile Upload Bot**\n\n"
        "Mujhe koi bhi file bhej do, main Gofile ka link de dunga.\n\n"
        "**Commands:**\n"
        "/help - Help\n"
        "/status - Bot status"
    )

@client.on(events.NewMessage(pattern='/help'))
async def help(event):
    await event.reply("Bas mujhe PM mein file bhej do. Main auto upload karke link de dunga ✅")

# YEHI MAIN KAAM HAI
@client.on(events.NewMessage(func=lambda e: e.media)) # Koi bhi file aaye
async def auto_upload(event):
    msg = await event.reply("📥 Downloading... 0%")
    try:
        path = await event.download_media("downloads/")
        size = round(os.path.getsize(path)/1024/1024, 2)
        await msg.edit(f"📤 Uploading to Gofile...\n`{os.path.basename(path)}` - {size} MB")
        
        link = upload_gofile(path)
        await msg.edit(f"✅ Upload Complete!\n\n📁 **Link:** {link}")
        os.remove(path)
    except Exception as e:
        await msg.edit(f"❌ Error: {e}")

print("Bot Started... PM mein file bhejo")
client.run_until_disconnected()