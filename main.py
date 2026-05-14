from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.telegram import send_message
from app.api.v1.routes.endpoints import router
from app.services.finance_db import get_daily_summary, get_all_users
from app.db.database import engine, Base

app = FastAPI()
app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def daily_job():
    for user_id in await get_all_users():
        summary = await get_daily_summary(user_id)
        await send_message(user_id, summary)

scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
scheduler.add_job(daily_job, "cron", hour=23, minute=59)
scheduler.start()
