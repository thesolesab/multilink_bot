import pytest
from unittest.mock import AsyncMock, patch
from src.link_parser import LinkParser, SpotifyParser, YandexParser, MTSParser
from src.constants import SERVICES

class TestLinkParser:
    def test_init(self):
        parser = LinkParser()
        assert 'Spotify' in parser.parsers
        assert 'YandexMusic' in parser.parsers
        assert 'MTS' in parser.parsers
    
    @pytest.mark.asyncio
    async def test_parse_spotify_link(self):
        parser = LinkParser()
        
        with patch.object(parser.parsers['Spotify'], 'parse', new_callable=AsyncMock) as mock_parse:
            mock_parse.return_value = {
                'url': 'https://open.spotify.com/track/123',
                'original_service': SERVICES['Spotify'],
                'title': 'Song Title',
                'artists': 'Artist Name',
            }
            
            result = await parser.parse_link('https://open.spotify.com/track/123')
            
            assert result['title'] == 'Song Title'
            assert result['artists'] == 'Artist Name'
            assert result['url'] == 'https://open.spotify.com/track/123'
    
    @pytest.mark.asyncio
    async def test_parse_yandex_link(self):
        parser = LinkParser()
        
        with patch.object(parser.parsers['YandexMusic'], 'parse', new_callable=AsyncMock) as mock_parse:
            mock_parse.return_value = {
                'url': 'https://music.yandex.ru/track/456',
                'original_service': SERVICES['YandexMusic'],
                'title': 'Yandex Song',
                'artists': 'Yandex Artist',
            }
            
            result = await parser.parse_link('https://music.yandex.ru/track/456')
            
            assert result['title'] == 'Yandex Song'
            assert result['artists'] == 'Yandex Artist'
            assert result['url'] == 'https://music.yandex.ru/track/456'
    
    @pytest.mark.asyncio
    async def test_parse_mts_link(self):
        parser = LinkParser()
        
        with patch.object(parser.parsers['MTS'], 'parse', new_callable=AsyncMock) as mock_parse:
            mock_parse.return_value = {
                'url': 'https://mts-music-spo.onelink.me/test',
                'original_service': SERVICES['MTS'],
                'title': 'MTS Song',
                'artists': 'MTS Artist',
            }
            
            result = await parser.parse_link('https://mts-music-spo.onelink.me/test')
            
            assert result['title'] == 'MTS Song'
            assert result['artists'] == 'MTS Artist'
            assert result['url'] == 'https://mts-music-spo.onelink.me/test'

class TestSpotifyParser:
    pass

class TestYandexParser:
    pass

class TestMTSParser:
    pass