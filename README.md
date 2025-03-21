# 🎵 Lyrics Floater Viewer

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Spotify](https://img.shields.io/badge/Spotify-Premium-1DB954.svg)](https://www.spotify.com/premium/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg)](CONTRIBUTING.md)

<div align="center">
  <img src="demo.gif" alt="Spotify Lyrics Viewer Demo" width="800"/>
  
  *A modern, real-time lyrics viewer for Spotify with beautiful visual effects*
</div>

---

## ✨ Features

<div align="center">

| Feature | Description |
|---------|-------------|
| ✨ Visual Effects | Smooth glowing animations for current lyrics |
| 🎨 Modern UI | Spotify-inspired dark theme interface |
| 🖼️ Rich Media | Album art display and song information |
| ⏯️ Controls | Integrated playback controls |
| 📊 Progress | Real-time progress bar with timestamps |
| 🔄 Auto-Update | Automatic lyrics fetching and updating |
| 🪟 Window Management | Minimize, maximize, and always-on-top options |

</div>

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Spotify Premium account
- Genius API token

### 📥 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/spotify-lyrics-viewer.git
   cd spotify-lyrics-viewer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API credentials**
   
   Create `config.json` in the root directory:
   ```json
   {
       "SPOTIFY_CLIENT_ID": "your_spotify_client_id",
       "SPOTIFY_CLIENT_SECRET": "your_spotify_client_secret",
       "GENIUS_ACCESS_TOKEN": "your_genius_api_token"
   }
   ```

### 🎮 Usage

1. **Start the application**
   ```bash
   python main.py
   ```
2. **Log in to Spotify** when prompted
3. **Play any song** and watch the magic happen!

## 🛠️ Technical Implementation

### Core Components

<details>
<summary><b>🎵 Spotify Integration</b></summary>

```python
# spotify_controller.py
class SpotifyController:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(...))
        
    def get_current_track(self):
        return self.sp.current_playback()
```
</details>

<details>
<summary><b>📝 Lyrics Engine</b></summary>

```python
# lyrics_fetcher.py
class GeniusLyricsFetcher:
    def fetch_lyrics(self, artist, title):
        lyrics = self.genius.search_song(title, artist)
        return self.parse_lyrics_with_timing(lyrics.lyrics)
```
</details>

<details>
<summary><b>✨ Glow Effect</b></summary>

```python
# lyrics_window.py
def update_glow_effect(self, line_start, line_end):
    # Create smooth color transition
    for i in range(10):
        alpha = (10 - i) / 10
        color = self.interpolate_color('#7CB7EB', '#FFFFFF', alpha)
        self.lyrics_text.tag_configure(f"glow_{i}", 
                                     foreground=color,
                                     font=(FONT_FAMILY, FONT_SIZE + 4, "bold"))
```
</details>

## 📚 Project Structure

```
spotify-lyrics-viewer/
├── main.py                 # Application entry point
├── config.json            # Configuration file
├── requirements.txt       # Dependencies
├── src/
│   ├── controllers/
│   │   ├── spotify_controller.py
│   │   └── lyrics_fetcher.py
│   ├── ui/
│   │   ├── lyrics_window.py
│   │   └── styles.py
│   └── utils/
│       └── helpers.py
└── cache/
    └── lyrics_cache.json
```

## 🔧 Best Practices

### Error Handling
```python
try:
    lyrics = lyrics_fetcher.fetch_lyrics(artist, title)
    if not lyrics:
        display_message("No lyrics found")
except APIError as e:
    log_error(f"API Error: {e}")
    display_message("Couldn't fetch lyrics")
```

### Performance Optimization
- Lyrics caching system
- Efficient update intervals
- Minimal API calls
- Resource cleanup

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## 🙏 Acknowledgments

- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
- [Genius API](https://docs.genius.com/)
- [Python Tkinter](https://docs.python.org/3/library/tkinter.html)
- [Spotipy](https://spotipy.readthedocs.io/)

## 🔮 Future Roadmap

- [ ] Multiple lyrics sources integration
- [ ] Customizable themes and animations
- [ ] Offline mode with cached lyrics
- [ ] Multi-language support
- [ ] Karaoke mode with timing markers
- [ ] User preferences panel
- [ ] Lyrics editing capability
- [ ] Export/share functionality


---

<div align="center">
  
Made with ❤️ by [perfectking321]

⭐ Star this repository if you find it helpful!

</div> 
