import os
import re
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from yandex_music import Client as YandexClient
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

sp = Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

yandex_client = YandexClient()

SPOTIFY_REGEX = r'open\.spotify\.com/(track|album|playlist)/([a-zA-Z0-9]+)'
YANDEX_REGEX = r'music\.yandex\.ru/album/(\d+)/track/(\d+)'
MTS_REGEX = r'mts-music-spo\.onelink\.me/sKFX/([a-zA-Z0-9]+)'

SERVICES={
    "spotify": {
        "name": "Spotify",
        "url": "https://open.spotify.com/track/{}",
        "search": lambda query: sp.search(q=query, type='track', limit=1)
    },
    "yandex": {
        "name": "Yandex Music",
        "url": "https://music.yandex.ru/album/{}/track/{}",
        "search": lambda query: yandex_client.search(query).tracks.results[0] if yandex_client.search(query).tracks else None
    },
    "mts": {
        "name": "MTS Music",
        "url": "https://mts.music.ru/track/{}",
        "search": lambda query: search_mts(query)
    }
}

def search_mts(query):
    try:
        url = "https://api.mtsmusic.ru/v1/search"
        params = {"q": query, "type": "tracks", "limit": 1}
        response = requests.get(url, params=params)
        data = response.json()

        if data.get("tracks") and data["tracks"]["data"]:
            track = data["tracks"]["data"][0]
            return track
        return None
    except:
        return None
    
def get_mts_track_info(track_id):
    url = f"https://music.mts.ru/track/{track_id}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    
    try:
        response = requests.get(url, headers=headers,timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.find("meta", property="og:title")["content"]

def extract_track_info(url):

    # Check Spotify
    spotfy_match = re.search(SPOTIFY_REGEX, url)
    if spotfy_match:
        track_id = spotfy_match.group(1)
        track = sp.track(track_id)
        return {
            "artist":track['artists'][0]['name'],
            "title":track['name'],
            "source":"spotify",
            "id":track_id
        }
    
    # Check Yandex Music
    yandex_match = re.search(YANDEX_REGEX, url)
    if yandex_match:
        album_id = yandex_match.group(1)
        track_id = yandex_match.group(2)
        track = yandex_client.tracks([f"{track_id}:{album_id}"])[0]
        return {
            "artist":track.artists[0].name,
            "title":track.title,
            "source":"yandex",
            "id":(album_id, track_id),
            "album_id":album_id,
        }
    
    # Check MTS Music
    mts_match = re.search(MTS_REGEX, url)
    if mts_match:
        track_id = mts_match.group(1)
        response = requests.get(f"https://api.mtsmusic.ru/v1/tracks/{track_id}")
        track = response.json()['data']
        if track:
            return {
                "artist":track['artist']['name'],
                "title":track['title'],
                "source":"mts",
                "id":track_id
            }
         
    return None

def clean_query(artist, title):
    title = re.sub(r'\(feat.*?\)', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\[.*?\]', '', title)
    return f"{artist} {title}".strip()

def search_on_all_services(artist, title):
    query = clean_query(artist, title)
    links={}

    #Spotify
    try:
        spotify_result = SERVICES['spotify']['search'](query)
        if spotify_result and spotify_result['tracks']['items']:
            track_id=spotify_result['tracks']['items'][0]['id']
            links['spotify'] = SERVICES['spotify']['url'].format(track_id)
    except:
        pass
    
    #Yandex Music
    try:
        yandex_result = SERVICES['yandex']['search'](query)
        if yandex_result:
            album_id = yandex_result.albums[0].id
            track_id = yandex_result.id
            links['yandex'] = SERVICES['yandex']['url'].format(album_id, track_id)
    except:
        pass
    
    #MTS Music
    try:
        mts_result = search_mts(query)
        if mts_result:
            track_id = mts_result['id']
            links['mts'] = SERVICES['mts']['url'].format(track_id)
    except:
        pass
    
    return links

def format_mukltilink(links, original_source):
    service_names={
        "spotify":"🟢 Spotify",
        "yandex":"🟠 Yandex Music",
        "mts":"🟡 MTS Music"
    }
    
    message = "🎵 Multi-link:\n\n"
    
    for service, url in links.items():
        if service != original_source:
            message += f"🎧 {service_names[service]}: {url}\n"
            
    if links.get(original_source):
        message += f"\n🔗 Original link ({service_names[original_source]}):\n{links[original_source]}"

    return message

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Hello! Send me a music track link from Spotify, Yandex Music, or MTS Music, and I'll provide you with multi-links to the track on other services.")   
    
@dp.message()
async def handle_link(message: Message):
    url = message.text
    
    if not (url.startswith("http://") or url.startswith("https://")):
        await message.answer("Please send a valid URL.")
        return
    
    try:
        track_info = extract_track_info(url)
        
        if not track_info:
            await message.answer("Could not extract track information from the provided link. Please ensure it's a valid link from Spotify, Yandex Music, or MTS Music.")
            return
        
        artist = track_info['artist']
        title = track_info['title']
        source = track_info['source']
        
        links = search_on_all_services(track_info["artist"], track_info["title"])
        
        if not links:
            await message.answer("Could not find the track on other services.")
            return
        
        response = format_mukltilink(links, track_info["source"])
        await message.answer(response)
        
    except Exception as e:
        print(f"Error: {e}")
        await message.answer(f"An error occurred while processing your request. Please try again later.")
        
async def main():
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())