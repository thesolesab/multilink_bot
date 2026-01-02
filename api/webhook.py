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

# Создаем приложение (глобально для переиспользования между вызовами)
application = None

# Предварительно инициализируем приложение, если токен доступен
if TOKEN:
    try:
        print("Pre-initializing application...")
        application = ApplicationBuilder().token(TOKEN).build()
        handlers = BotHandlers()
        handlers.setup_handlers(application)
        
        # Добавляем обработчик ошибок
        async def error_handler(update, context):
            print(f"Update {update} caused error {context.error}")
            import traceback
            traceback.print_exc()
        
        application.add_error_handler(error_handler)
        print("Application pre-initialized successfully")
    except Exception as e:
        print(f"Error pre-initializing application: {e}")
        application = None

def get_application():
    """Получает или создает приложение Telegram бота"""
    global application
    if application is None:
        if not TOKEN:
            print("ERROR: TELEGRAM_TOKEN не найден в переменных окружения")
            raise ValueError("TELEGRAM_TOKEN не найден в переменных окружения")
        print(f"Creating application with token: {TOKEN[:10]}...")
        application = ApplicationBuilder().token(TOKEN).build()
        handlers = BotHandlers()
        handlers.setup_handlers(application)
        
        # Добавляем обработчик ошибок
        async def error_handler(update, context):
            print(f"Update {update} caused error {context.error}")
            import traceback
            traceback.print_exc()
        
        application.add_error_handler(error_handler)
        print("Application created successfully")
    return application

async def process_update_async(update_data):
    """Асинхронная обработка update"""
    try:
        print(f"Processing update: {json.dumps(update_data, indent=2)[:200]}")
        app = get_application()
        update = Update.de_json(update_data, app.bot)
        if update:
            print(f"Update parsed: {update.update_id}")
            await app.process_update(update)
            print("Update processed successfully")
        else:
            print("Warning: Update is None")
    except Exception as e:
        print(f"Error in process_update_async: {e}")
        import traceback
        traceback.print_exc()
        raise

class handler(BaseHTTPRequestHandler):
    """Обработчик для Vercel serverless function"""
    
    def do_POST(self):
        """Обрабатывает POST запросы от Telegram"""
        try:
            print("Received POST request")
            # Читаем тело запроса
            content_length = int(self.headers.get('Content-Length', 0))
            print(f"Content-Length: {content_length}")
            
            if content_length == 0:
                print("Error: Empty body")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Empty body'}).encode())
                return
                
            body = self.rfile.read(content_length)
            print(f"Body received: {len(body)} bytes")
            
            try:
                update_data = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode())
                return
            
            if not update_data:
                print("Error: Empty update_data")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode())
                return
            
            # Обрабатываем update асинхронно
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(process_update_async(update_data))
                finally:
                    loop.close()
            except Exception as e:
                print(f"Error in async processing: {e}")
                import traceback
                traceback.print_exc()
                # Все равно возвращаем 200, чтобы Telegram не повторял запрос
            
            # Отправляем успешный ответ
            print("Sending 200 OK response")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = json.dumps({'ok': True})
            self.wfile.write(response.encode())
            self.wfile.flush()
            
        except Exception as e:
            print(f"Error processing update: {e}")
            import traceback
            traceback.print_exc()
            
            # Возвращаем 200, чтобы Telegram не повторял запрос при ошибках обработки
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'error': str(e)}).encode())
    
    def do_GET(self):
        """Обрабатывает GET запросы (для проверки работоспособности)"""
        try:
            print("Received GET request")
            # Проверяем, что токен установлен
            if not TOKEN:
                status = {'status': 'error', 'message': 'TELEGRAM_TOKEN not configured'}
                status_code = 500
            else:
                status = {'status': 'ok', 'service': 'telegram-webhook', 'token_set': True}
                status_code = 200
            
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status).encode())
        except Exception as e:
            print(f"Error in GET handler: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def log_message(self, format, *args):
        """Отключаем стандартное логирование, используем print"""
        pass