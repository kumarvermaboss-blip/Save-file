import os, requests, asyncio
from telethon import TelegramClient, events

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
GOFILE_TOKEN = os.getenv("GOFILE_TOKEN")

client = TelegramClient('bot_session', API_ID, API_HASH)
os.makedirs("downloads", exist_ok=True)
logged_in = False
TEMP_PHONE = "" # phone yahan save hoga

def upload_file(path):
    url = "https://upload.gofile.io/uploadfile"
    files = {'file': open(path, 'rb')}
    data = {'folderId': GOFILE_TOKEN}
    res = requests.post(url, data=data, files=files).json()
    return f"https://gofile.io/d/{GOFILE_TOKEN}"

@client.on(events.NewMessage(incoming=True, from_users='me'))
async def handler(event):
    global logged_in, TEMP_PHONE
    
    # 1. /login 92xxxxxxxxxx
    if event.text.startswith("/login "):
        TEMP_PHONE = event.text.split(" ")[1]
        await client.send_code_request(TEMP_PHONE)
        await event.reply(f"📱 Code bhej diya `{TEMP_PHONE}` par.\nAb reply karo: `/code 12345`")
        return

    # 2. /code 12345
    if event.text.startswith("/code "):
        code = event.text.split(" ")[1]
        try:
            await client.sign_in(TEMP_PHONE, code)
            logged_in = True
            await event.reply("✅ Login ho gaya! Ab file ya link bhejo.")
        except Exception as e:
            if "2FA" in str(e): await event.reply("🔒 2FA: `/password tumharapassword`")
            else: await event.reply(f"❌ {e}")
        return
        
    # 3. /password xxxx
    if event.text.startswith("/password "):
        pwd = event.text.split(" ", 1)[1]
        await client.sign_in(password=pwd); logged_in = True
        await event.reply("✅ 2FA ke sath Login ho gaya!")
        return

    if not logged_in:
        await event.reply("⚠️ Pehle `/login +92xxxxxxxxxx` karo")
        return

    if event.media:
        msg = await event.reply("📥 Downloading...")
        path = await event.download_media("downloads/")
        link = upload_file(path)
        await msg.edit(f"✅ Done 100%\n\nFolder: {link}")
        os.remove(path)

print("Bot Started... Waiting for /login")
client.start() # ab phone nahi mangega
client.run_until_disconnected()