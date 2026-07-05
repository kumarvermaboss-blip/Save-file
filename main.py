import os, requests, time
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError # Nayi line

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GOFILE_TOKEN = os.getenv("GOFILE_TOKEN")
GOFILE_FOLDER_ID = os.getenv("GOFILE_FOLDER_ID")

client = TelegramClient('bot', API_ID, API_HASH)

def upload_gofile(path):
    try:
        filename = os.path.basename(path)
        url = "https://upload.gofile.io/uploadFile"
        files = {'file': (filename, open(path, 'rb'))}
        data = {'token': GOFILE_TOKEN, 'folderId': GOFILE_FOLDER_ID}
        res = requests.post(url, data=data, files=files, timeout=600)
        res_json = res.json()
        if res_json.get('status') == 'ok':
            folder_link = f"https://gofile.io/d/{GOFILE_FOLDER_ID}"
            file_link = res_json['data']['downloadPage']
            return f"✅ Upload Complete!\n\n📁 **Folder:** {folder_link}\n📄 **File:** {file_link}"
        else:
            return f"❌ Upload failed: {res_json.get('message')}"
    except Exception as e:
        return f"❌ Error: {e}"

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Bot Active ✅\nSab files folder mein jayengi")

@client.on(events.NewMessage(func=lambda e: e.media))
async def auto_upload(event):
    msg = await event.reply("📥 Downloading...")
    try:
        path = await event.download_media("downloads/")
        size = round(os.path.getsize(path)/1024/1024, 2)
        await msg.edit(f"📤 Uploading...\n`{os.path.basename(path)}` - {size} MB")
        result = upload_gofile(path)
        await msg.edit(result)
        os.remove(path)
    except Exception as e:
        await msg.edit(f"❌ Error: {e}")

print("Bot Started...")
while True: # FloodWait ke liye loop
    try:
        client.start(bot_token=BOT_TOKEN)
        client.run_until_disconnected()
    except FloodWaitError as e:
        print(f"FloodWait: {e.seconds} seconds wait karna hai")
        time.sleep(e.seconds + 5)