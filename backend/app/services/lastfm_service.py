import pylast
import hashlib
import urllib.request
import json

class LastFmService:
    def __init__(self):
        self.api_key = "38a0db497a6bcbcc8794b2b12a5dc8fd"
        self.api_secret = "8a5cea7a443d7627d4d7b106e5adc6a3"

    def get_session_key(self, token):
        """Exchanges the temporary web token for a permanent session key via direct API call."""
        try:
            sig_string = f"api_key{self.api_key}methodauth.getSessiontoken{token}{self.api_secret}"
            api_sig = hashlib.md5(sig_string.encode('utf-8')).hexdigest()
            
            url = f"http://ws.audioscrobbler.com/2.0/?method=auth.getSession&api_key={self.api_key}&token={token}&api_sig={api_sig}&format=json"
            
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if 'session' in data:
                    session_key = data['session']['key']
                    username = data['session']['name']
                    return session_key, username
                else:
                    raise Exception("Session not found in Last.fm response")
                    
        except Exception as e:
            print(f"⚠️ Last.fm Session Error: {e}")
            raise e

    def scrobble(self, artist, title, album, timestamp, session_key):
        """Sends the scrobble data to the Last.fm server."""
        if not session_key:
            print("⚠️ No session key provided for scrobble")
            return False

        try:
            network = pylast.LastFMNetwork(
                api_key=self.api_key, 
                api_secret=self.api_secret, 
                session_key=session_key
            )
            
            network.scrobble(
                artist=artist, 
                title=title, 
                timestamp=timestamp,
                album=album
            )
            return True
        except Exception as e:
            print(f"⚠️ Last.fm Scrobble Error: {e}")
            return False