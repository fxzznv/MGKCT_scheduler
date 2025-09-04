import os
import re
import redis
from mgct_schedule.utils.daily_schedule import get_day_schedule
from dotenv import load_dotenv

load_dotenv()
host = os.getenv('REDIS_HOST', 'localhost')
port = int(os.getenv('REDIS_PORT', 6379))

r = redis.Redis(host=host, port=port, db=0, decode_responses=True)

def push_weekly_schedule(schedule_text: str) -> bool:

    try:

        # проверяем соединение
        r.ping()
    except Exception as e:
        print("Не удалось подключиться к Redis:", e)
        return False

    try:
        pipe = r.pipeline()
        # записываем в hash weekSchedule поле schedule
        pipe.hset("weekSchedule", mapping={"schedule_week": schedule_text})
        pipe.execute()
        print("Сохранено в Redis: ключ 'weekSchedule', поле 'schedule'")
        return True
    except Exception as e:
        print("Ошибка при записи в Redis:", e)
        return False

def extract_n_push_daily_schedule(target_date: str) -> bool:
    try:
        r.ping()  # Check connection
    except Exception as e:
        print("Не удалось подключиться к Redis:", e)
        return False

    try:
        # Retrieve the weekly schedule from Redis
        schedule_text = r.hget("weekSchedule", "schedule_week")
        if not schedule_text:
            print("No schedule found in Redis under key 'weekSchedule', field 'schedule_week'")
            return False

        # Extract the daily schedule for the target date
        daily_schedule = get_day_schedule(schedule_text, target_date)
        if "No schedule found" in daily_schedule:
            print(daily_schedule)
            return False

        # Save the daily schedule to Redis
        pipe = r.pipeline()
        pipe.hset("schedule_daily", "schedule_day", daily_schedule)
        pipe.execute()
        print(f"Сохранено в Redis: ключ 'schedule_daily', поле 'schedule_day'")
        return True

    except Exception as e:
        print("Ошибка при обработке или записи в Redis:", e)
        return False

def save_chat_id(chat_id: int):
    key = "chat_ids"
    # Проверим, нет ли уже такого id (чтобы не дублировать)
    if not r.sismember("chat_ids_set", str(chat_id)):
        r.rpush(key, str(chat_id))
        r.sadd("chat_ids_set", str(chat_id))  # Вспомогательное множество для проверки уникальности

def get_all_chat_ids() -> list[int]:
    key = "chat_ids"
    try:
        ids = r.lrange(key, 0, -1)  # Достаём все элементы списка (строки)
        return [int(chat_id) for chat_id in ids]  # Преобразуем строки в целые числа
    except ValueError as e:
        print(f"Ошибка преобразования chat_id в int: {e}")
        return []
    except Exception as e:
        print(f"Ошибка при получении chat_ids из Redis: {e}")
        return []

def debug_extract_day_schedule():
    """Функция для отладки поиска даты"""
    host = os.getenv('REDIS_HOST', 'localhost')
    port = int(os.getenv('REDIS_PORT', 6379))

    import redis
    r = redis.Redis(host=host, port=port, db=0, decode_responses=True)
    schedule_text = r.hget("weekSchedule", "schedule_week")

    if schedule_text:
        print("Поиск даты '04.09.2025' в тексте:")
        lines = schedule_text.split('\n')
        for i, line in enumerate(lines):
            if '04.09.2025' in line:
                print(f"Строка {i}: {line.strip()}")

        # Проверим конкретно с регулярным выражением
        print("\nПроверка регулярного выражения:")
        pattern = r' - 04\.09\.2025</b>'
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                print(f"Найдено в строке {i}: {line.strip()}")
                break
        else:
            print("Не найдено регулярным выражением")
if __name__ == "__main__":
    debug_extract_day_schedule()

    # Затем попробуйте извлечь
    target_date = "04.09.2025"
    success = extract_n_push_daily_schedule(target_date)
    if success:
        print(f"Successfully processed and saved schedule for {target_date}")