const askBtn = document.getElementById('askBtn');
const questionInput = document.getElementById('question');
const answerOutput = document.getElementById('answer');

askBtn?.addEventListener('click', async () => {
  const question = questionInput.value.trim();
  if (!question) {
    answerOutput.textContent = 'Введите вопрос перед отправкой.';
    return;
  }

  askBtn.disabled = true;
  askBtn.textContent = 'Отправка...';
  answerOutput.textContent = 'Думаю над ответом...';

  try {
    const response = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });

    const data = await response.json();

    if (!response.ok) {
      answerOutput.textContent = `Ошибка: ${data.error || 'Неизвестная ошибка'}`;
      return;
    }

    answerOutput.textContent = data.answer;
  } catch (error) {
    answerOutput.textContent = `Ошибка сети: ${error.message}`;
  } finally {
    askBtn.disabled = false;
    askBtn.textContent = 'Спросить AI';
  }
});
