import os, requests, re, asyncio, time
from telethon import TelegramClient, events

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")
GOFILE_TOKEN = os.getenv("GOFILE_TOKEN")

client = TelegramClient('bot_session', API_ID, API_HASH)
os.makedirs("downloads", exist_ok=True)
logged_in = False

def format_size(bytes): return f"{bytes / 1024 / 1024:.2f} MB"
async def delete_after(msg, seconds=5): await asyncio.sleep(seconds); await msg.delete()

@client.on(events.NewMessage(incoming=True, from_users='me'))
async def handler(event):
    global logged_in
    if event.text == "/login":
        await event.reply(f"📱 `{PHONE}` par code bhej diya.\nReply karo: `/code 12345`")
        await client.send_code_request(PHONE)
        return
    if event.text.startswith("/code "):
        code = event.text.split(" ")[1]
        try:
            await client.sign_in(PHONE, code)
            logged_in = True
            await event.reply("✅ Login ho gaya! Ab file/link bhej sakte ho.")
        except Exception as e:
            if "2FA" in str(e): await event.reply("🔒 2FA: `/password tumharapassword`")
            else: await event.reply(f"❌ {e}")
        return
    if event.text.startswith("/password "):
        pwd = event.text.split(" ", 1)[1]
        await client.sign_in(password=pwd); logged_in = True
        await event.reply("✅ 2FA ke sath Login ho gaya!")
        return
    if not logged_in: await event.reply("⚠️ Pehle `/login` karo"); return
    
    # Yahan tumhara file/link wala code aayega
    await event.reply("✅ Login ok hai. Ab file bhej do.")

print("Bot Started... Waiting for /login")
client.start()
client.run_until_disconnected()