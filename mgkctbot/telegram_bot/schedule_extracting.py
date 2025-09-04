import os

import redis


def extract_week_schedule() -> str:
    """
    Получение расписания недели из Redis (из хэша)
    """
    host = os.getenv('REDIS_HOST', 'localhost')
    port = int(os.getenv('REDIS_PORT', 6379))
    r = redis.Redis(host=host, port=port, db=0, decode_responses=True)

    # Получаем значение из поля schedule_week хэша
    schedule_week = r.hget("weekSchedule", "schedule_week")
    print(repr(schedule_week))
    return schedule_week


def extract_daily_schedule() -> str:
    """
    Получение дневного расписания из Redis (из хэша)
    """
    host = os.getenv('REDIS_HOST', 'localhost')
    port = os.getenv('REDIS_PORT', 6379)

    r = redis.Redis(host=host, port=port, db=0, decode_responses=True)

    # Получаем значение из поля schedule_day хэша
    schedule_day = r.hget("schedule_daily", "schedule_day")

    return schedule_day

if __name__ == "__main__":
    print(extract_week_schedule())

    print(extract_daily_schedule())