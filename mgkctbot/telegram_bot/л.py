import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from mgct_schedule.utils.rediss import get_all_chat_ids

# Токен вашего бота
BOT_TOKEN = "8192247154:AAE2mFLGN__f9kA3IQYyJayZZEzodje_1i8"

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Функция для отправки сообщений всем пользователям
async def send_message_to_users(chat_ids, message_text):
    for chat_id in chat_ids:
        try:
            await bot.send_message(chat_id=chat_id, text=message_text)
            print(f"Сообщение отправлено пользователю с chat_id {chat_id}")
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю с chat_id {chat_id}: {e}")
        await asyncio.sleep(0.05)  # Задержка для соблюдения лимитов Telegram


# Обработчик команды /start (для примера, если нужно собирать chat_id)
@dp.message(Command("start"))
async def start_command(message: types.Message):
    chat_id = message.chat.id
    username = message.from_user.username or "без username"
    await message.answer(f"Ваш chat_id ({chat_id}) сохранён! Вы получите сообщения от бота.")


# Основная функция для запуска
async def main():
    # Запускаем отправку сообщений
    chat_ids = get_all_chat_ids()
    message = "Привет! Это сообщение от бота."
    await send_message_to_users(chat_ids, message)

    # Запускаем polling для обработки команд
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())