FROM python:3.11-slim

# Рабочая папка
WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Запуск через gunicorn
CMD ["gunicorn", "mybuild.wsgi:application", "--bind", "0.0.0.0:8000"]
