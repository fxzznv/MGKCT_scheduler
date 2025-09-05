import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram import F
from dotenv import load_dotenv

from mgct_schedule.utils.rediss import save_chat_id
from telegram_bot.schedule_extracting import extract_week_schedule, extract_daily_schedule, \
    extract_previous_week_schedule

load_dotenv()
# Токен вашего бота
API_TOKEN = os.getenv("API_TOKEN", "8192247154:AAE2mFLGN__f9kA3IQYyJayZZEzodje_1i8")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    logger.info(f"Новый пользователь: chat_id={chat_id}, username={message.from_user.username or 'без username'}")
    await message.answer(
        "динаху",
        reply_markup=menu_keyboard
    )

# Обработчик кнопки "Расписание на день"
@dp.message(F.text == "📅 Расписание на день")
async def schedule_day(message: types.Message):
    day = extract_daily_schedule()
    if day == '':
        await message.answer(text="Error")
    else:
        await message.answer(
            text=day,
            parse_mode="HTML"
        )

# Обработчик кнопки "Расписание на неделю"
@dp.message(F.text == "📆 Расписание на неделю")
async def schedule_week(message: types.Message):
    week = extract_week_schedule()
    if week == '':
        await message.answer(text="Error")
    else:
        await message.answer(
            text=week,
            parse_mode="HTML"
        )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ пред. неделя", callback_data="prev_week")]
    ])

    await message.answer(
        text=week,
        parse_mode="HTML",
        reply_markup=kb
    )

# Обработчик любых других сообщений
@dp.message()
async def echo(message: types.Message):
    await message.answer("беее дяжвявсжфубйцдудж 654у654фыаджвфвбю, бутерброд с дерева сорви да поешь")

# Обработчик нажатия inline-кнопки "пред. неделя"
@dp.callback_query(F.data == "prev_week")
async def handle_prev_week(call: CallbackQuery):
    await call.answer()  # убирает "крутилку" в клиенте

    # удаляем сообщение, на котором нажали кнопку
    try:
        await call.message.delete()
    except Exception as e:
        logger.error(f"Не удалось удалить сообщение: {e}")

    # Попытка получить расписание предыдущей недели:
    # Если у тебя есть функция extract_week_schedule_previous(), заменяй соответственно.
    try:
        week_prev = extract_previous_week_schedule()  # <-- если есть, используем её
    except NameError:
        # fallback: использовать основную функцию (можно заменить логикой со смещением)
        week_prev = extract_week_schedule()

    if week_prev == '':
        await bot.send_message(chat_id=call.message.chat.id, text="Error")
        return

    # отправляем новое сообщение с кнопкой "след. неделя"
    kb_next = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="след. неделя ➡️", callback_data="next_week")]
    ])

    await bot.send_message(
        chat_id=call.message.chat.id,
        text=week_prev,
        parse_mode="HTML",
        reply_markup=kb_next
    )

# Обработчик нажатия inline-кнопки "след. неделя"
@dp.callback_query(F.data == "next_week")
async def handle_next_week(call: CallbackQuery):
    await call.answer()

    # удаляем сообщение, на котором нажали кнопку
    try:
        await call.message.delete()
    except Exception as e:
        logger.error(f"Не удалось удалить сообщение: {e}")

    # Попытка получить расписание следующей недели:
    # Если у тебя есть функция extract_week_schedule_next(), заменяй соответственно.
    try:
        week_next = extract_week_schedule()  # <-- если есть, используем её
    except NameError:
        week_next = extract_week_schedule()

    if week_next == '':
        await bot.send_message(chat_id=call.message.chat.id, text="Error")
        return

    # отправляем новое сообщение с кнопкой "пред. неделя"
    kb_prev = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ пред. неделя", callback_data="prev_week")]
    ])

    await bot.send_message(
        chat_id=call.message.chat.id,
        text=week_next,
        parse_mode="HTML",
        reply_markup=kb_prev
    )

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())