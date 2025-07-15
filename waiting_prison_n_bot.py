import logging
import os
import asyncio
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import aiofiles

# === НАСТРОЙКИ ===
TOKEN = '7845152168:AAEL64jqb8ZCTO6hFwOgvZnZN5_-pBF1evk'
CHAT_ID = -1001593342025  # число
TIMEZONE = 'Asia/Yekaterinburg'
COUNTER_FILE = 'counter.txt'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)

async def get_day_count():
    if not os.path.exists(COUNTER_FILE):
        async with aiofiles.open(COUNTER_FILE, 'w') as f:
            await f.write('3')
        return 3
    async with aiofiles.open(COUNTER_FILE, 'r') as f:
        content = await f.read()
        return int(content.strip())

async def increment_day_count():
    count = await get_day_count() + 1
    async with aiofiles.open(COUNTER_FILE, 'w') as f:
        await f.write(str(count))
    return count

async def send_daily_message():
    count = await get_day_count()
    message = f"ждем никитоса день {count}"
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
        logging.info(f"✅ Отправлено: {message}")
        await increment_day_count()
    except Exception as e:
        logging.error(f"❌ Ошибка при отправке сообщения: {e}")

async def main(test_mode=False):
    if test_mode:
        logging.info("Тестовый режим — отправляем сообщение прямо сейчас")
        await send_daily_message()
    else:
        scheduler = AsyncIOScheduler(timezone=TIMEZONE)
        scheduler.add_job(send_daily_message, CronTrigger(hour=0, minute=0))
        scheduler.start()
        logging.info("Бот запущен. Ждём никича...")
        while True:
            await asyncio.sleep(60)

if __name__ == '__main__':
    import sys
    test = False
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test = True
    asyncio.run(main(test_mode=test))
