import pytest
from unittest.mock import patch, MagicMock
from main import TelegramBot

class TestTelegramBot:
    @patch('main.load_dotenv')
    @patch.dict('os.environ', {'TELEGRAM_TOKEN': 'test_token'})
    @patch('main.ApplicationBuilder')
    @patch('main.BotHandlers')
    def test_init_success(self, mock_handlers, mock_builder, mock_load):
        mock_app = MagicMock()
        mock_builder.return_value.token.return_value.build.return_value = mock_app
        
        bot = TelegramBot()
        
        assert bot.token == 'test_token'
        assert bot.application == mock_app
        mock_handlers.assert_called_once()
        mock_handlers.return_value.setup_handlers.assert_called_once_with(mock_app)
    
    @patch('main.load_dotenv')
    @patch.dict('os.environ', {}, clear=True)
    def test_init_no_token(self, mock_load):
        with pytest.raises(ValueError, match="TELEGRAM_TOKEN не найден"):
            TelegramBot()
    
    @patch('main.load_dotenv')
    @patch.dict('os.environ', {'TELEGRAM_TOKEN': 'test_token'})
    @patch('main.ApplicationBuilder')
    @patch('main.BotHandlers')
    def test_run(self, mock_handlers, mock_builder, mock_load):
        mock_app = MagicMock()
        mock_builder.return_value.token.return_value.build.return_value = mock_app
        
        bot = TelegramBot()
        
        bot.run()
        
        mock_app.run_polling.assert_called_once()