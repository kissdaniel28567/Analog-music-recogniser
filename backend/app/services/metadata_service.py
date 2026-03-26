# backend/app/services/metadata_service.py
import urllib.request, urllib.parse, json, re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from ytmusicapi import YTMusic

class MetadataService:
    def __init__(self, spotify_client_id=None, spotify_secret=None):
        self.yt = YTMusic()
        self.sp = None
        if spotify_client_id and spotify_secret:
            try:
                auth_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_secret)
                self.sp = spotipy.Spotify(auth_manager=auth_manager)
            except Exception as e:
                print(f"⚠️ Spotify Auth Failed: {e}")

    def enrich(self, artist, title, external_ids):
        """ Fetching further data from external sources: Apple -> YT """

        data = self.fetch_apple(artist, title, external_ids.get('apple'))
        if data: return data

        data = self.fetch_youtube(artist, title, external_ids.get('youtube'))
        if data: return data

        return None

    def fetch_apple(self, artist, title, apple_id):
        """ Fetches Apple music API"""
        try:
            if apple_id:
                url = f"https://itunes.apple.com/lookup?id={apple_id}"
            else:
                query = urllib.parse.quote(f"{artist} {title}")
                url = f"https://itunes.apple.com/search?term={query}&entity=song&limit=1"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'SmartTurntable/1.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                res = json.loads(response.read().decode())
                if res['resultCount'] > 0:
                    t = res['results'][0]
                    return {
                        'duration': t.get('trackTimeMillis', 0) / 1000.0,
                        'album': t.get('collectionName', 'Unknown Album'),
                        'cover': t.get('artworkUrl100', '').replace('100x100', '600x600'),
                        'source': 'Apple Music'
                    }
        except Exception:
            pass
        return None

    def fetch_youtube_fallback(self, artist, title):
        return {
            'duration': 210.0,
            'album': 'Unknown Album',
            'cover': None,
            'source': 'Fallback'
        }
    
    def _yt_duration_to_seconds(self, duration_str):
        """Converts '3:45' or '1:02:30' to seconds."""
        try:
            parts = list(map(int, duration_str.split(':')))
            if len(parts) == 2: # mm:ss
                return parts[0] * 60 + parts[1]
            if len(parts) == 3: # hh:mm:ss
                return parts[0] * 3600 + parts[1] * 60 + parts[2]
        except:
            return 210.0
        return 210.0
    
    def fetch_youtube(self, artist, title, youtube_id=None):
        try:
            print(f"🏗️ Attempting YouTube Music lookup for: {artist} - {title}")
            
            search_query = f"{artist} {title}"
            results = self.yt.search(search_query, filter="songs", limit=1)
            
            if results:
                track = results[0]
                
                album_data = track.get('album')
                album_name = album_data.get('name') if album_data else 'Unknown Album'
                
                duration = track.get('duration_seconds')
                if not duration:
                    duration = self._yt_duration_to_seconds(track.get('duration', '3:30'))
                
                cover_url = None
                thumbnails = track.get('thumbnails',[])
                if thumbnails:
                    # Get the default URL provided by YouTube
                    base_url = thumbnails[-1].get('url', '')
                    import re
                    if '=' in base_url:
                        cover_url = re.sub(r'=w\d+-h\d+', '=w600-h600', base_url)
                    else:
                        cover_url = base_url

                print(f"   -> YT Music Album: {album_name}")
                
                return {
                    'duration': float(duration),
                    'album': album_name,
                    'cover': cover_url,
                    'source': 'YouTube Music'
                }
            else:
                print("   -> ⚠️ No official song match found on YouTube Music.")
                
        except Exception as e:
            print(f"⚠️ YouTube Music Fetch Error: {e}")
        
        return None