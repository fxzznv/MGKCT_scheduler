import time
from datetime import datetime, timedelta
from pytz import timezone

from mgct_schedule.utils.rediss import push_weekly_schedule, extract_n_push_daily_schedule
from mgct_schedule.utils.weekly_schedule import get_schedule


def run_scheduler():
    msk = timezone('Europe/Moscow')
    last_weekly_update = datetime.min.replace(tzinfo=msk)  # Инициализация для первого запуска
    last_next_day_update = None  # Для отслеживания обновления на следующий день

    while True:
        now = datetime.now(msk)
        current_date = now.date()

        # 1. Обновление еженедельного расписания каждые 6 часов
        if (now - last_weekly_update) >= timedelta(hours=6):
            print(f"[{now}] Обновление еженедельного расписания и текущего дня")
            actual_schedule = get_schedule()
            push_weekly_schedule(actual_schedule)  # Сохраняем еженедельное в Redis

            # 2. Сразу после: обновляем ежедневное для сегодняшнего дня
            today_str = now.strftime('%d.%m.%Y')
            extract_n_push_daily_schedule(today_str)

            last_weekly_update = now

        # 3. Обновление на следующий день в 17:00
        if now.hour == 17 and now.minute < 5 and (last_next_day_update is None or last_next_day_update.date() != current_date):
            print(f"[{now}] Обновление расписания на следующий день")
            tomorrow = now + timedelta(days=1)
            tomorrow_str = tomorrow.strftime('%d.%m.%Y')
            extract_n_push_daily_schedule(tomorrow_str)
            last_next_day_update = now

        # 4. Сброс в 00:00: обновляем для текущего дня и сбрасываем флаг для next day
        if now.hour == 0 and now.minute < 5:
            print(f"[{now}] Сброс и обновление расписания на текущий день")
            today_str = now.strftime('%d.%m.%Y')
            extract_n_push_daily_schedule(today_str)
            last_next_day_update = None  # Сброс, чтобы в новых сутках обновление next day произошло только после 17:00

        time.sleep(60)  # Проверяем каждую минуту

if __name__ == "__main__":
    run_scheduler()