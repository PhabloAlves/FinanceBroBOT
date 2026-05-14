from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.telegram import send_message
from app.api.v1.routes.endpoints import router
from app.services.google_sheets import get_daily_summary

app = FastAPI()

app.include_router(router, prefix="/api/v1")

async def daily_job():
    summary = await get_daily_summary()
    await send_message(summary)

scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
scheduler.add_job(daily_job, "cron", hour=23, minute=59)
scheduler.start()
