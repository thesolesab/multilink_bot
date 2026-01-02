# Multilink Bot (Python Version)

A Telegram bot that parses music links from Spotify, Yandex Music, and MTS Music, providing track information.

## Features

- Parse links from Spotify, Yandex Music, and MTS Music
- Extract track title and artist information
- Send formatted responses in Markdown

## Setup

### Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your Telegram bot token
4. Run the bot: `python main.py`

### Deploy to Vercel

1. **Push your code to GitHub/GitLab/Bitbucket**
   - Убедитесь, что все файлы закоммичены и запушены в репозиторий

2. **Создайте проект на Vercel**
   - Перейдите на [vercel.com](https://vercel.com)
   - Войдите через ваш Git-провайдер
   - Нажмите "Add New Project" и выберите ваш репозиторий

3. **Настройте переменные окружения в Vercel**
   - В настройках проекта перейдите в "Environment Variables"
   - Добавьте следующие переменные:
     - `TELEGRAM_TOKEN` - токен вашего Telegram бота
     - `SPOTIFY_CLIENT_ID` - ID клиента Spotify (если используется)
     - `SPOTIFY_CLIENT_SECRET` - секрет клиента Spotify (если используется)
     - `YANDEX_MUSIC_TOKEN` - токен Yandex Music (если используется)
     - `MTS_VK_TOKEN` - токен VK API для MTS Music (если используется)

4. **Деплой**
   - Vercel автоматически определит настройки из `vercel.json`
   - Нажмите "Deploy" и дождитесь завершения

5. **Настройте Webhook в Telegram**
   - После деплоя получите URL вашего проекта (например: `https://your-project.vercel.app`)
   - Установите webhook через Telegram Bot API:
     ```
     https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://your-project.vercel.app/api/webhook
     ```
   - Проверьте статус webhook:
     ```
     https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
     ```

**Важно:** После каждого деплоя URL может измениться, если вы не используете кастомный домен. Обновите webhook URL в Telegram.

## Project Structure

- `src/config/` - Configuration constants
- `src/services/` - Business logic services
- `src/utils/` - Utility functions
- `src/handlers/` - Message handlers for the bot