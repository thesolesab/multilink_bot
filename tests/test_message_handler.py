import pytest
from unittest.mock import AsyncMock, patch
from telegram import Update, Message, Chat, User
from telegram.ext import ContextTypes
from src.message_handler import BotHandlers

class TestBotHandlers:
    def test_init(self):
        handlers = BotHandlers()
        assert handlers.welcome_message.startswith('Hello!')
        assert handlers.invalid_message.startswith('Please send')
        assert handlers.error_message == 'Error parsing the link.'
    
    @pytest.mark.asyncio
    async def test_start_command(self):
        handlers = BotHandlers()
        
        # Мокаем update
        mock_update = AsyncMock(spec=Update)
        mock_message = AsyncMock(spec=Message)
        mock_update.message = mock_message
        
        context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
        
        await handlers.start_command(mock_update, context)
        
        mock_message.reply_text.assert_called_once_with(handlers.welcome_message)
    
    @pytest.mark.asyncio
    async def test_handle_message_with_url(self):
        handlers = BotHandlers()
        
        # Мокаем update
        mock_update = AsyncMock(spec=Update)
        mock_message = AsyncMock(spec=Message)
        mock_chat = AsyncMock(spec=Chat)
        mock_chat.id = 123
        mock_message.chat = mock_chat
        mock_message.text = 'Check this: https://open.spotify.com/track/123'
        mock_update.message = mock_message
        
        context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
        
        # Мокаем парсинг
        mock_data = {
            'title': 'Test Song',
            'artists': 'Test Artist',
            'url': 'https://open.spotify.com/track/123'
        }
        
        with patch('src.message_handler.parse_link') as mock_parse:
            mock_parse.return_value = mock_data  # Теперь не async, так как синхронная версия
            # Мокаем reply_text для parsing_msg
            parsing_msg = AsyncMock(spec=Message)
            parsing_msg.message_id = 456
            mock_message.reply_text.side_effect = [parsing_msg, None]
            
            await handlers.handle_message(mock_update, context)
            
            # Проверяем вызовы
            assert mock_message.reply_text.call_count == 2
            parsing_msg.delete.assert_called_once()
            mock_parse.assert_called_once_with('https://open.spotify.com/track/123')
    
    @pytest.mark.asyncio
    async def test_handle_message_no_url(self):
        handlers = BotHandlers()
        
        mock_update = AsyncMock(spec=Update)
        mock_message = AsyncMock(spec=Message)
        mock_message.text = 'Hello world'
        mock_update.message = mock_message
        
        context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
        
        await handlers.handle_message(mock_update, context)
        
        mock_message.reply_text.assert_called_once_with(handlers.invalid_message)
    
    @pytest.mark.asyncio
    async def test_handle_message_parse_error(self):
        handlers = BotHandlers()
        
        mock_update = AsyncMock(spec=Update)
        mock_message = AsyncMock(spec=Message)
        mock_message.text = 'https://open.spotify.com/track/123'
        mock_update.message = mock_message
        
        context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
        
        with patch('src.message_handler.parse_link', return_value={'error': 'Failed'}):
            parsing_msg = AsyncMock(spec=Message)
            mock_message.reply_text.side_effect = [parsing_msg, None]
            
            await handlers.handle_message(mock_update, context)
            
            # Должен ответить ошибкой
            calls = mock_message.reply_text.call_args_list
            assert len(calls) == 2
            assert calls[1][0][0] == handlers.error_message