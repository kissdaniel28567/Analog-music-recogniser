# Folder Structure
---
```plantuml

@startwbs
<style>
wbsDiagram {
  ' Folder styling
  node {
    Padding 5
    Margin 10
    BackgroundColor #E0F2FE
    BorderColor #0284C7
    FontName Arial
  }
  ' File styling
  .file {
    BackgroundColor #FFFFFF
    BorderColor #94A3B8
  }
}
</style>

* Smart-Turntable-Project
** backend/
*** app/
**** api/
***** auth.py <<file>>
***** cartridges.py <<file>>
***** user.py <<file>>
**** audio/
***** capture.py <<file>>
***** processing.py <<file>>
**** services/
***** lastfm_service.py <<file>>
***** metadata_service.py <<file>>
***** recognition_service.py <<file>>
**** __init__.py <<file>>
**** extensions.py <<file>>
**** main.py <<file>>
**** models.py <<file>>
**** sockets.py <<file>>
**** state.py <<file>>
**** tasks.py <<file>>
*** instance/
**** turntable.db <<file>>
**** turntable.db.-shm <<file>>
**** turntable.db.-wal <<file>>
*** tests/
*** .asoundrc <<file>>
*** .gitignore <<file>>
*** Dockerfile <<file>>
*** requirements.txt <<file>>
*** run.py <<file>>

** frontend/
*** src/
**** assets/
***** logo.svg <<file>>
**** components/
***** ThemeSwitcher.vue <<file>>
**** composables/
***** useDashboard.js <<file>>
***** useProfile.js <<file>>
**** router/
***** index.js <<file>>
**** services/
***** api.js <<file>>
**** stores/
***** auth.js <<file>>
***** theme.js <<file>>
**** styles/
***** base.css <<file>>
***** dashboard.css <<file>>
***** profile.css <<file>>
***** themes.css <<file>>
**** views/
***** Dashboard.vue <<file>>
***** Login.vue <<file>>
***** Profile.vue <<file>>
***** Register.vue <<file>>
**** App.vue <<file>>
**** main.js <<file>>
*** .gitignore <<file>>
*** Dockerfile <<file>>
*** index.html <<file>>
*** package-lock.json <<file>>
*** package.json <<file>>
*** vite.config.js <<file>>
** .gitignore <<file>>
** docker-compose.yml <<file>>
** README.md <<file>>

@endwbs

```
---
# Database Structure (Entity Relationship Diagram)
---

```plantuml

@startuml
' --- Styling and Theme ---
skinparam roundcorner 5
skinparam shadow false
skinparam class {
    BackgroundColor #F8FAFC
    BorderColor #334155
    HeaderBackgroundColor #E2E8F0
    ArrowColor #4F46E5
}

' --- Macros for table formatting ---
!define primary_key(x) <b><color:#b8861b><&key></color> x</b>
!define foreign_key(x) <color:#aaaaaa><&link-intact></color> <i>x</i>
!define column(x) <color:#333333><&media-record></color> x
!define table(x) entity x << (T, white) >>

left to right direction

' --- Tables ---
table(User) {
  primary_key(id): Integer
  column(username): String (150)
  column(password_hash): String (200)
  -- Settings --
  column(rms_threshold): Float
  column(click_sensitivity): Float
  column(audio_device_id): Integer
  -- Last.fm --
  column(lastfm_username): String (100)
  column(lastfm_session_key): String (100)
}

table(Cartridge) {
  primary_key(id): Integer
  foreign_key(user_id): Integer
  column(name): String (150)
  column(total_hours): Float
  column(total_clicks): Integer
  column(recommended_hours): Integer
  column(is_active_on_turntable): Boolean
}

table(TrackHistory) {
  primary_key(id): Integer
  foreign_key(user_id): Integer
  column(title): String (200)
  column(artist): String (200)
  column(album): String (200)
  column(cover_art): String (500)
  column(timestamp): DateTime
}

table(AlbumColor) {
  primary_key(id): Integer
  foreign_key(user_id): Integer
  column(artist): String (200)
  column(album): String (200)
  column(color_class): String (50)
}

table(TrackOffset) {
  primary_key(id): Integer
  foreign_key(user_id): Integer
  column(artist): String (200)
  column(title): String (200)
  column(offset_seconds): Float
}

' --- Relationships ---
User ||--o{ Cartridge : " owns"
User ||--o{ TrackHistory : " listens to"
User ||--o{ AlbumColor : " customizes"
User ||--o{ TrackOffset : " syncs lyrics for" 

@enduml

```
---
# Use Case Diagram
---
```plantuml

@startuml
left to right direction
skinparam packageStyle rectangle
skinparam actorStyle hollow

actor "Vinyl Listener" as user
actor "Turntable (USB Audio)" as hardware

package "Smart Turntable Assistant" {
  usecase "Listen to Music & View Analytics" as UC1
  usecase "Manage Cartridge Lifespan" as UC2
  usecase "Read Synced Lyrics" as UC3
  usecase "Customize Vinyl Colors" as UC4
  usecase "Connect Last.fm" as UC5
  
  usecase "Identify Audio" as UC_ID
  usecase "Fetch Metadata & Cover" as UC_Meta
  usecase "Scrobble Track" as UC_Scrobble
}

actor "Shazam / ACRCloud" as API_ID
actor "Apple / YT Music" as API_Meta
actor "LRCLIB" as API_Lyrics
actor "Last.fm API" as API_Lastfm

' User Actions
user --> UC1
user --> UC2
user --> UC3
user --> UC4
user --> UC5

' Hardware Input
hardware --> UC1 : "Provides Audio Stream"

' Includes (Automatic background tasks)
UC1 ..> UC_ID : <<include>>
UC1 ..> UC_Meta : <<include>>
UC1 ..> UC_Scrobble : <<include>>
UC3 ..> API_Lyrics : <<include>>

' API Connections
UC_ID --> API_ID
UC_Meta --> API_Meta
UC_Scrobble --> API_Lastfm
UC5 --> API_Lastfm
@enduml

```
---
# Sequence Diagram
---

```plantuml

@startuml
autonumber
skinparam maxMessageSize 150

actor "Turntable" as TT
participant "Audio Thread\n(main.py)" as Audio
participant "Identification Thread\n(tasks.py)" as ID_Task
participant "Recognition\nService" as Rec_API
database "SQLite DB" as DB
participant "Vue Frontend\n(Dashboard)" as UI

TT -> Audio : Continuous Audio Stream (indata)
activate Audio

loop 10x per second
    Audio -> Audio : Check RMS & Calculate Clicks
    Audio -> UI : socketio.emit('stats_update', rms, clicks)
    
    alt Music Start Detected
        Audio -> UI : socketio.emit('status_change', 'identifying')
        Audio -> ID_Task : Spawn Thread(identify_and_save)
        activate ID_Task
        
        ID_Task -> Rec_API : Send 8s audio buffer
        activate Rec_API
        Rec_API --> ID_Task : Return Shazam/ACRCloud Match
        deactivate Rec_API
        
        alt Match Found
            ID_Task -> Rec_API : Fetch Apple Music Metadata (Duration/Cover)
            activate Rec_API
            Rec_API --> ID_Task : Return Metadata
            deactivate Rec_API
            
            ID_Task -> DB : Save TrackHistory
            activate DB
            DB --> ID_Task : Success
            deactivate DB
            
            ID_Task -> UI : socketio.emit('track_identified', track_data)
        else No Match
            ID_Task -> Audio : Increment failed_attempts
        end
        
        ID_Task -> UI : socketio.emit('status_change', 'listening')
        deactivate ID_Task
    end
end
deactivate Audio
@enduml

```

---
# Deployment / Architecture Diagram
---

```plantuml

@startuml
skinparam componentStyle uml2

node "Host Machine (Raspberry Pi / PC)" {
  
  node "Docker Engine" {
    
    component "Frontend Container" as front_cont {
      [Nginx Web Server] as nginx
      [Vue.js SPA] as vue
    }
    
    component "Backend Container" as back_cont {
      [Flask API] as flask
      [Audio Thread] as audio_thread
      database "SQLite DB" as db
    }
    
  }
  
  interface "USB Port" as usb
  [USB Audio Interface] as adc
}

' Physical connections
adc -up-> usb : Analog to Digital
usb -up-> audio_thread : /dev/snd mapping

' Network connections
vue <--> flask : REST API & Socket.IO
audio_thread -->[ACRCloud / Shazam] : HTTPS
flask --> [Apple / YT Music API] : HTTPS
flask -->[LRCLIB API] : HTTPS
flask --> [Last.fm API] : HTTPS

@enduml

```

---
# Software Class Diagram 
---

```plantuml

@startuml
skinparam classAttributeIconSize 0

class AudioProcessor {
  - sample_rate: int
  - consecutive_loud_duration: float
  - track_end_silence_duration: float
  + calculate_rms(indata: array): float
  + check_music_start(indata: array, threshold: float): bool
  + check_silence_start(indata: array, required_duration: float): bool
  + detect_clicks(indata: array, sensitivity: float): int
  + measure_rumble(indata: array): float
  + detect_sibilance(indata: array): float
}

class RecognitionService {
  - shazam: Shazam
  - acr_recognizer: ACRCloudRecognizer
  + identify_audio(file_path: str): dict
}

class MetadataService {
  - yt: YTMusic
  - _yt_duration_to_seconds(duration_str: str): float
  + enrich(artist: str, title: str, external_ids: dict): dict
  + fetch_apple(artist: str, title: str, apple_id: str): dict
  + fetch_youtube(artist: str, title: str, youtube_id: str): dict
}

class LastFmService {
  - api_key: str
  - api_secret: str
  + get_session_key(token: str): tuple
  + scrobble(artist: str, title: str, timestamp: int, session_key: str): bool
}

class GlobalState {
  + is_playing: bool
  + is_identifying: bool
  + current_track: dict
  + song_start_time: float
  + click_history: list
  + current_track_offset: float
}

' Show dependencies (who uses whom)
RecognitionService .down.> MetadataService : " passes IDs to"
@enduml

```