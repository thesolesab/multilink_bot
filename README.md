# Multilink Bot

Multilink Bot - это Telegram-бот для конвертации ссылок на музыкальные треки между различными сервисами: Spotify, Yandex Music и MTS Music.

## Функциональность

Бот позволяет:
- Отправить ссылку на трек из одного сервиса и получить ссылки на этот же трек в других сервисах
- Поддерживаемые сервисы: Spotify, Yandex Music, MTS Music

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/thesolesab/multilink_bot.git
   cd multilink_bot
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Создайте файл `.env` на основе `.env-example`:
   ```bash
   cp .env-example .env
   ```

4. Заполните `.env` файл реальными значениями API-ключей.

## Настройка

### Получение токена Telegram бота
1. Напишите [@BotFather](https://t.me/botfather) в Telegram
2. Создайте нового бота командой `/newbot`
3. Скопируйте токен и вставьте в `TELEGRAM_TOKEN` в файле `.env`

### Получение ключей Spotify API
1. Перейдите на [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Создайте новое приложение
3. Скопируйте Client ID и Client Secret
4. Вставьте их в `SPOTIFY_CLIENT_ID` и `SPOTIFY_CLIENT_SECRET` в файле `.env`

## Запуск

Запустите бота командой:
```bash
python multilink_bot.py
```

## Использование

1. Найдите бота в Telegram по его username
2. Отправьте ссылку на трек из поддерживаемого сервиса
3. Бот вернет ссылки на этот трек в других сервисах

## Поддерживаемые форматы ссылок

- Spotify: `https://open.spotify.com/track/...`
- Yandex Music: `https://music.yandex.ru/album/.../track/...`
- MTS Music: `https://mts-music-spo.onelink.me/sKFX/...`

## Требования

- Python 3.7+
- Установленные зависимости из `requirements.txt`

## Лицензия

[Укажите лицензию, если есть]