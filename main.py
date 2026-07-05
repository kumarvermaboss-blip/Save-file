import os, requests
from telethon import TelegramClient, events

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
os.makedirs("downloads", exist_ok=True)

FOLDER_ID = None # Spelling theek kar di

def create_gofile_folder():
    global FOLDER_ID
    if FOLDER_ID: 
        return FOLDER_ID
    
    try:
        url = "https://api.gofile.io/createFolder"
        data = {'folderName': 'Telegram Uploads'}
        res = requests.post(url, data=data, timeout=30).json()
        
        if res.get('status') == 'ok':
            FOLDER_ID = res['data']['id']
            return FOLDER_ID
    except:
        pass
    return None

def upload_gofile(path):
    try:
        folder_id = create_gofile_folder()
        filename = os.path.basename(path)
        url = "https://upload.gofile.io/uploadFile"
        
        files = {'file': (filename, open(path, 'rb'))}
        data = {'folderId': folder_id} if folder_id else {}
            
        res = requests.post(url, data=data, files=files, timeout=300).json()
        
        if res.get('status') == 'ok':
            folder_link = f"https://gofile.io/d/{folder_id}" if folder_id else "N/A"
            file_link = res['data']['downloadPage']
            return f"✅ Upload Complete!\n\n📁 **Folder:** {folder_link}\n📄 **File:** {file_link}"
        else:
            return f"❌ Upload failed: {res.get('message', 'Unknown')}"
            
    except Exception as e:
        return f"❌ Error: {e}"

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("**👋 Gofile Upload Bot**\nMujhe koi bhi file bhej do. Sab 1 hi folder mein jama hongi.")

@client.on(events.NewMessage(func=lambda e: e.media))
async def auto_upload(event):
    msg = await event.reply("📥 Downloading...")
    try:
        path = await event.download_media("downloads/")
        size = round(os.path.getsize(path)/1024/1024, 2)
        await msg.edit(f"📤 Uploading to Folder...\n`{os.path.basename(path)}` - {size} MB")
        
        result = upload_gofile(path)
        await msg.edit(result)
        os.remove(path)
    except Exception as e:
        await msg.edit(f"❌ Error: {e}")

print("Bot Started... PM mein file bhejo")
client.run_until_disconnected()