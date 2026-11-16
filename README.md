# mizhnami — простір опори

Сайт психологічної підтримки та тілесної усвідомленості.

## Стек технологій
- **Backend:** Django 6.1 (без збереження в БД, повністю serverless-ready)
- **Frontend:** Vanilla HTML, CSS (Tailwind CSS, Glassmorphism, 3D soft shadows)
- **Сповіщення:** Telegram Bot API (пряма синхронна доставка заявок)
- **Деплой:** Vercel

## Локальний запуск

```bash
# 1. Встановити залежності
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Налаштувати змінні середовища
cp .env.example .env
# Заповніть TELEGRAM_BOT_TOKEN і TELEGRAM_CHAT_ID у .env

# 3. Перевірити роботу Telegram
python manage.py test_telegram

# 4. Запустити тести
DJANGO_DEBUG=1 python manage.py test

# 5. Запустити dev-сервер
DJANGO_DEBUG=1 python manage.py runserver
```

## Контент сайту
Тексти тем розмов, описів та станів цілісності зберігаються у файлі `main/content.py`. Щоб змінити будь-який текст — відредагуйте цей файл і закомітьте в git.
