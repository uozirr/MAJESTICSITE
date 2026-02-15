# Majestic RP Legal Portal

Docs-style сайт для законки Majestic RP + AI-ассистент Gemini + Telegram-бот на aiogram.

## 1) Установка

```bash
npm install
cp .env.example .env
```

Заполните в `.env`:
- `GEMINI_API_KEY`
- `TELEGRAM_BOT_TOKEN` (для бота)

## 2) Запуск сайта

```bash
npm start
```

Откройте `http://localhost:3000`.

## 3) Запуск Telegram-бота

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r bot/requirements.txt
python bot/bot.py
```

## 4) Что уже сделано

- Структура docs-портала (sidebar + разделы: конституция, УК, АК).
- Форма AI-ассистента на сайте (запросы через серверный API `/api/ask`).
- Telegram-бот на aiogram, отвечающий через Gemini.

> Рекомендация: не храните ключи API в коде; используйте `.env`.
