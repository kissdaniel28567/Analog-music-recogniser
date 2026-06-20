import unittest
import numpy as np
from app.audio.processing import AudioProcessor

class TestAudioDSP(unittest.TestCase):
    def setUp(self):
        self.processor = AudioProcessor(sample_rate=44100)

    def test_rms_perfect_silence(self):
        """Test if a completely empty array returns 0.0 volume."""
        silent_chunk = np.zeros((4096, 2)) 
        rms = self.processor.calculate_rms(silent_chunk)
        self.assertEqual(rms, 0.0, "RMS of pure silence should be exactly 0.0")

    def test_rms_constant_signal(self):
        """Test if a constant value returns the expected RMS."""
        noise_chunk = np.full((4096, 2), 0.5)
        rms = self.processor.calculate_rms(noise_chunk)
        self.assertAlmostEqual(rms, 0.5, places=5, msg="RMS of constant 0.5 should be 0.5")

    def test_click_detection_single_spike(self):
        """Test if the statistical algorithm finds exactly one massive spike."""
        audio_chunk = np.zeros((4096, 2))
        
        audio_chunk[2000] = [1.0, 1.0] 
        
        clicks = self.processor.detect_clicks(audio_chunk, sensitivity=15)
        
        self.assertGreater(clicks, 0, "Should detect the massive injected spike")
        
    def test_stereo_rms_separation(self):
        """Test if calculate_stereo_rms correctly isolates Left and Right."""
        stereo_chunk = np.zeros((1024, 2))
        stereo_chunk[:, 1] = 1.0 
        
        left_rms, right_rms = self.processor.calculate_stereo_rms(stereo_chunk)
        
        self.assertEqual(left_rms, 0.0, "Left channel should be silent")
        self.assertEqual(right_rms, 1.0, "Right channel should be loud")
    
    def test_channel_balance_left_heavy(self):
        """Test if balance is negative when left channel is louder."""
        chunk = np.zeros((1024, 2))
        chunk[:, 0] = 0.8 # Left
        chunk[:, 1] = 0.2 # Right
        
        balance = self.processor.get_channel_balance(chunk)
        # Formula: (R-L)/(R+L) -> (0.2-0.8)/(1.0) = -0.6
        self.assertAlmostEqual(balance, -0.6, places=5)

    def test_channel_balance_perfect_center(self):
        """Test if balance is 0 when both channels are equal."""
        chunk = np.full((1024, 2), 0.5)
        balance = self.processor.get_channel_balance(chunk)
        self.assertEqual(balance, 0.0)

    def test_measure_rumble_low_freq_injection(self):
        """Test rumble detection by injecting a pure 30Hz sine wave."""
        # Generate 1 second of 30Hz sine wave
        t = np.linspace(0, 1, 44100, endpoint=False)
        # Formula: sin(2 * pi * frequency * time)
        wave_30hz = np.sin(2 * np.pi * 30 * t) 
        
        # Shape it for our processor (frames, channels)
        audio_chunk = np.column_stack((wave_30hz, wave_30hz))
        
        rumble_val = self.processor.measure_rumble(audio_chunk)
        
        # A pure 30Hz wave should produce a very high rumble value
        self.assertGreater(rumble_val, 1000)

    def test_detect_sibilance_high_freq_injection(self):
        """Test sibilance detection by injecting an 8kHz sine wave."""
        t = np.linspace(0, 0.1, int(44100 * 0.1), endpoint=False)
        wave_8khz = np.sin(2 * np.pi * 8000 * t)
        
        audio_chunk = np.column_stack((wave_8khz, wave_8khz))
        
        sibilance_val = self.processor.detect_sibilance(audio_chunk)
        self.assertAlmostEqual(sibilance_val, 1.0, places=2)