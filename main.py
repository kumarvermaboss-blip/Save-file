import os, requests
from telethon import TelegramClient, events

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
os.makedirs("downloads", exist_ok=True)

def upload_gofile(path):
    try:
        filename = os.path.basename(path)
        url = "https://upload.gofile.io/uploadFile"
        
        files = {'file': (filename, open(path, 'rb'))}
        data = {'folderId': ''}
            
        res = requests.post(url, data=data, files=files, timeout=300).json()
        
        if res['status'] == 'ok':
            link = res['data']['downloadPage']
            return f"✅ Upload Complete!\n\n📁 **Link:** {link}"
        else:
            return f"❌ Upload failed: {res.get('message', 'Unknown')}"
            
    except Exception as e:
        return f"❌ Error: {e}"

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("**👋 Gofile Upload Bot**\nMujhe koi bhi file bhej do.")

@client.on(events.NewMessage(func=lambda e: e.media))
async def auto_upload(event):
    msg = await event.reply("📥 Downloading...")
    try:
        path = await event.download_media("downloads/")
        size = round(os.path.getsize(path)/1024/1024, 2)
        await msg.edit(f"📤 Uploading to Gofile...\n`{os.path.basename(path)}` - {size} MB")
        
        result = upload_gofile(path)
        await msg.edit(result)
        os.remove(path)
    except Exception as e:
        await msg.edit(f"❌ Error: {e}")

print("Bot Started... PM mein file bhejo")
client.run_until_disconnected()