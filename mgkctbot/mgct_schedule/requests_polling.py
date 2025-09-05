import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot
from pytz import timezone

from mgct_schedule.utils.rediss import push_weekly_schedule, extract_n_push_daily_schedule, get_all_chat_ids
from mgct_schedule.utils.weekly_schedule import get_schedule
from telegram_bot.schedule_extracting import extract_week_schedule

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Токен вашего бота
API_TOKEN = "8192247154:AAE2mFLGN__f9kA3IQYyJayZZEzodje_1i8"
bot = Bot(token=API_TOKEN)

async def send_message_to_users(chat_ids, message_text):
    """Отправка сообщений всем пользователям по списку chat_id."""
    logger.info(f"Отправка сообщения: '{message_text}' для chat_ids: {chat_ids}")
    for chat_id in chat_ids:
        try:
            await bot.send_message(chat_id=chat_id, text=message_text, parse_mode="HTML")
            logger.info(f"Сообщение отправлено пользователю с chat_id {chat_id}")
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения пользователю с chat_id {chat_id}: {e}")
        await asyncio.sleep(0.05)  # Задержка для соблюдения лимитов Telegram

async def run_scheduler():
    msk = timezone('Europe/Moscow')
    last_weekly_update = datetime.min.replace(tzinfo=msk)  # Инициализация для первого запуска
    last_next_day_update = None  # Для отслеживания обновления на следующий день

    while True:
        now = datetime.now(msk)
        current_date = now.date()

        # 1. Обновление еженедельного расписания каждые 2 минуты
        if (now - last_weekly_update) >= timedelta(hours=3):
            extracted_schedule = extract_week_schedule()
            logger.info(f"[{now}] Обновление еженедельного расписания и текущего дня")
            actual_schedule = get_schedule()
            logger.info(f"Сравнение расписаний: actual_schedule == extracted_schedule: {actual_schedule == extracted_schedule}")
            logger.info(f"actual_schedule: {actual_schedule}")
            logger.info(f"extracted_schedule: {extracted_schedule}")

            # Временно форсируем отправку для теста (замените на `actual_schedule != extracted_schedule` после проверки)
            if actual_schedule != extracted_schedule:
                logger.info("Расписание изменилось (или тестовая отправка), сохраняем в Redis")
                push_weekly_schedule(actual_schedule)
                logger.info("Пуш в Redis выполнен")

                chat_ids = get_all_chat_ids()
                logger.info(f"Получены chat_ids: {chat_ids}")
                if chat_ids:
                    await send_message_to_users(chat_ids, "📢 <b>Получено измененное расписание</b>\n\nПроверьте новое расписание с помощью команды /start или кнопок.")
                else:
                    logger.warning("Список chat_ids пуст, сообщения не отправлены")

            # Обновляем ежедневное расписание для текущего дня
            today_str = now.strftime('%d.%m.%Y')
            extract_n_push_daily_schedule(today_str)
            logger.info(f"Ежедневное расписание для {today_str} обновлено")
            last_weekly_update = now

        # 2. Обновление на следующий день в 17:00
        if now.hour == 17 and now.minute < 5 and (last_next_day_update is None or last_next_day_update.date() != current_date):
            logger.info(f"[{now}] Обновление расписания на следующий день")
            tomorrow = now + timedelta(days=1)
            tomorrow_str = tomorrow.strftime('%d.%m.%Y')
            extract_n_push_daily_schedule(tomorrow_str)
            logger.info(f"Расписание на следующий день ({tomorrow_str}) обновлено")
            last_next_day_update = now

        # 3. Сброс в 00:00: обновляем для текущего дня и сбрасываем флаг
        if now.hour == 0 and now.minute < 5:
            logger.info(f"[{now}] Сброс и обновление расписания на текущий день")
            today_str = now.strftime('%d.%m.%Y')
            extract_n_push_daily_schedule(today_str)
            logger.info(f"Ежедневное расписание для {today_str} обновлено")
            last_next_day_update = None  # Сброс для обновления на следующий день

        await asyncio.sleep(60)  # Проверяем каждую минуту

async def main():
    try:
        await run_scheduler()
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())