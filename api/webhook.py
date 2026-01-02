import json
import os
import asyncio
from http.server import BaseHTTPRequestHandler
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder
from src.message_handler import BotHandlers

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN не найден")

# Создаем приложение (глобально для переиспользования между вызовами)
application = None

def get_application():
    """Получает или создает приложение Telegram бота"""
    global application
    if application is None:
        application = ApplicationBuilder().token(TOKEN).build()
        handlers = BotHandlers()
        handlers.setup_handlers(application)
    return application

async def process_update_async(update_data):
    """Асинхронная обработка update"""
    app = get_application()
    update = Update.de_json(update_data, app.bot)
    await app.process_update(update)

class handler(BaseHTTPRequestHandler):
    """Обработчик для Vercel serverless function"""
    
    def do_POST(self):
        """Обрабатывает POST запросы от Telegram"""
        try:
            # Читаем тело запроса
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            update_data = json.loads(body.decode('utf-8'))
            
            if not update_data:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Empty body'}).encode())
                return
            
            # Обрабатываем update асинхронно
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(process_update_async(update_data))
            finally:
                loop.close()
            
            # Отправляем успешный ответ
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'message': 'OK'}).encode())
            
        except Exception as e:
            print(f"Error processing update: {e}")
            import traceback
            traceback.print_exc()
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_GET(self):
        """Обрабатывает GET запросы (для проверки работоспособности)"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'ok', 'service': 'telegram-webhook'}).encode())
    
    def log_message(self, format, *args):
        """Отключаем логирование запросов"""
        pass