import httpx
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_KEY")
_http_client = httpx.AsyncClient()

async def send_message(chat_id: int, text: str):
    await _http_client.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text},
    )
