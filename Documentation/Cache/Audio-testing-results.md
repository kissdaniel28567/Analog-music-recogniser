# Audio recognition
### I have tested 3 audio recognition services being:
- Acrcloud
- Acustid
- Shazamio

#### First of all, I did not want to write my own AI or audio recognition software because as of my research, the databases that store data from songs are paid services mainly for coorporative use. I did not want my project this big financially, so I have backed out of the idea.

#### As of the results, at the end there was a clear winner. I have testes Acrcloud first, which had free subscribtion before, but as of today, it only has a 14 day free trial. They are not providing a good pricing plan for my project, since they are charging for each recognition particularly. I would have to scan each song, so this is not fitting my project. The second contender was AcustId, which is an open-source, free software, that has big database of songs and metadata. But this service can only recognise a song if there is no noise in the file, which is not good for my purpose since vinyl can have noises on it, mainly surface noise, pitch shifting, pops. This service was not able to recognise any of my records, so I have moved on to the Shazamio service. Shazamio can detect an song even if it has noise, and it only needs 5-8 second of the song to recognise it. So this makes it clear that I have sticked with Shazamio since it fits the project perfectly.

# Audio analyzing
### First of all, let's clear how python is managing sound coming in from a recorded audio.
#### In our case, we record in stereo, so there will be two channels, left and right. They will have different numbers based on their loudness. They will be stored in a matrix where rows are the samples and the columns are the channels. Quick example:
``` python 
indata = np.array([
    [ 0.012, -0.011],   # frame 0: left, right
    [ 0.015, -0.014],   # frame 1
    [ 0.980, -0.975],   # BIG spike
    [ 0.014, -0.013],
])
 ```

## Detecting when a track starts
#### I have came up with the idea to use RMS calculations to determine wherethere a song have started or not. The if the RMS volume passes a threshold, we detect it as the track has started. RMS is calculated via this operation:
$$
\mathrm{RMS} = \sqrt{\frac{1}{N}\sum_{i=1}^{N} x_i^2}
$$

## Click Detection Algorithm
This algorithm detects audio clicks and pops by identifying statistically significant, short-duration transients in the time domain.

### Overview
Clicks are characterized by abrupt, high-amplitude changes between adjacent audio samples. The algorithm emphasizes these changes using a first-difference operation and detects them as statistical outliers relative to normal signal behavior within a short time block.

---

### Algorithm Steps

1. **Channel Reduction (Stereo → Mono)**  
   If the input signal has multiple channels, they are averaged to produce a single mono signal:
   - Reduces dimensionality
   - Preserves broadband transients such as clicks

2. **First Difference (Discrete Derivative)**  
   The mono signal is differenced sample-to-sample:
   $$
   d[n] = x[n] - x[n-1]
   $$
   This acts as a first-order high-pass filter, suppressing slowly varying audio content and emphasizing rapid transients.

3. **Rectification**  
   The absolute value of the derivative is taken:
   $$
   |d[n]|
   $$
   This ensures both positive and negative spikes caused by clicks are treated equally.

4. **Statistical Modeling**  
   The mean ($\mu$) and standard deviation ($\sigma$) of the absolute derivative are computed over the block:
   $$\mu = \mathbb{E}[|d[n]|], \quad \sigma = \sqrt{\mathbb{E}[(|d[n]| - \mu)^2]}$$
   These values characterize the typical sample-to-sample variation of the signal.

5. **Adaptive Thresholding (Outlier Detection)**  
   A detection threshold is defined as:
   $$
   T = \mu + k\sigma
   $$
   where $k$ is a user-defined sensitivity parameter. Samples exceeding this threshold are classified as click candidates.

6. **Click Counting**  
   The total number of samples exceeding the threshold is counted. Each physical click may produce multiple detections due to its bipolar and oscillatory nature.

---

### Notes and Limitations
- The algorithm operates entirely in the time domain.
- It assumes clicks are rare, high-energy events relative to normal audio.
- Percussive sounds may produce false positives.
- Detected counts represent threshold crossings, not clustered click events.

---

### Summary
This method implements derivative-based transient detection with adaptive statistical thresholding. It is computationally efficient and well-suited for real-time or block-based audio analysis.


## Measuring Stereo Balance

To understand whether the audio is leaning toward the left or the right channel, I compare the **RMS** (root mean square) loudness of both channels. RMS gives a stable representation of perceived loudness.

The stereo balance is then computed using this formula:

$$
\text{balance} = \frac{R - L}{R + L}
$$

Where:

*   L = RMS of the left channel
*   R = RMS of the right channel

This produces a value between **-1 and +1**:

*   **-1** → fully left
*   **0** → centered
*   **+1** → fully right

If both channels are silent, the balance is simply reported as **0**.

***

## Measuring Low‑Frequency Rumble

Turntables and vinyl playback often produce unwanted low‑frequency noise known as *rumble*. To quantify this, I take the **FFT** (Fast Fourier Transform) of the incoming audio and look specifically at the frequency range between **10 Hz and 50 Hz**, which is where rumble typically occurs.

After computing the FFT:

$$
X(f) = \text{FFT of the signal}
$$

I sum the magnitude of all spectral components in the rumble band:

$$
\text{rumble energy} = \sum_{f=10}^{50} |X(f)|
$$

This provides a simple numeric value representing how much low‑frequency mechanical noise is present in the audio.
