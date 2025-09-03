FROM python:3.11-slim

WORKDIR /app

# Копируем ВЕСЬ проект
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Создаем пользователя
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app
USER botuser

# Добавляем корневую директорию в PYTHONPATH
ENV PYTHONPATH=/app

# Запускаем из нужной директории
WORKDIR /app/telegram_bot
CMD ["python", "bot.py"]