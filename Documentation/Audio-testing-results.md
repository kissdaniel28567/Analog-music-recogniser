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

### Detecting when a track starts
#### I have came up with the idea to use RMS calculations to determine wherethere a song have started or not. The if the RMS volume passes a threshold, we detect it as the track has started. RMS is calculated via this operation:
$$
\mathrm{RMS} = \sqrt{\frac{1}{N}\sum_{i=1}^{N} x_i^2}
$$

