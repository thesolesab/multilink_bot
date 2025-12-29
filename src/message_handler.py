from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from .link_parser import parse_link
from .markdown import escape_markdown
from .logger import log_async_method

class BotHandlers:
    """Класс для обработки сообщений Telegram-бота"""
    
    def __init__(self):
        self.welcome_message = (
            'Hello! Send me a music track link from Spotify, Yandex Music, or MTS Music, '
            'and I\'ll provide you with multi-links to the track on other services.'
        )
        self.invalid_message = (
            'Please send a valid music track link from Spotify, Yandex Music, or MTS Music.'
        )
        self.error_message = 'Error parsing the link.'
    
    @log_async_method
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        await update.message.reply_text(self.welcome_message)
    
    @log_async_method
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        text = update.message.text
        chat_id = update.message.chat_id
        
        # Проверяем, есть ли URL
        import re
        url_regex = re.compile(r'https?://[^\s]+')
        match = url_regex.search(text)
        
        if match:
            parsing_msg = await update.message.reply_text('Parsing your link...')
            
            data = await parse_link(match.group(0))
            print(f"Parsed data: {data}")  # Для отладки
            
            if 'error' in data:
                await update.message.reply_text(self.error_message)
                return
            
            response = f"*{escape_markdown(data['artists'])}* - {escape_markdown(data['title'])}\n"
            response += f"*URL:* {data['url']}\n"
            
            await parsing_msg.delete()
            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            await update.message.reply_text(self.invalid_message)
    
    def setup_handlers(self, application):
        """Регистрирует все хендлеры в приложении"""
        application.add_handler(CommandHandler('start', self.start_command))
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

# Для совместимости с main.py
def setup_handlers(application):
    handlers = BotHandlers()
    handlers.setup_handlers(application)