import os
from .constants import SERVICES
from abc import ABC, abstractmethod
from .logger import log_async_method

class Finder(ABC):
    """Абстрактный базовый класс для парсеров"""
    
    def __init__(self, service_info):
        self.service = service_info
    
    @abstractmethod
    async def find(self, track_info):
        """Ищет ссылку и возвращает данные о треке"""
        pass

class SpotifyFinder(Finder):
    @log_async_method
    async def find(self, track_info):
        try:
            import spotipy
            from spotipy.oauth2 import SpotifyClientCredentials
            
            client_credentials_manager = SpotifyClientCredentials(
                client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
            )
            sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            
            query = f"{track_info['artists']} - {track_info['title']}"
            results = sp.search(q=query, type='track', limit=1)
            items = results.get('tracks', {}).get('items', [])
            
            if items:
                track = items[0]
                url = track['external_urls']['spotify']
                
                return {
                    'service': self.service['name'],
                    'url': url,
                }
            return {
                'service': self.service['name'],
                'url': None,
            }
        except Exception as e:
            print(f"Error Finding Spotify: {e}")
            return {
                'url': None,
                'error': str(e),
                'service': self.service['name'],
            }
    
class YandexFinder(Finder):
    @log_async_method
    async def find(self, track_info):
        try:
            from yandex_music import Client
            client = Client(os.getenv("YANDEX_MUSIC_TOKEN")).init()
            track_name = f"{track_info['artists']} - {track_info['title']}"
            search_result = client.search(track_name)
            
            if search_result.best:
                type_ = search_result.best.type
                best = search_result.best.result
                
                if type_ == 'track':
                    url = f"https://music.yandex.ru/album/{best.albums[0].id}/track/{best.id}"
            
                    return {
                        'service': self.service['name'],
                        'url': url,
                    }

            return {
                'service': self.service['name'],
                'url': None,
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
    async def find(self, track_info):
        try:
            from vk_api import VkApi
            vk_session = VkApi(token=os.getenv("MTS_VK_TOKEN"))
            vk = vk_session.get_api()
            
            search_result = vk.audio.search(q=f"{track_info['artists']} - {track_info['title']}", count=1)
            if search_result['items']:
                track = search_result['items'][0]
                url = track.get('url')
                print(f"Found MTS track URL: {url}, {track}")
                return {
                    'service': self.service['name'],
                    'url': url,
                }
            return {
                'service': self.service['name'],
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
    async def find_link(self, track_info):
        try:
            results = []
            for name, finder in self.finders.items():
                if track_info.get('original_service').get('name') != finder.service["name"]:
                    result = await finder.find(track_info)
                    results.append(result)
            return results
                
        except Exception as e:
            print(f'Error parsing link: {e}')
            return {'error': 'Failed to parse link'}
        
# Для совместимости (асинхронная версия)
async def find_link(track_info):
    finder = LinkFinder()
    return await finder.find_link(track_info)