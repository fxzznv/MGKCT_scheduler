import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram import F
from dotenv import load_dotenv

from mgct_schedule.utils.rediss import save_chat_id
from telegram_bot.schedule_extracting import extract_week_schedule, extract_daily_schedule

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
    chat_id = int(message.chat.id)
    save_chat_id(chat_id)
    await message.answer(
        "динаху",
        reply_markup=menu_keyboard
    )

# Обработчик кнопки "Расписание на день"
@dp.message(F.text == "📅 Расписание на день")
async def schedule_day(message: types.Message):
    day = extract_daily_schedule()
    if day == '':
        await message.answer(text="Вернуло пустое значение почему-то. Пинганите @oeeeag")
    else:
        print(day)
        await message.answer(
            text=day,
            parse_mode="HTML"
        )
# Обработчик кнопки "Расписание на неделю"
@dp.message(F.text == "📆 Расписание на неделю")
async def schedule_week(message: types.Message):
    week = extract_week_schedule()
    if week == '':
        await message.answer(text="Вернуло пустое значение почему-то. Пинганите @oeeeag")
    else:
        print(week)
        await message.answer(
            text=week,
            parse_mode="HTML"
        )

# Обработчик любых других сообщений
@dp.message()
async def echo(message: types.Message):
    await message.answer("беее дяжвявсжфубйцдудж 654у654фыаджвфвбю, бутерброд с дерева сорви да поешь")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())