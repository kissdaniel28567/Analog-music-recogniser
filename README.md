# Smart Turntable Assistant

A Raspberry Pi-powered project designed to bring modern, smart features to your classic vinyl listening experience. This application analyzes the analog audio output from a turntable in real-time and presents a rich, interactive experience through a modern web interface.

## Key Features

*   **🎵 Automatic Song Identification:** Recognizes the currently playing track from the analog audio stream with high accuracy.

*   **🌐 Modern Web Interface:** A sleek, responsive UI to control and visualize your listening session, accessible from any device on your local network.

*   **📀 Animated Player Visualization:** Features a visually appealing animation of a spinning record that updates with the currently identified album art.

*   **🔊 Local Network Audio Streaming:** Broadcasts the turntable's audio over your local network, allowing you to listen in any room on your phone or computer.

*   **🎤 Synchronized Lyrics:** Fetches and displays real-time, scrolling lyrics for the recognized song.

*   **✔️ Automatic Last.fm Scrobbling:** Integrates with your Last.fm account to automatically log the tracks you play on vinyl.

*   **📊 Personal Listening Statistics:** Keeps a local database of your listening history and generates interesting stats, like your most-played artists and albums on vinyl.

*   **🩺 Vinyl & Stylus Condition Monitoring:**
    *   Detects audible artifacts like pops and clicks to give feedback on the record's condition.
    *   Tracks total playback time to provide an estimate of stylus wear and sends a notification when it's time for a replacement.

*   **💿 Rich Metadata Display:** Fetches album art, release year, and other track information from online databases like Discogs.

## Tech Stack (Planned)

*   **Hardware:** Raspberry Pi 4, USB Audio Interface (ADC)
*   **Backend:** Python (Flask), Flask-SocketIO
*   **Frontend:** React
*   **Database:** SQLite
*   **External APIs:** ACRCloud (for recognition), Last.fm, Musixmatch (for lyrics), Discogs

## Getting Started

*(TODO: Add setup instructions for hardware and software installation here.)*

## License
*(TODO: Add license info here.)*
