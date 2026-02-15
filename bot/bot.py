import asyncio
import os

import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

SYSTEM_PROMPT = (
    'Ты — юридический AI-ассистент по законке Majestic RP. '
    'Отвечай структурно: статья/пункт, суть нарушения, пример санкции, '
    'и уточнение, что финальное решение принимает уполномоченный сотрудник.'
)


async def ask_gemini(question: str) -> str:
    if not GEMINI_API_KEY:
        return 'Не настроен GEMINI_API_KEY в окружении.'

    url = (
        f'https://generativelanguage.googleapis.com/v1beta/models/'
        f'{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}'
    )

    payload = {
        'contents': [
            {
                'role': 'user',
                'parts': [
                    {
                        'text': f'{SYSTEM_PROMPT}\n\nВопрос пользователя: {question}'
                    }
                ],
            }
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, timeout=40) as response:
            data = await response.json()
            if response.status != 200:
                return f"Ошибка Gemini API: {data.get('error', {}).get('message', 'unknown error')}"

            return (
                data.get('candidates', [{}])[0]
                .get('content', {})
                .get('parts', [{}])[0]
                .get('text', 'Пустой ответ от Gemini.')
            )


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError('TELEGRAM_BOT_TOKEN is missing in environment.')

    dp = Dispatcher()
    bot = Bot(token=BOT_TOKEN)

    @dp.message(CommandStart())
    async def cmd_start(message: Message) -> None:
        await message.answer(
            'Привет! Я AI-ассистент по законке Majestic RP. '\
            'Отправь вопрос по статьям УК/АК/конституции.'
        )

    @dp.message(F.text)
    async def answer_question(message: Message) -> None:
        user_question = message.text.strip()
        if not user_question:
            await message.answer('Напиши вопрос текстом.')
            return

        await message.answer('Ищу ответ по законке...')
        answer = await ask_gemini(user_question)
        await message.answer(answer)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
