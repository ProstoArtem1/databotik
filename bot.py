import asyncio

from aiogram import Bot, Dispatcher
from registration_handlers import router

from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_router(router)

async def main():
    await dp.start_polling(bot)


from match_handlers import router as match_router

dp.include_router(match_router)

if __name__ == "__main__":
    asyncio.run(main())