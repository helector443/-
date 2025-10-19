import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import aiohttp
import json

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class QuizBot:
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_TOKEN')
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.model = "deepseek/deepseek-chat-v3.1:free"
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
    async def generate_question(self, topic: str) -> str:
        """Генерирует вопрос по теме через DeepSeek"""
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""Сгенерируй интересный вопрос по теме: {topic}
        Вопрос должен быть:
        - Понятным и четким
        - Проверять понимание темы
        - Не слишком простым, но и не слишком сложным
        - Один конкретный вопрос, а не несколько
        
        Верни только сам вопрос, без дополнительных объяснений."""
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 150
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=headers, json=data) as response:
                    result = await response.json()
                    return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f"Ошибка при генерации вопроса: {str(e)}"

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Привет! Я бот для генерации вопросов. "
            "Просто напиши тему, и я создам по ней вопрос!\n\n"
            "Например: 'история Древнего Рима' или 'программирование на Python'"
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        topic = update.message.text
        await update.message.reply_text("🤔 Генерирую вопрос...")
        
        question = await self.generate_question(topic)
        await update.message.reply_text(f"❓ Вопрос по теме '{topic}':\n\n{question}")

def main():
    bot = QuizBot()
    
    # Создаем приложение
    application = Application.builder().token(bot.telegram_token).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
