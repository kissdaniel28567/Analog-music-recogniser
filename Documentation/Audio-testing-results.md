# Audio recognition
### I have tested 3 audio recognition services being:
- Acrcloud
- Acustid
- Shazamio

#### First of all, I did not want to write my own AI or audio recognition software because as of my research, the databases that store data from songs are paid services mainly for coorporative use. I did not want my project this big financially, so I have backed out of the idea.

#### As of the results, at the end there was a clear winner. I have testes Acrcloud first, which had free subscribtion before, but as of today, it only has a 14 day free trial. They are not providing a good pricing plan for my project, since they are charging for each recognition particularly. I would have to scan each song, so this is not fitting my project. The second contender was AcustId, which is an open-source, free software, that has big database of songs and metadata. But this service can only recognise a song if there is no noise in the file, which is not good for my purpose since vinyl can have noises on it, mainly surface noise, pitch shifting, pops. This service was not able to recognise any of my records, so I have moved on to the Shazamio service. Shazamio can detect an song even if it has noise, and it only needs 5-8 second of the song to recognise it. So this makes it clear that I have sticked with Shazamio since it fits the project perfectly.
