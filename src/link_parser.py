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
        og_description = soup.find('meta', property='og:description')
        
        title = og_title.get('content', 'Unknown Title') if og_title else 'Unknown Title'
        description = og_description.get('content', '') if og_description else ''
        
        artists = description.split(title)[0] if title in description else 'Unknown Artist'
        artists = artists.replace('by', '').replace('·', '').strip()
        
        return {
            'url': url,
            'original_service': self.service,
            'title': title.strip(),
            'artists': artists,
        }

class YandexParser(Parser):
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
                async with session.get(url, headers=headers) as response:
                    html = await response.text()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            og_title = soup.find('meta', property='og:title')
            og_description = soup.find('meta', property='og:description')
            
            title = og_title.get('content', 'Yandex Music Track') if og_title else 'Yandex Music Track'
            description = og_description.get('content', '') if og_description else ''
            
            # Для Yandex Music описание может содержать артиста
            artists = 'Unknown Artist'
            if ' — ' in title:
                parts = title.split(' — ')
                if len(parts) >= 2:
                    artists = parts[0].strip()
                    title = parts[1].strip()
            
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
                'title': 'Yandex Music Track',
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
            
            # Для MTS попробуем найти мета-теги
            og_title = soup.find('meta', property='og:title')
            og_description = soup.find('meta', property='og:description')
            
            title = og_title.get('content', 'Unknown Title') if og_title else 'Unknown Title'
            # Очистить название от лишней информации
            if ' - слушать песню онлайн' in title:
                title = title.split(' - слушать песню онлайн')[0].strip()
            description = og_description.get('content', '') if og_description else ''
            
            # Извлечь артиста из описания, если возможно
            artists = 'Unknown Artist'
            if 'исполнителя' in description:
                parts = description.split('исполнителя')
                if len(parts) > 1:
                    artist_part = parts[1].split('!')[0].strip()
                    artists = artist_part
            elif 'by' in description:
                parts = description.split('by')
                if len(parts) > 1:
                    artists = parts[1].split('·')[0].strip()
            
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