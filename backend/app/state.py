class GlobalState:
    is_playing = False
    is_identifying = False
    current_track = {'title': '', 'artist': '', 'album': '', 'cover': None, 'color': 'v-classic', 'lyrics': ''}
    song_start_time = None
    click_history = []
    
    rms = 0.0
    current_clicks = 0
    
    stop_thread = False
    failed_attempts = 0
    track_duration = 180
    is_userdetect = False
    is_paused = False
    temp_start_time = None

state = GlobalState()