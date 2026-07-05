import os, requests
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
GOFILE_TOKEN = os.getenv("GOFILE_TOKEN")
SESSION = os.getenv("SESSION_STRING")

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
os.makedirs("downloads", exist_ok=True)

def upload_gofile(path):
    url = "https://upload.gofile.io/uploadfile"
    files = {'file': open(path, 'rb')}
    data = {'folderId': GOFILE_TOKEN}
    res = requests.post(url, data=data, files=files).json()
    if res['status'] == 'ok':
        return f"https://gofile.io/d/{res['data']['code']}"
    return "Upload failed"

@client.on(events.NewMessage(incoming=True, from_users='me'))
async def handler(event):
    if event.media:
        msg = await event.reply("📥 Downloading... 0%")
        path = await event.download_media("downloads/")
        size = round(os.path.getsize(path)/1024/1024, 2)
        await msg.edit(f"📤 Uploading {os.path.basename(path)} {size} MB")
        
        link = upload_gofile(path)
        await msg.edit(f"✅ Done 100%\n\n📁 {link}")
        os.remove(path)

print("Bot Started... Ready")
client.run_until_disconnected()