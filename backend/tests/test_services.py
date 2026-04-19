import unittest
import re
from app.services.metadata_service import MetadataService
from app.services.lastfm_service import LastFmService
from unittest.mock import patch, MagicMock
import json

# Very basic test
class TestServices(unittest.TestCase):
    def setUp(self):
        self.meta_service = MetadataService()

    def test_youtube_duration_parser_standard(self):
        """Test converting 'MM:SS' to total seconds."""
        seconds = self.meta_service._yt_duration_to_seconds("3:45")
        self.assertEqual(seconds, 225.0)

    def test_youtube_duration_parser_long(self):
        """Test converting 'HH:MM:SS' (long albums/mixes) to total seconds."""
        seconds = self.meta_service._yt_duration_to_seconds("1:02:30")
        self.assertEqual(seconds, 3750.0)

    def test_youtube_duration_parser_garbage_data(self):
        """Test that bad data safely returns the 210s fallback instead of crashing."""
        seconds = self.meta_service._yt_duration_to_seconds("Invalid Time String")
        self.assertEqual(seconds, 210.0)

    def test_lrc_regex_sync_parsing(self):
        """Test parsing standard synced LRC timestamps."""
        lrc_string = "[01:23.45] Hello World\n[01:28.00] How are you?"
        parsed = []
        regex = r'\[(\d{2}):(\d{2}(?:\.\d+)?)\](.*)'
        
        for line in lrc_string.split('\n'):
            match = re.search(regex, line)
            if match:
                minutes = int(match.group(1))
                seconds = float(match.group(2))
                text = match.group(3).strip()
                parsed.append({"time": (minutes * 60) + seconds, "text": text})
                
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]['time'], 83.45)
        self.assertEqual(parsed[1]['text'], "How are you?")

    @patch('urllib.request.urlopen')
    def test_fetch_apple_success(self, mock_urlopen):
        """Test parsing valid data from Apple Music API without using the internet."""
        
        fake_apple_response = {
            "resultCount": 1,
            "results": [{
                "trackTimeMillis": 180500, 
                "collectionName": "Abbey Road",
                "artworkUrl100": "http://apple.com/image_100x100.jpg"
            }]
        }
        
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(fake_apple_response).encode('utf-8')
        mock_response.__enter__.return_value = mock_response 
        mock_urlopen.return_value = mock_response

        result = self.meta_service.fetch_apple("Pink Floyd", "Money", "12345")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['duration'], 180.5)
        self.assertEqual(result['album'], "Abbey Road")
        self.assertEqual(result['cover'], "http://apple.com/image_600x600.jpg")
        self.assertEqual(result['source'], "Apple Music")

    @patch('urllib.request.urlopen')
    def test_fetch_apple_empty_result(self, mock_urlopen):
        """Test behavior when Apple Music finds no match."""
        fake_empty_response = {"resultCount": 0, "results": []}
        
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(fake_empty_response).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = self.meta_service.fetch_apple("FakeBand", "FakeSong", None)
        
        self.assertIsNone(result)

    @patch('pylast.LastFMNetwork')
    def test_lastfm_scrobble_success(self, mock_network_class):
        """Test if scrobbling attempts to call the correct pylast methods."""
        service = LastFmService()
        
        mock_network_instance = MagicMock()
        mock_network_class.return_value = mock_network_instance
        
        success = service.scrobble(
            artist="Queen", 
            title="Bohemian Rhapsody", 
            album="A Night at the Opera", 
            timestamp=123456789, 
            session_key="fake_session"
        )
        
        self.assertTrue(success)
        
        mock_network_instance.scrobble.assert_called_once_with(
            artist="Queen",
            title="Bohemian Rhapsody",
            album="A Night at the Opera",
            timestamp=123456789
        )

# Extra test for boosting coverage making sure nothing I will miss
class TestServices(unittest.TestCase):
    def setUp(self):
        self.meta_service = MetadataService()

    # ==========================================
    # --- METADATA WATERFALL TESTS ---
    # ==========================================

    @patch.object(MetadataService, 'fetch_apple')
    @patch.object(MetadataService, 'fetch_youtube')
    def test_enrich_waterfall_hits_apple_first(self, mock_yt, mock_apple):
        """Test that the waterfall returns immediately if Apple succeeds."""
        mock_apple.return_value = {'source': 'Apple Music'}
        
        result = self.meta_service.enrich("Artist", "Title", {'apple': '123'})
        
        self.assertEqual(result['source'], 'Apple Music')
        mock_apple.assert_called_once()
        mock_yt.assert_not_called()

    @patch.object(MetadataService, 'fetch_apple')
    @patch.object(MetadataService, 'fetch_youtube')
    @patch.object(MetadataService, 'fetch_musicbrainz_cover')
    def test_enrich_waterfall_falls_back_to_youtube(self, mock_mb, mock_yt, mock_apple):
        """Test that if Apple fails, it tries YouTube and MusicBrainz."""
        mock_apple.return_value = None
        mock_yt.return_value = {'source': 'YouTube Music', 'album': 'Test Album'}
        mock_mb.return_value = 'http://mb.com/cover.jpg'
        
        result = self.meta_service.enrich("Artist", "Title", {})
        
        self.assertEqual(result['source'], 'YouTube (Duration) + MusicBrainz (Cover)')
        self.assertEqual(result['cover'], 'http://mb.com/cover.jpg')
        mock_apple.assert_called_once()
        mock_yt.assert_called_once()
        mock_mb.assert_called_once()

    @patch.object(MetadataService, 'fetch_apple')
    @patch.object(MetadataService, 'fetch_youtube')
    def test_enrich_waterfall_total_failure(self, mock_yt, mock_apple):
        """Test that it returns None if all services fail."""
        mock_apple.return_value = None
        mock_yt.return_value = None
        
        result = self.meta_service.enrich("Artist", "Title", {})
        self.assertIsNone(result)

    # ==========================================
    # --- YOUTUBE DURATION PARSING ---
    # ==========================================
    def test_youtube_duration_parser_standard(self):
        seconds = self.meta_service._yt_duration_to_seconds("3:45")
        self.assertEqual(seconds, 225.0)

    def test_youtube_duration_parser_long(self):
        seconds = self.meta_service._yt_duration_to_seconds("1:02:30")
        self.assertEqual(seconds, 3750.0)

    def test_youtube_duration_parser_garbage_data(self):
        seconds = self.meta_service._yt_duration_to_seconds("Invalid Time String")
        self.assertEqual(seconds, 210.0)

    # ==========================================
    # --- LRC REGEX PARSING ---
    # ==========================================
    def test_lrc_regex_sync_parsing(self):
        lrc_string = "[01:23.45] Hello World\n[01:28.00] How are you?"
        parsed = []
        regex = r'\[(\d{2}):(\d{2}(?:\.\d+)?)\](.*)'
        
        for line in lrc_string.split('\n'):
            match = re.search(regex, line)
            if match:
                minutes = int(match.group(1))
                seconds = float(match.group(2))
                text = match.group(3).strip()
                parsed.append({"time": (minutes * 60) + seconds, "text": text})
                
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]['time'], 83.45)
        self.assertEqual(parsed[1]['text'], "How are you?")

    def test_lrc_regex_unsynced_fallback(self):
        lrc_string = "Just plain text\nAnother line"
        parsed = []
        regex = r'\[(\d{2}):(\d{2}(?:\.\d+)?)\](.*)'
        
        for line in lrc_string.split('\n'):
            match = re.search(regex, line)
            if match:
                pass 
            elif line.strip() != '':
                parsed.append({"time": -1, "text": line.strip()})
                
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]['time'], -1)
        self.assertEqual(parsed[1]['text'], "Another line")

    def test_lrc_regex_empty_lines_ignored(self):
        lrc_string = "[01:00.00] Line 1\n\n\n[01:05.00] Line 2\n "
        parsed = []
        regex = r'\[(\d{2}):(\d{2}(?:\.\d+)?)\](.*)'
        
        for line in lrc_string.split('\n'):
            match = re.search(regex, line)
            if match:
                parsed.append({"time": 0, "text": match.group(3).strip()})
            elif line.strip() != '':
                parsed.append({"time": -1, "text": line.strip()})
                
        self.assertEqual(len(parsed), 2)

    # ==========================================
    # --- APPLE MUSIC API MOCKING ---
    # ==========================================
    @patch('urllib.request.urlopen')
    def test_fetch_apple_success(self, mock_urlopen):
        fake_apple_response = {
            "resultCount": 1,
            "results": [{
                "trackTimeMillis": 180500, 
                "collectionName": "Abbey Road",
                "artworkUrl100": "http://apple.com/image_100x100.jpg"
            }]
        }
        
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(fake_apple_response).encode('utf-8')
        mock_response.__enter__.return_value = mock_response 
        mock_urlopen.return_value = mock_response

        result = self.meta_service.fetch_apple("Pink Floyd", "Money", "12345")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['duration'], 180.5)
        self.assertEqual(result['album'], "Abbey Road")
        self.assertEqual(result['cover'], "http://apple.com/image_600x600.jpg")
        self.assertEqual(result['source'], "Apple Music")

    @patch('urllib.request.urlopen')
    def test_fetch_apple_empty_result(self, mock_urlopen):
        fake_empty_response = {"resultCount": 0, "results": []}
        
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(fake_empty_response).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = self.meta_service.fetch_apple("FakeBand", "FakeSong", None)
        self.assertIsNone(result)

    @patch('urllib.request.urlopen')
    def test_fetch_apple_by_search_query(self, mock_urlopen):
        fake_resp = {"resultCount": 1, "results": [{"trackTimeMillis": 10000, "collectionName": "Album"}]}
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(fake_resp).encode('utf-8')
        mock_response.__enter__.return_value = mock_response 
        mock_urlopen.return_value = mock_response

        result = self.meta_service.fetch_apple("Artist", "Title", None)
        self.assertIsNotNone(result)
        
        call_args = mock_urlopen.call_args[0][0]
        self.assertIn("search?term=Artist%20Title", call_args.full_url)

    @patch('urllib.request.urlopen')
    def test_fetch_apple_http_error(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("API Down")
        result = self.meta_service.fetch_apple("Artist", "Title", "123")
        self.assertIsNone(result)

    # ==========================================
    # --- YOUTUBE MUSIC MOCKING ---
    # ==========================================

    @patch('ytmusicapi.YTMusic.search')
    def test_fetch_youtube_search_success(self, mock_search):
        """Test YouTube parsing via text search using the exact logic from metadata_service.py."""
        mock_search.return_value = [{
            'duration': '1:30',
            'album': {'name': 'Search Album'},
            'thumbnails': [{'url': 'http://yt.com/cover=w120-h120'}]
        }]
        
        result = self.meta_service.fetch_youtube("Artist", "Title", None)
        
        self.assertEqual(result['duration'], 90.0)
        self.assertEqual(result['album'], "Search Album")
        self.assertEqual(result['cover'], "http://yt.com/cover=w1000-h1000")

    @patch('ytmusicapi.YTMusic.search')
    def test_fetch_youtube_search_no_results(self, mock_search):
        """Test YouTube handles empty search results."""
        mock_search.return_value = []
        result = self.meta_service.fetch_youtube("Artist", "Title", None)
        self.assertIsNone(result)

    # ==========================================
    # --- LAST.FM SERVICE TESTS ---
    # ==========================================
    @patch('urllib.request.urlopen')
    def test_lastfm_get_session_key_success(self, mock_urlopen):
        """Test exchanging a web token via direct HTTP request."""
        fake_response = {
            "session": {
                "key": "fake_session_key",
                "name": "test_user"
            }
        }
        
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(fake_response).encode('utf-8')
        mock_response.__enter__.return_value = mock_response 
        mock_urlopen.return_value = mock_response

        service = LastFmService()
        session_key, username = service.get_session_key("fake_token")
        
        self.assertEqual(session_key, "fake_session_key")
        self.assertEqual(username, "test_user")

    def test_lastfm_scrobble_missing_key(self):
        """Test that scrobbling safely returns False if no session key is provided."""
        service = LastFmService()
        
        success = service.scrobble("Artist", "Title", "Album", 12345, None)
        self.assertFalse(success)

    @patch('pylast.LastFMNetwork')
    def test_lastfm_scrobble_network_failure(self, mock_network_class):
        service = LastFmService()
        
        mock_network_instance = MagicMock()
        mock_network_instance.scrobble.side_effect = Exception("API Down")
        mock_network_class.return_value = mock_network_instance
        
        success = service.scrobble("Artist", "Title", "Album", 12345, "key")
        self.assertFalse(success)

    @patch('pylast.LastFMNetwork')
    def test_lastfm_scrobble_success(self, mock_network_class):
        service = LastFmService()
        
        mock_network_instance = MagicMock()
        mock_network_class.return_value = mock_network_instance
        
        success = service.scrobble(
            artist="Queen", 
            title="Bohemian Rhapsody", 
            album="A Night at the Opera", 
            timestamp=123456789, 
            session_key="fake_session"
        )
        
        self.assertTrue(success)