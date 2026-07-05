import os, requests, re, asyncio, time
from telethon import TelegramClient, events

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")
GOFILE_TOKEN = os.getenv("GOFILE_TOKEN")

client = TelegramClient('bot_session', API_ID, API_HASH)
os.makedirs("downloads", exist_ok=True)

logged_in = False # shuru mein login nahi hua

def upload_gofile_folder(filepath, folder_token):
    try:
        url = "https://upload.gofile.io/uploadfile"
        files = {'file': open(filepath, 'rb')}
        data = {'folderId': folder_token}
        res = requests.post(url, data=data, files=files, timeout=1200).json()
        return f"https://gofile.io/d/{folder_token}"
    except Exception as e:
        return f"Error: {e}"

def format_size(bytes):
    return f"{bytes / 1024 / 1024:.2f} MB"

def format_speed(bytes, seconds):
    if seconds == 0: return "0 MB/s"
    return f"{(bytes / 1024 / 1024) / seconds:.2f} MB/s"

async def progress_callback(current, total, msg, name, start_time):
    percent = current * 100 / total
    speed = format_speed(current, time.time() - start_time)
    size = format_size(total)
    if percent < 25: p = "25%"
    elif percent < 50: p = "50%"
    elif percent < 75: p = "75%"
    else: p = "100%"
    text = f"📥 {name}\nSize: {size}\nProgress: {p}\nSpeed: {speed}"
    try: await msg.edit(text)
    except: pass

async def delete_after(msg, seconds=5):
    await asyncio.sleep(seconds)
    try: await msg.delete()
    except: pass

@client.on(events.NewMessage(incoming=True, from_users='me')) # sirf tumhare msg
async def handler(event):
    global logged_in

    # 1. /login command
    if event.text == "/login":
        await event.reply(f"📱 `{PHONE}` par code bhej diya hai.\nAb code reply karo is format mein:\n`/code 12345`")
        await client.send_code_request(PHONE)
        return

    # 2. /code command
    if event.text.startswith("/code "):
        code = event.text.split(" ")[1]
        try:
            await client.sign_in(PHONE, code)
            logged_in = True
            await event.reply("✅ Login ho gaya! Ab link ya file bhej sakte ho.")
        except Exception as e:
            if "2FA" in str(e):
                await event.reply("🔒 2FA password chahiye. Is tarah bhejo:\n`/password tumharapassword`")
            else:
                await event.reply(f"❌ Error: {e}")
        return

    # 3. /password command
    if event.text.startswith("/password "):
        pwd = event.text.split(" ", 1)[1]
        try:
            await client.sign_in(password=pwd)
            logged_in = True
            await event.reply("✅ 2FA ke sath Login ho gaya!")
        except Exception as e:
            await event.reply(f"❌ Error: {e}")
        return

    if not logged_in:
        await event.reply("⚠️ Pehle `/login` karo")
        return

    # 4. Baaki kaam - File / Link wala same code
    if event.media and (event.video or event.document):
        size = format_size(event.file.size)
        msg = await event.reply(f"📥 Downloading...\nSize: {size}\nProgress: 0%")
        start = time.time()
        path = await event.download_media("downloads/", progress_callback=lambda c,t: asyncio.create_task(progress_callback(c,t,msg,"Video",start)))
        await msg.edit("📤 Uploading to Gofile...")
        upload_gofile_folder(path, GOFILE_TOKEN)
        await msg.edit(f"✅ Done 100%\n\nFolder: https://gofile.io/d/{GOFILE_TOKEN}")
        asyncio.create_task(delete_after(msg, 5))
        os.remove(path)

print("Bot Started... Waiting for /login")
client.start()
client.run_until_disconnected()