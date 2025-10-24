# 🎵 Lyric Floater - Windows 11# 🎵 Lyrics Floater Viewer



A beautiful floating lyrics window for Spotify that displays real-time synchronized lyrics on your Windows desktop. Built with Pygame for smooth animations and hardware acceleration.[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)

[![Spotify](https://img.shields.io/badge/Spotify-Premium-1DB954.svg)](https://www.spotify.com/premium/)

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

![License](https://img.shields.io/badge/license-MIT-green.svg)[![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg)](CONTRIBUTING.md)

![Platform](https://img.shields.io/badge/platform-Windows%2011-blue.svg)

<div align="center">

---  <img src="demo.gif" alt="Spotify Lyrics Viewer Demo" width="800"/>

  

## 📋 Table of Contents  *Lyric-floater: A transparent, adjustable mini-screen that displays lyrics for your Spotify songs while you work. Keep it floating beside your tasks and never miss a word while singing along. Perfect for multitaskers who want to nail every lyric without switching windows. *

</div>

- [Features](#-features)

- [Technologies & APIs](#-technologies--apis)---

- [System Requirements](#-system-requirements)

- [Installation](#-installation)## ✨ Features

- [Setup & Configuration](#-setup--configuration)

- [How It Works](#-how-it-works)<div align="center">

- [Project Architecture](#-project-architecture)

- [Configuration Options](#-configuration-options)| Feature | Description |

- [Troubleshooting](#-troubleshooting)|---------|-------------|

| ✨ Visual Effects | Smooth glowing animations for current lyrics |

---| 🎨 Modern UI | Spotify-inspired dark theme interface |

| 🖼️ Rich Media | Album art display and song information |

## ✨ Features| ⏯️ Controls | Integrated playback controls |

| 📊 Progress | Real-time progress bar with timestamps |

- **🎯 Real-time Synced Lyrics**: Line-by-line synchronized lyrics with smooth animations| 🔄 Auto-Update | Automatic lyrics fetching and updating |

- **🎨 Beautiful UI**: Modern, translucent window with smooth scrolling and transitions| 🪟 Window Management | Minimize, maximize, and always-on-top options |

- **🌐 Multi-language Support**: Full support for Hindi, English, and Unicode characters (Nirmala UI font)

- **💾 Smart Caching**: Lyrics are cached locally to reduce API calls and improve performance</div>

- **🔄 Auto-refresh**: Automatically detects song changes and updates lyrics

- **📱 Always on Top**: Floating window stays above other applications## 🚀 Quick Start

- **🎭 Multiple Data Sources**: Falls back between LRClib (synced) → Genius (plain text)

- **⚡ Hardware Accelerated**: Pygame with hardware acceleration for smooth 60 FPS rendering### Prerequisites

- **📏 Text Wrapping**: Intelligent word wrapping for long lyrics

- **🎚️ Opacity Control**: Adjustable transparency for current/past/future lyrics- Python 3.8 or higher

- Spotify Premium account

---- Genius API token



## 🛠️ Technologies & APIs### 📥 Installation



### **Core Technologies**1. **Clone the repository**

   ```bash

| Technology | Version | Purpose |   git clone https://github.com/yourusername/spotify-lyrics-viewer.git

|-----------|---------|---------|   cd spotify-lyrics-viewer

| **Python** | 3.8+ | Core programming language |   ```

| **Pygame** | 2.5.0+ | Graphics rendering and UI framework |

| **Pygame GUI** | 0.6.0+ | UI components (buttons, controls) |2. **Install dependencies**

   ```bash

### **Python Libraries**   pip install -r requirements.txt

   ```

| Library | Version | Purpose |

|---------|---------|---------|3. **Configure API credentials**

| **spotipy** | 2.23.0+ | Spotify API integration for track info |   

| **requests** | 2.31.0+ | HTTP requests for lyrics APIs |   Create `config.json` in the root directory:

| **lyricsgenius** | 3.0.1+ | Genius API integration for fallback lyrics |   ```json

| **Pillow (PIL)** | 10.0.0+ | Image processing for album artwork |   {

       "SPOTIFY_CLIENT_ID": "your_spotify_client_id",

### **APIs Used**       "SPOTIFY_CLIENT_SECRET": "your_spotify_client_secret",

       "GENIUS_ACCESS_TOKEN": "your_genius_api_token"

#### 1. **Spotify Web API**   }

- **Purpose**: Track currently playing song, artist, album info, playback position   ```

- **Authentication**: OAuth 2.0 (Authorization Code Flow)

- **Endpoints Used**:### 🎮 Usage

  - `GET /v1/me/player/currently-playing` - Get current track

  - Track metadata (name, artist, album, duration, progress)1. **Start the application**

- **Rate Limits**: 180 requests per minute   ```bash

- **Documentation**: https://developer.spotify.com/documentation/web-api   python main.py

   ```

#### 2. **LRClib API** (Primary Lyrics Source)2. **Log in to Spotify** when prompted

- **Purpose**: Free, open-source synced lyrics database3. **Play any song** and watch the magic happen!

- **Type**: REST API (No authentication required)

- **Endpoint**: `https://lrclib.net/api/get`## 🛠️ Technical Implementation

- **Features**:

  - Line-by-line timestamps in LRC format### Core Components

  - Search by track name, artist, album, duration

  - Free and open-source<details>

- **Response Format**: JSON with `syncedLyrics` field (LRC format)<summary><b>🎵 Spotify Integration</b></summary>

- **Documentation**: https://lrclib.net/docs

```python

#### 3. **Genius API** (Fallback Lyrics Source)# spotify_controller.py

- **Purpose**: Plain text lyrics when synced lyrics unavailableclass SpotifyController:

- **Authentication**: Access Token (API key)    def __init__(self):

- **Features**:        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(...))

  - Large lyrics database        

  - Plain text format (no timestamps)    def get_current_track(self):

- **Documentation**: https://docs.genius.com        return self.sp.current_playback()

```

### **System APIs**</details>



- **Windows API (`ctypes`)**: Window transparency, always-on-top, layered window attributes<details>

- **Win32 API**: Extended window styles for click-through effects<summary><b>📝 Lyrics Engine</b></summary>



---```python

# lyrics_fetcher.py

## 💻 System Requirementsclass GeniusLyricsFetcher:

    def fetch_lyrics(self, artist, title):

- **Operating System**: Windows 10/11 (64-bit)        lyrics = self.genius.search_song(title, artist)

- **Python**: 3.8 or higher        return self.parse_lyrics_with_timing(lyrics.lyrics)

- **RAM**: 256 MB minimum```

- **Display**: 1280×720 or higher resolution</details>

- **Spotify**: Desktop app (not browser version) running on the same machine

- **Internet**: Required for fetching lyrics and Spotify API<details>

<summary><b>✨ Glow Effect</b></summary>

---

```python

## 📥 Installation# lyrics_window.py

def update_glow_effect(self, line_start, line_end):

### **Step 1: Install Python**    # Create smooth color transition

    for i in range(10):

1. Download Python 3.8+ from [python.org](https://www.python.org/downloads/)        alpha = (10 - i) / 10

2. During installation, **check "Add Python to PATH"**        color = self.interpolate_color('#7CB7EB', '#FFFFFF', alpha)

3. Verify installation:        self.lyrics_text.tag_configure(f"glow_{i}", 

   ```powershell                                     foreground=color,

   python --version                                     font=(FONT_FAMILY, FONT_SIZE + 4, "bold"))

   ``````

</details>

### **Step 2: Clone/Download the Project**

## 📚 Project Structure

```powershell

# Clone with Git```

git clone https://github.com/perfectking321/Lyric-Floater-Win11.gitspotify-lyrics-viewer/

cd Lyric-Floater-Win11├── main.py                 # Application entry point

├── config.json            # Configuration file

# OR download ZIP and extract├── requirements.txt       # Dependencies

```├── src/

│   ├── controllers/

### **Step 3: Install Dependencies**│   │   ├── spotify_controller.py

│   │   └── lyrics_fetcher.py

```powershell│   ├── ui/

# Install required Python packages│   │   ├── lyrics_window.py

pip install -r requirements_pygame.txt│   │   └── styles.py

```│   └── utils/

│       └── helpers.py

### **Step 4: Verify Installation**└── cache/

    └── lyrics_cache.json

```powershell```

# Check if all packages are installed

pip list | Select-String "pygame|spotipy|requests|lyricsgenius|pillow"## 🔧 Best Practices

```

### Error Handling

---```python

try:

## ⚙️ Setup & Configuration    lyrics = lyrics_fetcher.fetch_lyrics(artist, title)

    if not lyrics:

### **1. Spotify API Setup**        display_message("No lyrics found")

except APIError as e:

You need Spotify API credentials to access currently playing track information.    log_error(f"API Error: {e}")

    display_message("Couldn't fetch lyrics")

#### **Get Spotify API Credentials:**```



1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)### Performance Optimization

2. Log in with your Spotify account- Lyrics caching system

3. Click **"Create App"**- Efficient update intervals

4. Fill in the form:- Minimal API calls

   - **App Name**: `Lyric Floater` (or any name)- Resource cleanup

   - **App Description**: `Desktop lyrics display`

   - **Redirect URI**: `http://localhost:8888/callback` ⚠️ **IMPORTANT**: Must be exactly this## 🤝 Contributing

5. Accept terms and click **"Save"**

6. Click **"Settings"** → Copy your **Client ID** and **Client Secret**1. Fork the repository

2. Create your feature branch (`git checkout -b feature/AmazingFeature`)

#### **Configure Credentials:**3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)

4. Push to the branch (`git push origin feature/AmazingFeature`)

Open `config.json` in the project folder and update:5. Open a Pull Request



```json

{## 🙏 Acknowledgments

    "spotify_client_id": "YOUR_CLIENT_ID_HERE",

    "spotify_client_secret": "YOUR_CLIENT_SECRET_HERE",- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)

    "spotify_redirect_uri": "http://localhost:8888/callback",- [Genius API](https://docs.genius.com/)

    "genius_access_token": "OPTIONAL_GENIUS_TOKEN"- [Python Tkinter](https://docs.python.org/3/library/tkinter.html)

}- [Spotipy](https://spotipy.readthedocs.io/)

```

## 🔮 Future Roadmap

### **2. Genius API Setup (Optional)**

- [ ] Multiple lyrics sources integration

Genius provides fallback lyrics when LRClib doesn't have synced lyrics.- [ ] Customizable themes and animations

- [ ] Offline mode with cached lyrics

1. Go to [Genius API Clients](https://genius.com/api-clients)- [ ] Multi-language support

2. Create a new API Client- [ ] Karaoke mode with timing markers

3. Generate an **Access Token**- [ ] User preferences panel

4. Add it to `config.json`:- [ ] Lyrics editing capability

   ```json- [ ] Export/share functionality

   "genius_access_token": "YOUR_GENIUS_TOKEN_HERE"

   ```

---

⚠️ **Note**: If you skip this, the app will only use LRClib (which is free and sufficient for most songs).

<div align="center">

### **3. First Run Authentication**  

Made with ❤️ by [perfectking321]

When you first run the app:

⭐ Star this repository if you find it helpful!

1. Start the application:

   ```powershell</div> 

   python main_pygame.py
   ```

2. A browser window will open asking you to authorize the app
3. Log in to Spotify and click **"Agree"**
4. You'll be redirected to `localhost:8888/callback` (may show error - that's OK!)
5. Copy the **entire URL** from browser address bar
6. Paste it into the terminal and press Enter
7. Authentication token is saved in `.spotify_cache/` for future use

---

## 🚀 How to Run

### **Basic Usage**

```powershell
# Navigate to project folder
cd Lyric-Floater-Win11

# Run the application
python main_pygame.py
```

### **What to Expect:**

1. **Window Opens**: Translucent floating window appears
2. **Play Spotify**: Start playing any song on Spotify Desktop
3. **Lyrics Load**: Lyrics appear automatically (2-3 seconds delay)
4. **Sync Animation**: Current line highlights and scrolls smoothly
5. **Auto-Update**: Changes automatically when you switch songs

### **Controls:**

- **Window**: Drag to move, resize by dragging edges
- **Close**: Click × button or press Alt+F4
- **Minimize**: Window can be minimized to taskbar

---

## 🔄 How It Works

### **Complete Workflow (Step-by-Step)**

```
┌─────────────────────────────────────────────────────────────┐
│                     APPLICATION START                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  1. INITIALIZATION PHASE                                     │
│  ─────────────────────────                                   │
│  • Load config.json (API credentials)                        │
│  • Initialize Pygame window (800×600, resizable)            │
│  • Load fonts (Nirmala UI → Segoe UI → Arial)               │
│  • Setup text renderer with color cache                      │
│  • Create sprite manager for lyric animation                 │
│  • Initialize Spotify client with OAuth                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. SPOTIFY AUTHENTICATION                                   │
│  ──────────────────────────                                  │
│  • Check for cached token (.spotify_cache/)                  │
│  • If no cache: Open browser for OAuth authorization         │
│  • User logs in and grants permissions                       │
│  • Receive authorization code                                │
│  • Exchange code for access token (1 hour validity)          │
│  • Save token to cache for future runs                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. MAIN EVENT LOOP (60 FPS)                                 │
│  ────────────────────────────                                │
│  Every frame (16.67ms):                                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  A. Poll Spotify API (every 1 second)               │    │
│  │     • GET /me/player/currently-playing              │    │
│  │     • Extract: track_id, name, artist, album,       │    │
│  │                duration_ms, progress_ms              │    │
│  └─────────────────────────────────────────────────────┘    │
│                       ↓                                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  B. Detect Song Change                              │    │
│  │     • Compare current track_id with previous        │    │
│  │     • If different → Trigger lyrics fetch           │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  4. LYRICS FETCHING WORKFLOW                                 │
│  ────────────────────────────                                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Step 1: Check Local Cache                          │    │
│  │  ────────────────────────                           │    │
│  │  • Look in lyrics_cache/{artist}_{song}.json        │    │
│  │  • If found: Load and skip API calls                │    │
│  │  • Cache format: {synced_lyrics: [...], plain: ""} │    │
│  └─────────────────────────────────────────────────────┘    │
│                       ↓ (Cache miss)                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Step 2: Try LRClib API (Synced Lyrics)            │    │
│  │  ────────────────────────────────────               │    │
│  │  • API: https://lrclib.net/api/get                  │    │
│  │  • Parameters:                                       │    │
│  │    - track_name: Song name                          │    │
│  │    - artist_name: Artist name                       │    │
│  │    - album_name: Album name (optional)              │    │
│  │    - duration: Song duration in SECONDS             │    │
│  │                                                      │    │
│  │  • Response: JSON with "syncedLyrics" field         │    │
│  │  • Format: LRC (Line with timestamp)                │    │
│  │    Example:                                          │    │
│  │    [00:12.50]First line here                        │    │
│  │    [00:15.80]Second line here                       │    │
│  │                                                      │    │
│  │  • Parse LRC: Extract timestamps & text             │    │
│  │  • Convert to: [(timestamp_ms, "line text"), ...]   │    │
│  │                                                      │    │
│  │  ✅ Success: Cache and use synced lyrics            │    │
│  │  ❌ Fail (404/400): Try Genius API                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                       ↓ (LRClib failed)                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Step 3: Fallback to Genius API (Plain Text)       │    │
│  │  ─────────────────────────────────────              │    │
│  │  • Search Genius for song                           │    │
│  │  • Get song URL                                      │    │
│  │  • Scrape lyrics from page                          │    │
│  │  • Format: Plain text (no timestamps)               │    │
│  │  • Display as static text (no sync animation)       │    │
│  │                                                      │    │
│  │  ✅ Success: Cache and display plain lyrics         │    │
│  │  ❌ Fail: Show "Lyrics not found"                   │    │
│  └─────────────────────────────────────────────────────┘    │
│                       ↓                                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Step 4: Cache Result                               │    │
│  │  ───────────────────                                │    │
│  │  • Save to lyrics_cache/{artist}_{song}.json        │    │
│  │  • Structure:                                        │    │
│  │    {                                                 │    │
│  │      "synced_lyrics": [[time_ms, "text"], ...],    │    │
│  │      "plain_lyrics": "full text...",                │    │
│  │      "source": "lrclib" or "genius"                 │    │
│  │    }                                                 │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  5. LYRICS RENDERING & ANIMATION                             │
│  ────────────────────────────────                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  A. Create Lyric Sprites                            │    │
│  │     • One sprite per line                           │    │
│  │     • Text wrapping for long lines (max width)      │    │
│  │     • Initial opacity: 0.4 (future lines)           │    │
│  │     • Position: Y = header + (line_index × 50px)    │    │
│  └─────────────────────────────────────────────────────┘    │
│                       ↓                                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  B. Sync Animation Loop (for synced lyrics)         │    │
│  │     Every frame:                                     │    │
│  │     • Get current playback position (progress_ms)   │    │
│  │     • Find matching timestamp in lyric array        │    │
│  │     • If new line: Update current_index             │    │
│  │                                                      │    │
│  │     • Update opacities:                              │    │
│  │       - Current line: 1.0 (100% bright)             │    │
│  │       - Past lines: 0.5 (50% dim)                   │    │
│  │       - Future lines: 0.4 (40% dim)                 │    │
│  │                                                      │    │
│  │     • Smooth scroll to center current line:         │    │
│  │       - Calculate: base_y = line_index × 50         │    │
│  │       - Target: center_y = window_height / 2        │    │
│  │       - Scroll: base_y - center_y                   │    │
│  │       - Apply smooth interpolation (15% per frame)  │    │
│  │                                                      │    │
│  │     • Update sprite positions with scroll offset    │    │
│  │     • Re-render changed sprites                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                       ↓                                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  C. Draw to Screen                                   │    │
│  │     • Clear screen (black background)               │    │
│  │     • Draw header (song info, album art)            │    │
│  │     • Draw visible lyric sprites (culling)          │    │
│  │     • Draw controls (play/pause, progress bar)      │    │
│  │     • Apply window transparency (layered window)    │    │
│  │     • Flip display buffer (60 FPS)                  │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  6. EVENT HANDLING                                           │
│  ──────────────────                                          │
│  • Window Resize: Recreate sprites, restore scroll position │
│  • Window Close: Save state, cleanup, exit                   │
│  • Mouse Click: Handle UI button interactions                │
│  • Song Change: Clear cache, restart workflow from Step 4    │
└─────────────────────────────────────────────────────────────┘
```

### **Data Flow Diagram**

```
Spotify Desktop → Spotify API → Application → LRClib API ──✅→ Synced Lyrics
                                      ↓                            ↓
                                      └─→ Genius API ──✅→ Plain Lyrics
                                                ↓
                                        Local Cache (.json)
                                                ↓
                                      Pygame Renderer
                                                ↓
                                        Screen Display
```

---

## 🏗️ Project Architecture

### **Directory Structure**

```
Lyric-Floater-Win11/
├── main_pygame.py              # Application entry point
├── config.json                 # API credentials configuration
├── requirements_pygame.txt     # Python dependencies
│
├── spotify_client.py           # Spotify API integration
├── lrclib_fetcher.py          # LRClib API (synced lyrics)
├── lyrics_fetcher.py          # Lyrics coordinator (LRClib → Genius)
├── config.py                   # Configuration loader
├── common.py                   # Shared utilities
│
├── ui/                         # User Interface components
│   ├── pygame_lyrics_window.py    # Main window & game loop
│   ├── pygame_sprite_manager.py   # Lyric sprites & animations
│   ├── pygame_text_renderer.py    # Text rendering & caching
│   ├── pygame_ui_components.py    # UI buttons & controls
│   ├── styles.py                  # Colors, fonts, constants
│   ├── icon.py                    # Application icon
│   ├── color_cache.py             # Color utilities (internal)
│   └── __init__.py
│
├── controllers/                # Business logic
│   └── spotify_controller.py      # Spotify polling & callbacks
│
├── lyrics_cache/              # Cached lyrics (JSON)
│   ├── {Artist}_{Song}.json      # Individual song cache files
│   └── ...
│
├── .spotify_cache/            # Spotify OAuth tokens
│   └── .spotify_cache            # Token file (auto-generated)
│
└── utils/                      # Utility modules
    └── __init__.py
```

### **Core Modules Explained**

#### **1. `main_pygame.py`**
- Application entry point
- Initializes all systems
- Starts the main event loop

#### **2. `spotify_client.py`**
- Wraps Spotipy library
- Handles OAuth authentication
- Polls currently playing track
- Provides track metadata

#### **3. `lrclib_fetcher.py`**
- Fetches synced lyrics from LRClib
- Parses LRC format (timestamps + text)
- Converts to `[(timestamp_ms, "text"), ...]`

#### **4. `lyrics_fetcher.py`**
- Coordinates lyrics fetching
- Priority: Cache → LRClib → Genius
- Manages local cache files
- Returns unified format

#### **5. `ui/pygame_lyrics_window.py`**
- Main window class
- Pygame event loop (60 FPS)
- Handles window events (resize, close)
- Manages UI updates
- Syncs playback position with lyrics

#### **6. `ui/pygame_sprite_manager.py`**
- Creates lyric line sprites
- Manages animations (opacity, position)
- Smooth scrolling logic
- Auto-centers current line
- Text wrapping for long lines

#### **7. `ui/pygame_text_renderer.py`**
- Font loading (Nirmala UI, Segoe UI, Arial)
- Text rendering with opacity
- Color interpolation
- Render cache for performance

#### **8. `ui/styles.py`**
- Color definitions (hex codes)
- Font sizes and families
- Layout constants (header height, padding)
- Opacity values for different line states

---

## ⚙️ Configuration Options

### **config.json Settings**

```json
{
    "spotify_client_id": "string",        // Spotify API Client ID (required)
    "spotify_client_secret": "string",    // Spotify API Client Secret (required)
    "spotify_redirect_uri": "string",     // OAuth redirect (must be http://localhost:8888/callback)
    "genius_access_token": "string"       // Genius API token (optional)
}
```

### **styles.py Constants**

You can customize the appearance by editing `ui/styles.py`:

```python
# Window Settings
WINDOW_WIDTH = 800           # Initial window width (px)
WINDOW_HEIGHT = 600          # Initial window height (px)
FPS = 60                     # Frame rate

# Colors (Hex format)
BG_COLOR = "#000000"         # Background color (black)
TEXT_COLOR = "#FFFFFF"       # Text color (white)
HEADER_BG = "#1A1A1A"        # Header background
CONTROL_BG = "#1A1A1A"       # Control panel background

# Opacity Values
OPACITY_CURRENT = 1.0        # Current line brightness (100%)
OPACITY_PAST = 0.5           # Past lines brightness (50%)
OPACITY_FUTURE = 0.4         # Future lines brightness (40%)

# Layout
HEADER_HEIGHT = 120          # Top header height (px)
CONTROL_HEIGHT = 120         # Bottom control panel height (px)
LYRICS_PADDING = 40          # Left/right padding for lyrics (px)
LINE_HEIGHT = 50             # Spacing between lyric lines (px)

# Fonts
FONT_FAMILY_PRIORITY = [
    "Nirmala UI",            # Best for Hindi
    "Segoe UI",              # Good for English
    "Arial"                  # Universal fallback
]
FONT_SIZE_NORMAL = 24        # Normal lyric lines
FONT_SIZE_CURRENT = 32       # Current highlighted line
```

### **Cache Settings**

- **Location**: `lyrics_cache/`
- **Format**: JSON
- **Naming**: `{Artist}_{Song}.json`
- **Expiration**: Never (manual deletion required)
- **Clear Cache**: Delete files in `lyrics_cache/` folder

---

## 🐛 Troubleshooting

### **Common Issues & Solutions**

#### **1. "No module named 'pygame'"**
```powershell
# Install dependencies
pip install -r requirements_pygame.txt
```

#### **2. "Spotify authorization failed"**
**Cause**: Invalid credentials or redirect URI mismatch

**Solution**:
- Verify `config.json` has correct Client ID and Secret
- Ensure redirect URI is EXACTLY: `http://localhost:8888/callback`
- Delete `.spotify_cache/` folder and re-authenticate

#### **3. "Lyrics not found" for all songs**
**Possible Causes**:
- No internet connection
- LRClib API down
- Missing Genius token (optional)

**Solutions**:
- Check internet connection
- Try songs from popular artists (better lyrics coverage)
- Add Genius API token to `config.json`

#### **4. Window appears but no lyrics show**
**Checks**:
1. Is Spotify Desktop app running? (not browser)
2. Is a song currently playing?
3. Check terminal for error messages
4. Try clearing cache: Delete `lyrics_cache/` contents

#### **5. Hindi/Unicode text shows as boxes □□□**
**Cause**: Nirmala UI font not found

**Solution**:
- Windows 11 should have Nirmala UI by default
- Fallback to Segoe UI (may not display all Hindi characters)
- Install Nirmala UI font manually if missing

#### **6. Lyrics not syncing (wrong timing)**
**Possible Causes**:
- LRClib timestamps are user-submitted (may be inaccurate)
- Network delay in polling Spotify API

**Solution**:
- Try refreshing (change song and return)
- Report incorrect lyrics to LRClib community
- Use Genius fallback (plain text, no sync)

#### **7. "Access token expired"**
**Cause**: Spotify token lifetime is 1 hour

**Solution**:
- App should auto-refresh token
- If fails: Delete `.spotify_cache/` and restart app
- Re-authenticate when browser opens

#### **8. High CPU usage**
**Cause**: 60 FPS rendering + smooth animations

**Solutions**:
- Reduce FPS in `styles.py`: `FPS = 30`
- Close other resource-heavy apps
- Normal usage: 5-10% CPU on modern systems

#### **9. Lyrics not centered after window resize**
**Status**: Fixed in latest version

**If still occurring**:
- Restart the application
- Ensure using latest code from repository

---

## 🔧 Advanced Configuration

### **Running on Startup (Windows)**

1. Create a shortcut to `main_pygame.py`
2. Press `Win + R`, type `shell:startup`, press Enter
3. Copy the shortcut to the Startup folder

### **Running in Background**

```powershell
# Use pythonw to hide console window
pythonw main_pygame.py
```

### **Custom Window Size**

Edit `ui/styles.py`:
```python
WINDOW_WIDTH = 1000   # Your preferred width
WINDOW_HEIGHT = 800   # Your preferred height
```

---

## 📝 API Rate Limits & Best Practices

### **Spotify API**
- **Limit**: 180 requests/minute
- **Polling Interval**: 1 second (60 req/min)
- **Well within limits** ✅

### **LRClib API**
- **Limit**: No official limit (free service)
- **Caching**: Recommended (implemented)
- **Be respectful**: Don't spam requests

### **Genius API**
- **Limit**: Varies by account tier
- **Usage**: Only fallback when LRClib fails
- **Caching**: Essential (implemented)

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **LRClib**: Free synced lyrics database
- **Spotify**: Music streaming and API
- **Genius**: Lyrics fallback source
- **Pygame**: Graphics and UI framework
- **Spotipy**: Python Spotify API wrapper

---

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Read troubleshooting section above

---

**Made with ❤️ for music lovers**
