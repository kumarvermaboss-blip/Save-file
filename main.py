import os, requests, re, asyncio, time
from telethon import TelegramClient, events

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH") 
PHONE = os.getenv("PHONE")
GOFILE_TOKEN = os.getenv("GOFILE_TOKEN")

client = TelegramClient('bot_session', API_ID, API_HASH)
os.makedirs("downloads", exist_ok=True)

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
    try:
        await msg.edit(text)
    except: pass

async def delete_after(msg, seconds=5):
    await asyncio.sleep(seconds)
    try:
        await msg.delete()
    except: pass

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private: return
    
    # 1. Forward wali video
    if event.media and (event.video or event.document):
        size = format_size(event.file.size)
        msg = await event.reply(f"📥 Downloading...\nSize: {size}\nProgress: 0%")
        start = time.time()
        
        path = await event.download_media("downloads/", progress_callback=lambda c,t: asyncio.create_task(progress_callback(c,t,msg,"Video",start)))
        
        await msg.edit("📤 Uploading to Gofile...")
        upload_gofile_folder(path, GOFILE_TOKEN) 
        await msg.edit(f"✅ Done 100%\n\nFolder: https://gofile.io/d/{GOFILE_TOKEN}")
        asyncio.create_task(delete_after(msg, 5)) # 5 sec baad delete
        os.remove(path)
    
    # 2. Link with Range 1-100
    elif event.text and "t.me/" in event.text:
        text = event.text
        match = re.search(r't\.me/(.*?)/(\d+)-(\d+)', text)
        
        if match: # Range wala
            channel = match.group(1)
            start = int(match.group(2))
            end = int(match.group(3))
            main_msg = await event.reply(f"✅ `{start}` se `{end}` tak shuru kar raha hun...")
            
            for i in range(start, end + 1):
                try:
                    msg = await client.get_messages(channel, ids=i)
                    if msg and msg.media:
                        size = format_size(msg.file.size)
                        status = await event.reply(f"📥 Post {i}\nSize: {size}\nProgress: 0%")
                        start = time.time()
                        
                        path = await msg.download_media("downloads/", progress_callback=lambda c,t: asyncio.create_task(progress_callback(c,t,status,f"Post {i}",start)))
                        
                        await status.edit(f"📤 Post {i} Uploading...")
                        upload_gofile_folder(path, GOFILE_TOKEN)
                        await status.edit(f"✅ Post {i} Done 100%")
                        asyncio.create_task(delete_after(status, 5)) # 5 sec baad delete
                        os.remove(path)
                        await asyncio.sleep(3)
                except: 
                    pass # error wale bhi delete
            await main_msg.edit(f"🎉 Sab Ho gaya!\nFolder: https://gofile.io/d/{GOFILE_TOKEN}")
        
        else: # Single link
            try:
                msg = await client.get_messages(None, link=text)
                if msg and msg.media:
                    size = format_size(msg.file.size)
                    status = await event.reply(f"📥 Downloading...\nSize: {size}\nProgress: 0%")
                    start = time.time()
                    
                    path = await msg.download_media("downloads/", progress_callback=lambda c,t: asyncio.create_task(progress_callback(c,t,status,"Video",start)))
                    
                    await status.edit("📤 Uploading to Gofile...")
                    upload_gofile_folder(path, GOFILE_TOKEN)
                    await status.edit(f"✅ Done 100%\nFolder: https://gofile.io/d/{GOFILE_TOKEN}")
                    asyncio.create_task(delete_after(status, 5)) # 5 sec baad delete
                    os.remove(path)
            except Exception as e:
                await event.reply(f"❌ Error: {e}")

print("Bot Started...")
client.start(phone=PHONE)
client.run_until_disconnected()
