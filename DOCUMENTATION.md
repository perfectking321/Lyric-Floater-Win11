# 📖 Lyric-Floater-Win11 - Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Setup Guide](#setup-guide)
4. [API Configuration](#api-configuration)
5. [Module Documentation](#module-documentation)
6. [UI Components](#ui-components)
7. [Authentication Flow](#authentication-flow)
8. [Troubleshooting](#troubleshooting)
9. [Development Guidelines](#development-guidelines)

---

## Project Overview

### Description
Lyric-Floater-Win11 is a desktop application that displays real-time synchronized lyrics for Spotify tracks. It features a modern, transparent floating window with smooth animations and playback controls.

### Key Technologies
- **Language:** Python 3.8+
- **GUI Framework:** Tkinter
- **APIs:** Spotify Web API, Genius API
- **Libraries:** Spotipy, LyricsGenius, Pillow, Requests

### System Requirements
- Windows 11/10
- Python 3.8 or higher
- Spotify Premium account (required for playback control)
- Active internet connection

---

## Architecture

### Project Structure
```
Lyric-Floater-Win11/
├── main.py                      # Application entry point
├── lyricstify_fetcher.py        # Alternative entry point
├── config.json                  # API credentials configuration
├── spotify_tokens.json          # Cached Spotify tokens (auto-generated)
├── requirements.txt             # Python dependencies
├── README.md                    # Project overview
├── DOCUMENTATION.md             # This file
│
├── controllers/
│   └── spotify_controller.py   # Spotify API integration & playback control
│
├── ui/
│   ├── __init__.py
│   ├── lyrics_window.py         # Main GUI window and lyrics display
│   ├── styles.py                # UI styling constants and themes
│   └── icon.py                  # Application icon generator
│
├── utils/
│   └── __init__.py
│
├── .spotify_cache/              # OAuth token cache (auto-generated)
│   └── .spotify_cache
│
└── common.py                    # Shared utilities
    config.py                    # Configuration loader
    lyrics_fetcher.py            # Genius API lyrics fetcher
    spotify_client.py            # Legacy Spotify client
```

### Component Flow
```
┌─────────────────────────────────────────────────────────┐
│                        main.py                          │
│                  Application Entry Point                │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────────┐    ┌──────────────────────┐
│  LyricsWindow    │    │ SpotifyController    │
│  (UI Layer)      │◄───┤ (Controller Layer)   │
└────────┬─────────┘    └──────────┬───────────┘
         │                         │
         ▼                         ▼
┌──────────────────┐    ┌──────────────────────┐
│ GeniusLyrics     │    │   Spotify Web API    │
│ Fetcher          │    │   (spotipy)          │
└──────────────────┘    └──────────────────────┘
```

---

## Setup Guide

### 1. Installation

```powershell
# Clone the repository
git clone https://github.com/perfectking321/Lyric-Floater-Win11.git
cd Lyric-Floater-Win11

# Install dependencies
pip install -r requirements.txt
```

### 2. Dependencies
```
spotipy>=2.23.0
lyricsgenius>=3.0.1
Pillow>=10.0.0
requests>=2.31.0
```

### 3. First Run
```powershell
python main.py
```

---

## API Configuration

### config.json Structure
```json
{
    "spotify_client_id": "your_spotify_client_id",
    "spotify_client_secret": "your_spotify_client_secret",
    "spotify_redirect_uri": "http://localhost:8888/callback",
    "genius_access_token": "your_genius_api_token"
}
```

### Obtaining Spotify API Credentials

1. **Visit Spotify Developer Dashboard**
   - Go to: https://developer.spotify.com/dashboard
   - Log in with your Spotify account

2. **Create an App**
   - Click "Create App"
   - Fill in:
     - App Name: `Lyric Floater` (or any name)
     - App Description: `Desktop lyrics viewer`
     - Redirect URI: `http://localhost:8888/callback`
   - Check the Terms of Service box
   - Click "Save"

3. **Get Your Credentials**
   - Click "Settings" in your app dashboard
   - Copy your `Client ID`
   - Click "View client secret" and copy your `Client Secret`
   - Paste these into `config.json`

### Obtaining Genius API Token

1. **Visit Genius API**
   - Go to: https://genius.com/api-clients
   - Log in or create a Genius account

2. **Create API Client**
   - Click "New API Client"
   - Fill in:
     - App Name: `Lyric Floater`
     - App Website URL: `http://localhost`
   - Click "Save"

3. **Generate Access Token**
   - Click "Generate Access Token"
   - Copy the token
   - Paste it into `config.json` as `genius_access_token`

---

## Module Documentation

### main.py
**Purpose:** Application entry point and initialization

**Key Functions:**
- `load_config()` - Loads configuration from config.json
- `initialize_spotify(config, root)` - Sets up Spotify controller
- `initialize_lyrics_fetcher(config)` - Initializes Genius lyrics fetcher
- `main()` - Main application loop

**Usage:**
```python
python main.py
```

### controllers/spotify_controller.py
**Purpose:** Manages Spotify authentication and playback control

**Class: `SpotifyController`**

**Methods:**
- `__init__(client_id, client_secret, redirect_uri, root=None)` - Initialize controller
- `initialize_spotify()` - Set up Spotify OAuth authentication
- `test_connection()` - Verify Spotify connection
- `is_authenticated()` - Check authentication status
- `get_current_track()` - Retrieve currently playing track info
- `get_playback_state()` - Get current playback state
- `start_playback()` - Resume playback
- `pause_playback()` - Pause playback
- `next_track()` - Skip to next track
- `previous_track()` - Skip to previous track
- `bind_progress_callback(callback)` - Register progress update callback
- `update_progress()` - Update playback progress (called every 1000ms)
- `cleanup()` - Clean up resources on exit

**OAuth Flow:**
1. Checks for cached token in `.spotify_cache/`
2. If no token, displays authorization URL
3. User logs in via browser
4. User copies redirect URL with code
5. Token is obtained and cached for future use

### lyrics_fetcher.py
**Purpose:** Fetches and parses lyrics from Genius API

**Class: `GeniusLyricsFetcher`**

**Methods:**
- `__init__(access_token)` - Initialize with Genius API token
- `fetch_lyrics(artist, title)` - Search and fetch lyrics for a song
- `clean_title(title)` - Clean song title for better search results
- `parse_lyrics(lyrics_text)` - Parse and format lyrics text

**Features:**
- Intelligent title cleaning (removes feat., remix tags, etc.)
- Fallback search strategies
- Lyrics formatting and cleanup
- Error handling for API failures

### ui/lyrics_window.py
**Purpose:** Main GUI window with lyrics display and controls

**Class: `LyricsWindow`**

**Key Features:**
- Transparent window with custom styling
- Scrollable lyrics display
- Album art display
- Playback controls (play/pause, next, previous)
- Progress bar with timestamps
- Window management (minimize, maximize, always-on-top)
- Smooth glow animations for current line
- Automatic window centering on current lyric line

**Important Methods:**
- `__init__(root)` - Initialize window and UI components
- `set_spotify_controller(controller)` - Set Spotify controller reference
- `set_lyrics_fetcher(fetcher)` - Set lyrics fetcher reference
- `update_song_info()` - Update displayed song information
- `update_lyrics()` - Display fetched lyrics
- `highlight_current_line(progress_ms, duration_ms)` - Highlight current lyric
- `update_glow_effect(line_start, line_end)` - Animate glow effect
- `toggle_playback()` - Toggle play/pause
- `on_close()` - Handle window close event

### ui/styles.py
**Purpose:** Centralized styling constants

**Constants:**
```python
BACKGROUND_COLOR = "#002649"      # Dark blue background
TEXT_COLOR = "#4A90E2"            # Light blue text
HIGHLIGHT_COLOR = "#7CB7EB"       # Highlighted text
SECONDARY_COLOR = "#003366"       # Secondary elements
FONT_FAMILY = "Segoe UI"          # Main font
FONT_SIZE = 16                    # Base font size
TITLE_FONT_SIZE = 20              # Title font size
BUTTON_FONT_SIZE = 18             # Button font size
```

### ui/icon.py
**Purpose:** Generate application icon programmatically

**Function:**
- `get_icon()` - Creates a PIL Image object with app icon

---

## UI Components

### Main Window Layout
```
┌─────────────────────────────────────────────┐
│  [≡] Spotify Lyrics          [_][□][X]     │  ← Title bar with controls
├─────────────────────────────────────────────┤
│  ┌─────────────┐                            │
│  │   Album     │  Song Title                │  ← Song info section
│  │    Art      │  Artist Name               │
│  └─────────────┘  Album Name                │
├─────────────────────────────────────────────┤
│  [◄◄]  [▶||]  [►►]                         │  ← Playback controls
├─────────────────────────────────────────────┤
│  ════════════════════════                   │  ← Progress bar
│  1:23 / 3:45                                │
├─────────────────────────────────────────────┤
│                                             │
│  Lyric line 1                               │  ← Lyrics display
│  Lyric line 2                               │     (scrollable)
│  ✨ Current lyric line (highlighted) ✨     │
│  Lyric line 4                               │
│  Lyric line 5                               │
│                                             │
└─────────────────────────────────────────────┘
```

### Visual Effects
- **Glow Animation:** 10-step gradient effect on current line
- **Smooth Scrolling:** Auto-centers on highlighted line
- **Color Interpolation:** Smooth transitions between colors
- **Bold Highlighting:** Current line uses larger, bold font

---

## Authentication Flow

### Spotify OAuth 2.0 Process

```
┌──────────┐                                    ┌──────────────┐
│   User   │                                    │   Spotify    │
│  (Your   │                                    │     API      │
│   App)   │                                    │              │
└────┬─────┘                                    └──────┬───────┘
     │                                                 │
     │  1. Request Authorization URL                  │
     ├────────────────────────────────────────────────►
     │                                                 │
     │  2. Return Authorization URL                   │
     ◄────────────────────────────────────────────────┤
     │                                                 │
     │  3. User opens URL in browser                  │
     │     and logs in to Spotify                     │
     │                                                 │
     │  4. User clicks "Agree"                        │
     │                                                 │
     │  5. Redirect to localhost with code            │
     │     (page won't load - this is expected!)      │
     │                                                 │
     │  6. User copies redirect URL                   │
     │                                                 │
     │  7. App extracts code from URL                 │
     ├────────────────────────────────────────────────►
     │                                                 │
     │  8. Exchange code for access token             │
     ◄────────────────────────────────────────────────┤
     │                                                 │
     │  9. Token cached in .spotify_cache/            │
     │                                                 │
```

### Important Notes
- **"localhost refused to connect" is NORMAL** - Don't worry when you see this error
- The authorization code is in the URL, not on the page
- Copy the entire URL from your browser's address bar
- Token is cached and valid for 1 hour, then automatically refreshed

---

## Troubleshooting

### Common Issues

#### 1. "localhost refused to connect" Error
**Status:** ✅ This is expected behavior

**Solution:** 
- This is normal! Just copy the URL from your browser's address bar
- The URL contains the authorization code
- Paste the entire URL into the terminal

#### 2. Invalid Client Error
**Cause:** Incorrect Spotify credentials

**Solution:**
- Verify `spotify_client_id` in config.json
- Verify `spotify_client_secret` in config.json
- Check credentials in Spotify Developer Dashboard

#### 3. Redirect URI Mismatch
**Cause:** Redirect URI doesn't match Spotify app settings

**Solution:**
- Ensure `spotify_redirect_uri` in config.json is: `http://localhost:8888/callback`
- In Spotify Developer Dashboard, add the same URI to "Redirect URIs"
- Must match exactly (including port and path)

#### 4. No Lyrics Found
**Cause:** Song not available in Genius database

**Solution:**
- Try playing a more popular song
- Check if Genius API token is valid
- Verify internet connection

#### 5. Playback Control Not Working
**Cause:** Spotify Premium required for playback control

**Solution:**
- Spotify Premium account is required
- Free accounts can view lyrics but not control playback

#### 6. Token Expired Error
**Cause:** Cached token has expired

**Solution:**
- Delete `.spotify_cache/.spotify_cache` file
- Restart the application
- Complete authorization again

---

## Development Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose

### Error Handling
```python
try:
    # Your code here
except SpecificException as e:
    print(f"Descriptive error message: {e}")
    traceback.print_exc()  # For debugging
    # Fallback behavior
```

### Adding New Features

#### 1. New Lyrics Source
```python
# In lyrics_fetcher.py
class NewLyricsFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def fetch_lyrics(self, artist, title):
        # Implementation
        pass
```

#### 2. New UI Theme
```python
# In ui/styles.py
DARK_THEME = {
    "background": "#002649",
    "text": "#4A90E2",
    "highlight": "#7CB7EB"
}

LIGHT_THEME = {
    "background": "#FFFFFF",
    "text": "#000000",
    "highlight": "#1DB954"
}
```

#### 3. New Playback Feature
```python
# In controllers/spotify_controller.py
def seek_to_position(self, position_ms):
    """Seek to specific position in current track."""
    if self.is_authenticated() and self.sp is not None:
        self.sp.seek_track(position_ms)
```

### Testing
- Test with various songs (popular and obscure)
- Test network failure scenarios
- Test token expiration handling
- Test UI responsiveness
- Test on different Windows versions

### Building for Distribution
```powershell
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --icon=app.ico main.py
```

---

## Performance Optimization

### Current Optimizations
- Token caching (reduces API calls)
- Progress updates every 1 second (not real-time)
- Lyrics cached after first fetch
- Efficient UI updates (only when necessary)

### Potential Improvements
- Implement lyrics database cache
- Reduce GUI update frequency
- Lazy load album artwork
- Background thread for lyrics fetching

---

## Security Considerations

### Credential Storage
- **Never commit config.json to version control**
- Add to `.gitignore`:
  ```
  config.json
  spotify_tokens.json
  .spotify_cache/
  ```

### API Token Security
- Tokens stored locally only
- Cache files have restricted permissions
- No token transmission except to official APIs

---

## Version History

### Current Version: 1.0.0
- Initial release
- Spotify integration
- Genius lyrics fetching
- Modern UI with animations
- Playback controls
- Progress tracking

---

## Credits & Attribution

### APIs Used
- **Spotify Web API** - Music playback and track information
- **Genius API** - Lyrics content

### Libraries
- **spotipy** - Spotify API wrapper
- **lyricsgenius** - Genius API wrapper
- **Pillow** - Image processing
- **Tkinter** - GUI framework

### Developer
- **GitHub:** perfectking321
- **Project:** Lyric-Floater-Win11

---

## License
MIT License - See LICENSE file for details

---

## Support

### Getting Help
1. Check this documentation
2. Review the Troubleshooting section
3. Check existing GitHub issues
4. Create a new issue with:
   - Detailed problem description
   - Error messages
   - Steps to reproduce
   - System information

### Contributing
Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Last Updated:** October 24, 2025
**Documentation Version:** 1.0.0
