import pylast

class LastFmService:
    def __init__(self):
        self.api_key = "27e187684baf9e1ba38abf679eb1c2b7"
        self.api_secret = "18b61b646c308956644e677a8ba46017"

    def get_session_key(self, token):
        """Exchanges the temporary web token for a permanent session key."""
        try:
            network = pylast.LastFMNetwork(api_key=self.api_key, api_secret=self.api_secret)
            sg = pylast.SessionKeyGenerator(network)
            session_key, username = sg.get_web_auth_session_key(url="", token=token)
            return session_key, username
        except Exception as e:
            print(f"⚠️ Last.fm Session Error: {e}")
            raise e

    def scrobble(self, artist, title, album, timestamp, session_key):
        """Sends the scrobble data to the Last.fm server."""
        if not session_key:
            raise ValueError("No Last.fm session key provided.")

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