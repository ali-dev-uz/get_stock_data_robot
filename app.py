from aiogram import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from loader import dp
import middlewares
from twelvedata_real_time import connect_api
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    scheduler = AsyncIOScheduler()
    # dubai_tz = timezone('Asia/Dubai')
    # scheduler.timezone = dubai_tz
    # scheduler.add_job(xxx, trigger='cron', hour=9, minute=1)
    scheduler.add_job(connect_api, 'interval', minutes=1)

    # Start the scheduler
    scheduler.start()
    await set_default_commands(dispatcher)

    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)

