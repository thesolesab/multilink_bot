import json
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder
from src.message_handler import BotHandlers

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN не найден")

# Создаем приложение
application = ApplicationBuilder().token(TOKEN).build()

# Настраиваем хендлеры
handlers = BotHandlers()
handlers.setup_handlers(application)

def handler(event, context):
    """Обработчик для Vercel serverless function"""
    try:
        # Получаем update из тела запроса
        update_data = json.loads(event.get('body', '{}'))
        update = Update.de_json(update_data, application.bot)
        
        # Обрабатываем update
        application.process_update(update)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'OK'})
        }
    except Exception as e:
        print(f"Error processing update: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }