import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder
from src.message_handler import BotHandlers

class TelegramBot:
    """Класс для управления Telegram-ботом"""
    
    def __init__(self):
        # Загружаем переменные окружения
        load_dotenv()
        self.token = os.getenv('TELEGRAM_TOKEN')
        
        if not self.token:
            raise ValueError("TELEGRAM_TOKEN не найден в .env файле")
        
        # Создаём приложение
        self.application = ApplicationBuilder().token(self.token).build()
        
        # Настраиваем хендлеры
        self.handlers = BotHandlers()
        self.handlers.setup_handlers(self.application)
    
    def run(self):
        """Запускает бота в режиме webhook или polling"""
        print("Бот запущен!")
        
        # Добавляем обработчик ошибок
        async def error_handler(update, context):
            print(f"Update {update} caused error {context.error}")
        
        self.application.add_error_handler(error_handler)
        
        # Проверяем, использовать ли webhook
        use_webhook = os.getenv('USE_WEBHOOK', 'false').lower() == 'true'
        webhook_url = os.getenv('WEBHOOK_URL')
        
        if use_webhook and webhook_url:
            print(f"Запуск в режиме webhook: {webhook_url}")
            self.application.run_webhook(
                listen="0.0.0.0",
                port=int(os.getenv('WEBHOOK_PORT', 8443)),
                url_path=os.getenv('WEBHOOK_PATH', 'webhook'),
                webhook_url=webhook_url,
                cert=None,  # Для HTTPS, если нужно
                key=None
            )
        else:
            print("Запуск в режиме polling")
            self.application.run_polling()

def main():
    try:
        bot = TelegramBot()
        bot.run()
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем.")
    except Exception as e:
        print(f"Ошибка запуска бота: {e}")

if __name__ == '__main__':
    main()