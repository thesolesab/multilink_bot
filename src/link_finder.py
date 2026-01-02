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
            import urllib.parse
            
            token = os.getenv("YANDEX_MUSIC_TOKEN")
            if not token:
                # Если токен не установлен, возвращаем ссылку на поиск
                track_name = f"{track_info['artists']} - {track_info['title']}"
                return {
                    'service': self.service['name'],
                    'url': f'https://music.yandex.ru/search?text={urllib.parse.quote(track_name)}',
                }
            
            client = Client(token).init()
            track_name = f"{track_info['artists']} - {track_info['title']}"
            
            try:
                search_result = client.search(track_name, type_='track', page=0, playlist_in_best=True)
                
                # Пытаемся найти трек в результатах поиска
                if search_result and search_result.tracks:
                    tracks = search_result.tracks.results
                    if tracks:
                        # Берем первый результат
                        track = tracks[0]
                        if track and track.albums:
                            url = f"https://music.yandex.ru/album/{track.albums[0].id}/track/{track.id}"
                            return {
                                'service': self.service['name'],
                                'url': url,
                            }
                
                # Если не нашли через tracks, пробуем через best
                if search_result.best:
                    try:
                        type_ = search_result.best.type
                        if type_ == 'track':
                            best = search_result.best.result
                            if best and best.albums:
                                url = f"https://music.yandex.ru/album/{best.albums[0].id}/track/{best.id}"
                                return {
                                    'service': self.service['name'],
                                    'url': url,
                                }
                    except Exception as best_error:
                        print(f"Error processing best result: {best_error}")
                        # Продолжаем выполнение
                        pass
                        
            except Exception as search_error:
                print(f"Error in Yandex search: {search_error}")
                # Возвращаем ссылку на поиск при ошибке
                pass

            # Если ничего не нашли, возвращаем ссылку на поиск
            return {
                'service': self.service['name'],
                'url': f'https://music.yandex.ru/search?text={urllib.parse.quote(track_name)}',
            }
        except Exception as e:
            print(f"Error Finding Yandex: {e}")
            import traceback
            traceback.print_exc()
            # При любой ошибке возвращаем ссылку на поиск вместо None
            track_name = f"{track_info['artists']} - {track_info['title']}"
            import urllib.parse
            return {
                'service': self.service['name'],
                'url': f'https://music.yandex.ru/search?text={urllib.parse.quote(track_name)}',
                'error': str(e),
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
                'url': f'https://music.mts.ru/search?text={track_info['artists']} - {track_info['title']}',
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