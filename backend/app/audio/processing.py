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

    def detect_clicks(self, indata, sensitivity=10):
        """
        Detects pops and clicks using statistical outlier detection on the signal derivative.
        
        Args:
            indata: The audio chunk.
            sensitivity: How many standard deviations a spike must be to count as a click.
                         Lower = more sensitive (might detect drums as clicks).
                         Higher = less sensitive (only detects huge pops).
        
        Returns:
            int: The number of clicks detected in this chunk.
        """
        # 1. Convert to mono for analysis
        if indata.shape[1] > 1:
            mono_data = np.mean(indata, axis=1)
        else:
            mono_data = indata.flatten()

        # 2. Calculate the 'First Difference' (Derivative)
        diff = np.diff(mono_data)

        # 3. Calculate Statistics
        abs_diff = np.abs(diff)
        mean_val = np.mean(abs_diff)
        std_dev = np.std(abs_diff)

        if std_dev == 0:
            return 0

        # 4. Count outliers
        threshold = mean_val + (sensitivity * std_dev)
        
        click_mask = abs_diff > threshold
        num_clicks = np.sum(click_mask)
        
        return int(num_clicks)
    
    def get_channel_balance(self, indata):

        """
        Calculates the stereo balance based on RMS levels of left and right channels.

        Args:
            indata (numpy.ndarray): 2‑channel audio data.

        Returns:
            float: Balance value between -1 (left‑heavy) and +1 (right‑heavy).
                Returns 0 if both channels are silent.
        """

        rms_left = self.calculate_rms(indata[:, 0])
        rms_right = self.calculate_rms(indata[:, 1])
        
        if rms_left + rms_right == 0:
            return 0 

        balance = (rms_right - rms_left) / (rms_right + rms_left)
        return balance
    
    def measure_rumble(self, indata):
        """
        Measures low‑frequency rumble by summing FFT energy between 10–50 Hz.

        Args:
            indata (numpy.ndarray): 2‑channel audio data.

        Returns:
            float: Total spectral energy in the 10–50 Hz band.
        """

        fft_spectrum = np.fft.rfft(indata[:, 0]) # Analyze left channel
        frequencies = np.fft.rfftfreq(len(indata), d=1/self.sample_rate)
        
        idx_low = np.argmax(frequencies > 10)
        idx_high = np.argmax(frequencies > 50)

        rumble_energy = np.sum(np.abs(fft_spectrum[idx_low:idx_high]))
        return rumble_energy