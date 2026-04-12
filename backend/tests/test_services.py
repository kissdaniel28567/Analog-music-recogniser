import unittest
import re
from app.services.metadata_service import MetadataService
from app.services.lastfm_service import LastFmService
from unittest.mock import patch, MagicMock
import json

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