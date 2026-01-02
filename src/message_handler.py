from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, InlineQueryHandler
from .link_parser import parse_link
from .markdown import escape_markdown
from .logger import log_async_method
from .link_finder import find_link

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
            parsing_msg = await update.message.reply_text('🎶Parsing your link\\.\\.\\.', parse_mode='MarkdownV2')
            
            data = await parse_link(match.group(0))
            links = await find_link(data)
            print(f'Parsed data: {data}, links: {links}')
            
            if 'error' in data:
                await parsing_msg.edit_text(self.error_message)
                return
            
            response = f"*{escape_markdown(data['artists'])}* \\- {escape_markdown(data['title'])}\n"
            response += f'[{escape_markdown(data["original_service"]["name"])}]({data["url"]})\n'
            for link_info in links:
                if link_info.get('url'):
                    response += f'[{escape_markdown(link_info["service"])}]({link_info["url"]})\n'  

            await parsing_msg.edit_text(response, parse_mode='MarkdownV2')
        else:
            await update.message.reply_text(self.invalid_message)
            
    @log_async_method        
    async def inline_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик inline-запросов"""
        query = update.inline_query.query
        
        if not query:
            return
        
        import re
        url_regex = re.compile(r'https?://[^\s]+')
        match = url_regex.search(query)
        
        if match:
            data = await parse_link(query)
            links = await find_link(data)
            print(f'Parsed data: {data}, links: {links}')
            
            response = f"*{escape_markdown(data['artists'])}* \\- {escape_markdown(data['title'])}\n"
            response += f'[{escape_markdown(data["original_service"]["name"])}]({data["url"]})\n'
            for link_info in links:
                if link_info.get('url'):
                    response += f'[{escape_markdown(link_info["service"])}]({link_info["url"]})\n'  
            
            results = [(
                InlineQueryResultArticle(
                    id='1',
                    title=f'{escape_markdown(data["title"])}',
                    input_message_content=InputTextMessageContent(
                        response,
                        parse_mode='MarkdownV2'
                    ),
                    description='Get multi-links for the track',
                )
            )]
        
        await update.inline_query.answer(results)
    
    def setup_handlers(self, application):
        """Регистрирует все хендлеры в приложении"""
        application.add_handler(CommandHandler('start', self.start_command))
        application.add_handler(InlineQueryHandler(self.inline_query))
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

# Для совместимости с main.py
def setup_handlers(application):
    handlers = BotHandlers()
    handlers.setup_handlers(application)