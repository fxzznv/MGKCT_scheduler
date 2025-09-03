FROM python:3.11-slim

WORKDIR /app

# Копируем ВЕСЬ проект
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Создаем пользователя
RUN useradd -m -u 1000 scheduler && \
    chown -R scheduler:scheduler /app
USER scheduler

# Добавляем корневую директорию в PYTHONPATH
ENV PYTHONPATH=/app

# Запускаем из нужной директории
WORKDIR /app/mgct_schedule
CMD ["python", "requests_polling.py"]