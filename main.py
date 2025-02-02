import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from config import TOKEN
from database import create_db_pool
from handlers import show_categories, show_cars
from commands import set_main_menu
from utils import load_messages

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()
db_pool = None

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_name = message.from_user.first_name or "Друже"
    messages = load_messages()
    start_message = messages["start_message"].format(name=user_name)
    await message.answer(start_message)

@dp.message(Command("categories"))
async def categories_handler(message: Message):
    await show_categories(message, db_pool)

@dp.callback_query(lambda c: c.data.startswith("category_"))
async def cars_handler(callback: CallbackQuery):
    await show_cars(callback, db_pool, bot)

async def main():
    global db_pool
    db_pool = await create_db_pool()
    await set_main_menu(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())