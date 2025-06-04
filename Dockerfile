# Проверенная облегченная версия ОС
FROM python:3.12-slim-bullseye
# Отключаем создание кешированных байт-код файлов Python, это ускоряет работу и уменьшает размер образа
ENV PYTHONDONTWRITEBYTECODE=1
# Отключаем буферизацию вывода Python, логи сразу выводятся в консоль
ENV PYTHONUNBUFFERED=1
# Это нужно, чтобы докер правильно подтягивал файлы и не выдавал ошибку импорта
ENV PYTHONPATH=/app
# Устанавливаем зависимости для asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY wallet /app/wallet
CMD ["uvicorn", "wallet.main:app", "--host", "0.0.0.0", "--port", "8000"]

