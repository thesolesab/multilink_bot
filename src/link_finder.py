import os
from .constants import SERVICES
from abc import ABC, abstractmethod
from .logger import log_async_method

class Finder(ABC):
    """Абстрактный базовый класс для парсеров"""
    
    def __init__(self, service_info):
        self.service = service_info
    
    @abstractmethod
    async def find(self, url):
        """Ищет ссылку и возвращает данные о треке"""
        pass

class SpotifyFinder(Finder):
    @log_async_method
    async def find(self, url):
        return {
            'service': 'Spotify',
            'url': url,
        }
    
class YandexFinder(Finder):
    @log_async_method
    async def find(self, track_name):
        try:
            from yandex_music import Client
            client = Client(os.getenv("YANDEX_MUSIC_TOKEN")).init()

            search_result = client.search(track_name, type='track', nocorrect=True)
            
            if search_result.tracks.results:
                track = search_result.tracks.results[0]
                url = f"https://music.yandex.ru/album/{track.album.id}/track/{track.id}"
                
                return {
                    'service': self.service['name'],
                    'url': url,
                }
            
            return {
                'service': self.service['name'],
                'url': url,
            }
        except Exception as e:
            print(f"Error Finding Yandex: {e}")
            return {
                'url': None,
                'error': str(e),
                'service': self.service['name'],
            }
        
class MTSFinder(Finder):
    @log_async_method
    async def find(self, url):
        try:
            
            return {
                'service': self.service['name'],
                'url': url,
            }
        except Exception as e:
            print(f"Error Finding MTS: {e}")
            return {
                'url': None,
                'error': str(e),
                'service': self.service['name'],
            }
            


class LinkFinder:
    def __init__(self):
        self.services = SERVICES
        self.finders = {
            'Spotify': SpotifyFinder(self.services['Spotify']),
            'YandexMusic': YandexFinder(self.services['YandexMusic']),
            'MTS': MTSFinder(self.services['MTS']),
        }
        
    @log_async_method
    async def find_link(self, trrack_info):
        try:
            for name, finder in self.finders.items():
                if trrack_info.original_service == name:
                    result = await finder.find(trrack_info.url)
                    return result
            return {'error': 'Service not supported'}
                
        except Exception as e:
            print(f'Error parsing link: {e}')
            return {'error': 'Failed to parse link'}