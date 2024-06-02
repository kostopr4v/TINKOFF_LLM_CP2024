import asyncio
import logging
import sys
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
import sqlite3
import message_router

BOT_TOKEN = "7180497967:AAFYTjx5HnWJbN1rMB4Qvrlv79MO5kyuUqs"
bot = Bot(BOT_TOKEN, parse_mode="HTML")
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS likes (user_id, like, query, answer)")
conn.commit()


async def on_startup():
    sqlite3.connect("database.db")
    print("Подключён к БД")


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    await bot.delete_webhook(drop_pending_updates=True)
    dp = Dispatcher()
    dp.include_routers(message_router.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
