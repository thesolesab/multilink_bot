# Multilink Bot (Python Version)

A Telegram bot that parses music links from Spotify, Yandex Music, and MTS Music, providing track information.

## Features

- Parse links from Spotify, Yandex Music, and MTS Music
- Extract track title and artist information
- Send formatted responses in Markdown

## Setup

1. Clone the repository
2. Navigate to python_version folder
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your Telegram bot token
5. Run the bot: `python main.py`

## Project Structure

- `src/config/` - Configuration constants
- `src/services/` - Business logic services
- `src/utils/` - Utility functions
- `src/handlers/` - Message handlers for the bot