const path = require('path');
const express = require('express');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const GEMINI_MODEL = process.env.GEMINI_MODEL || 'gemini-1.5-flash';

app.use(express.json({ limit: '1mb' }));
app.use(express.static(path.join(__dirname, 'public')));

app.post('/api/ask', async (req, res) => {
  if (!GEMINI_API_KEY) {
    return res.status(500).json({
      error: 'GEMINI_API_KEY is not configured on server.'
    });
  }

  const question = req.body?.question?.toString()?.trim();
  if (!question) {
    return res.status(400).json({ error: 'Question is required.' });
  }

  const systemPrompt = `Ты — юридический AI-ассистент проекта Majestic RP. 
Объясняй нормы простым языком, но обязательно указывай:
1) конкретную статью/пункт (если известен),
2) суть нарушения,
3) пример санкции,
4) пометку, что финальное решение принимает уполномоченный сотрудник.
Если данных недостаточно — прямо скажи, что нужна уточняющая информация.`;

  try {
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${GEMINI_API_KEY}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [
          {
            role: 'user',
            parts: [{ text: `${systemPrompt}\n\nВопрос: ${question}` }]
          }
        ]
      })
    });

    const data = await response.json();

    if (!response.ok) {
      return res.status(response.status).json({
        error: data?.error?.message || 'Gemini API error.'
      });
    }

    const answer = data?.candidates?.[0]?.content?.parts?.[0]?.text;

    if (!answer) {
      return res.status(502).json({ error: 'Empty response from Gemini.' });
    }

    return res.json({ answer });
  } catch (error) {
    return res.status(500).json({
      error: 'Failed to reach Gemini API.',
      details: error.message
    });
  }
});

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Majestic legal portal running on http://localhost:${PORT}`);
});
