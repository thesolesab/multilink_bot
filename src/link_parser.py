import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from .constants import SERVICES
from .logger import log_method, log_async_method

class Parser(ABC):
    """Абстрактный базовый класс для парсеров"""
    
    def __init__(self, service_info):
        self.service = service_info
    
    @abstractmethod
    async def parse(self, url):
        """Парсит ссылку и возвращает данные о треке"""
        pass

class SpotifyParser(Parser):
    @log_async_method
    async def parse(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'User-Agent': 'TelegramBot (like Twitterbot) Android'}) as response:
                html = await response.text()
        
        soup = BeautifulSoup(html, 'html.parser')
        
        og_title = soup.find('meta', property='og:title')
        artists_meta = soup.find('meta', {'name': 'music:musician_description'}) or soup.find('meta', {'property': 'music:musician_description'})
        
        title = og_title.get('content', 'Unknown Title') if og_title else 'Unknown Title'
        artists = artists_meta.get('content', 'Unknown Artist') if artists_meta else 'Unknown Artist'
        
        return {
            'url': url,
            'original_service': self.service,
            'title': title,
            'artists': artists,
        }

class YandexParser(Parser):
    @log_async_method
    async def parse(self, url):
        try:
            # Извлечь track_id из URL
            import re
            match = re.search(r'/track/(\d+)', url)
            if not match:
                return {
                    'url': url,
                    'original_service': self.service,
                    'title': 'Yandex Music Track',
                    'artists': 'Unknown Artist',
                }
                
            track_id = match.group(1)
            print(f"Extracted track_id: {track_id}")
            
            from yandex_music import Client
            client = Client(os.getenv("YANDEX_MUSIC_TOKEN")).init()
            track = client.tracks([track_id])[0]
            title = track.title
            artists = ', '.join(name.name for name in track.artists)
            
            return {
                'url': url,
                'original_service': self.service,
                'title': title,
                'artists': artists,
            }
        except Exception as e:
            print(f"Error parsing Yandex: {e}")
            return {
                'url': url,
                'original_service': self.service,
                'title': 'Unknown Title',
                'artists': 'Unknown Artist',
            }
                
class MTSParser(Parser):
    @log_async_method
    async def parse(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, allow_redirects=True) as response:
                    final_url = str(response.url)
                    
                    # Извлечь deep_link_value из URL
                    from urllib.parse import parse_qs, urlparse
                    parsed = urlparse(final_url)
                    query = parse_qs(parsed.query)
                    deep_link = query.get('deep_link_value', [None])[0]
                    if deep_link:
                        deep_link = deep_link.replace('%3A', ':').replace('%2F', '/')
                        async with session.get(deep_link, headers=headers) as track_response:
                            html = await track_response.text()
                    else:
                        html = await response.text()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Ищем заголовок трека в h1 элементе
            track_title_elem = soup.find('h1', {'data-testid': 'playlist-title', 'itemprop': 'name'})
            if track_title_elem:
                full_title = track_title_elem.get_text(strip=True)
                # Разделяем на артистов и название по " - "
                if ' - ' in full_title:
                    artists, title = full_title.split(' - ', 1)
                    artists = artists.strip()
                    title = title.strip()
                else:
                    # Если нет разделителя, считаем всё названием
                    artists = 'Unknown Artist'
                    title = full_title.strip()
            else:
                # Fallback на мета-теги, если h1 не найден
                og_title = soup.find('meta', property='og:title')
                title = og_title.get('content', 'Unknown Title') if og_title else 'Unknown Title'
                # Очистить название от лишней информации
                if ' - слушать песню онлайн' in title:
                    title = title.split(' - слушать песню онлайн')[0].strip()
                artists = 'Unknown Artist'
            
            return {
                'url': url,
                'original_service': self.service,
                'title': title,
                'artists': artists,
            }
        except Exception as e:
            print(f"Error parsing MTS: {e}")
            return {
                'url': url,
                'original_service': self.service,
                'title': 'Unknown Title',
                'artists': 'Unknown Artist',
            }

class LinkParser:
    def __init__(self):
        self.services = SERVICES
        self.parsers = {
            'Spotify': SpotifyParser(self.services['Spotify']),
            'YandexMusic': YandexParser(self.services['YandexMusic']),
            'MTS': MTSParser(self.services['MTS']),
        }
    
    @log_async_method
    async def parse_link(self, url):
        try:
            for name, parser in self.parsers.items():
                if parser.service['regex'].match(url):
                    return await parser.parse(url)
            return None
        except Exception as e:
            print(f'Error parsing link: {e}')
            return {'error': 'Failed to parse link'}

# Для совместимости (асинхронная версия)
async def parse_link(url):
    parser = LinkParser()
    return await parser.parse_link(url)