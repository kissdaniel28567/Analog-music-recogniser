import numpy as np

class AudioProcessor:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        
        self.consecutive_loud_duration = 0
        self.is_playing = False
        
    def calculate_rms(self, indata):
        """
        Calculates the Root Mean Square of a given file.
        """
        data_float = indata.astype(np.float32)
        
        # RMS = square root of the mean of the squares
        rms = np.sqrt(np.mean(data_float**2))
        return rms

    def check_music_start(self, indata, threshold=0.01, required_duration=0.5, chunk_duration=0.1):
        """
        Determines if music has started based on sustained volume.

        Args:
            indata: The audio chunk.
            threshold: The RMS value above which we consider 'sound' (not silence).
            required_duration: How many seconds of sustained sound we need.
            chunk_duration: The length of this specific audio chunk in seconds.

        Returns:
            True if music has started, False otherwise.
        """
        rms = self.calculate_rms(indata)
        
        if rms > threshold:
            self.consecutive_loud_duration += chunk_duration
        else:
            self.consecutive_loud_duration = 0
            
        if not self.is_playing and self.consecutive_loud_duration >= required_duration:
            self.is_playing = True
            return True
            
        return False

    def reset_state(self):
        """Resets the detection state (e.g., when the track ends)."""
        self.consecutive_loud_duration = 0
        self.is_playing = False