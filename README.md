# Majestic RP Legal Portal

Docs-style сайт для законки Majestic RP + AI-ассистент Gemini + Telegram-бот на aiogram.

## 1) Установка

```bash
cp .env.example .env
```

Заполните в `.env`:
- `GEMINI_API_KEY`
- `TELEGRAM_BOT_TOKEN` (для бота)

## 2) Общий запуск всего через один `.py` файл

```bash
python run_all.py
```

Полезные режимы:

```bash
python run_all.py --mode all   # сайт + бот
python run_all.py --mode web   # только сайт
python run_all.py --mode bot   # только бот
```

По умолчанию сайт откроется на `http://localhost:3000`.

## 3) Ручной запуск по отдельности (опционально)

```bash
python web_server.py
python bot/bot.py
```

## 4) Что уже сделано

- Структура docs-портала (sidebar + разделы: конституция, УК, АК).
- Форма AI-ассистента на сайте (запросы через серверный API `/api/ask`).
- Telegram-бот на aiogram, отвечающий через Gemini.

> Рекомендация: не храните ключи API в коде; используйте `.env`.
