import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram import F
from dotenv import load_dotenv

from telegram_bot.schedule_extracting import get_week_schedule, get_daily_schedule

load_dotenv()
# Токен вашего бота
API_TOKEN = os.getenv("API_TOKEN", "8192247154:AAE2mFLGN__f9kA3IQYyJayZZEzodje_1i8")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Создаем клавиатуру с меню
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📅 Расписание на день"),
            KeyboardButton(text="📆 Расписание на неделю")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        "Привет! Я бот для просмотра расписания.\n"
        "Выберите опцию из меню ниже:",
        reply_markup=menu_keyboard
    )

# Обработчик кнопки "Расписание на день"
@dp.message(F.text == "📅 Расписание на день")
async def schedule_day(message: types.Message):
    day = get_daily_schedule()
    print(day)
    await message.answer(
        text=day,
        parse_mode="HTML"
    )
# Обработчик кнопки "Расписание на неделю"
@dp.message(F.text == "📆 Расписание на неделю")
async def schedule_week(message: types.Message):
    week = get_week_schedule()
    print(week)
    await message.answer(
        text=week,
        parse_mode="HTML"
    )

# Обработчик любых других сообщений
@dp.message()
async def echo(message: types.Message):
    await message.answer("Пожалуйста, используйте кнопки меню для навигации")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())