import os, requests, asyncio
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
GOFILE_TOKEN = os.getenv("GOFILE_TOKEN")
SESSION = os.getenv("SESSION_STRING")
CHANNEL_ID = -1003984525744  # tumhara channel

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
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

# /start command
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply(
        "**👋 Auto Upload Bot**\n\n"
        "Main tumhare `Save file` channel ki files ko auto Gofile par upload kar dunga.\n\n"
        "**Commands:**\n"
        "/help - Help\n"
        "/status - Bot status\n"
        "/wizard - Setup guide",
        buttons=[
            [Button.inline("🚀 Start Wizard", b'wizard')],
            [Button.inline("📊 Status", b'status')]
        ]
    )

# /help command
@client.on(events.NewMessage(pattern='/help'))
async def help(event):
    await event.reply(
        "**📖 Commands List**\n\n"
        "/start - Bot shuru karo\n"
        "/help - Ye message\n"
        "/status - Bot status\n"
        "/wizard - Setup guide\n"
        "Bas `Save file` channel mein file bhej do, main auto upload kar dunga."
    )

# /status command
@client.on(events.NewMessage(pattern='/status'))
async def status(event):
    await event.reply(f"✅ Bot Active hai\n📡 Monitoring Channel: `{CHANNEL_ID}`")

# /wizard command
@client.on(events.NewMessage(pattern='/wizard'))
async def wizard(event):
    await event.reply(
        "**🧙 Setup Wizard**\n\n"
        "Step 1: Bas `Save file` channel mein koi file bhej do.\n"
        "Step 2: Main usko auto download karke Gofile link de dunga.\n\n"
        "Ho gaya kaam!"
    )

# Button clicks
@client.on(events.CallbackQuery)
async def callback(event):
    if event.data == b'wizard':
        await wizard(event)
    if event.data == b'status':
        await status(event)

# Auto upload from channel - YAHAN FIX KIYA HAI
@client.on(events.NewMessage(chats=CHANNEL_ID, outgoing=True)) # <-- outgoing=True add kiya
async def auto_upload(event):
    if event.media:
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

async def main():
    await client.start()
    print(f"Bot Started... Monitoring Channel: {CHANNEL_ID}")
    await client.run_until_disconnected()

client.loop.run_until_complete(main())