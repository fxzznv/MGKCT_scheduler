import logging
import os
import threading

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram import F
from dotenv import load_dotenv
from flask import Flask, jsonify

from mgct_schedule.utils.rediss import save_chat_id, get_all_chat_ids
from telegram_bot.schedule_extracting import extract_week_schedule, extract_daily_schedule

load_dotenv()
app = Flask(__name__)
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
        # print(day)
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
        # print(week)
        await message.answer(
            text=week,
            parse_mode="HTML"
        )
# Обработчик любых других сообщений
@dp.message()
async def echo(message: types.Message):
    await message.answer("беее дяжвявсжфубйцдудж 654у654фыаджвфвбю, бутерброд с дерева сорви да поешь")


@app.route('/make_notification', methods=['POST'])
def make_notification():
    # Получаем текущий event loop (или создаем, если нет)
    loop = asyncio.get_event_loop()

    chat_ids = get_all_chat_ids()
    # Отправляем "Hello World" в каждый сохраненный chat_id
    for chat_id in chat_ids:
        loop.run_until_complete(send_notification(chat_id, "📢 Получено измененное расписание"))

    print("Notification sent")
    return jsonify({"success": True, "notification": "NoError"}), 200

async def send_notification(chat_id: int, text: str):
        await bot.send_message(chat_id=chat_id, text=text)


def run_flask():
    app.run(debug=True, use_reloader=False, port=5000)


async def main():
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Запускаем polling бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())