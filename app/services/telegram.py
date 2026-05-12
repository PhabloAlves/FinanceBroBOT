import httpx
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_KEY")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

async def send_message(text: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": text},
        )
