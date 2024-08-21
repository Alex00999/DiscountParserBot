# Используем официальный образ Python в качестве базового
FROM python:3.11-slim

# Устанавливаем переменную окружения для указания Docker, что не требуется буферизация вывода
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Устанавливаем зависимости для сборки и общие утилиты
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Создаем и используем непользовательскую директорию для приложения
WORKDIR /bot

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения в рабочую директорию
COPY . .
