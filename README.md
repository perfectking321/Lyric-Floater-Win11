# Lyric-Floater Win11

A floating lyrics display application that integrates with Spotify to show real-time lyrics while you multitask.

Lyric-Floater Screenshot

## Features

- **Always-on-Top Window**: Lyrics float above other applications for easy reference while multitasking
- **Customizable Appearance**: Adjust font, size, colors, and opacity to match your desktop theme
- **System Tray Integration**: Minimize to system tray for discreet operation
- **Manual Search**: Look up lyrics for any song even without Spotify playing
- **Offline Mode**: Cached lyrics for previously viewed songs


## Requirements

- Python 3.7+
- Spotify Developer Account (for API credentials)
- Genius Developer Account (for lyrics API credentials)
- Windows 11 (optimized for this OS)


## Installation

1. Clone this repository:

```
git clone https://github.com/yourusername/lyric-floater.git
cd lyric-floater
```

2. Install required dependencies:

```
pip install -r requirements.txt
```

3. Set up API credentials:
    - Create a Spotify Developer account at [developer.spotify.com](https://developer.spotify.com)
    - Register a new application and get your Client ID and Client Secret
    - Create a Genius API account at [genius.com/api-clients](https://genius.com/api-clients)
    - Generate an API key
4. Configure the application:
    - Open `config.py` and enter your API credentials
    - Or use the Settings window in the application to enter your credentials

## Usage

1. Run the application:

```
python main.py
```

2. Authorize with Spotify when prompted
3. Play a song on Spotify
4. Lyrics will automatically display in the floating window
5. Right-click on the window for additional options
6. Minimize to system tray by clicking the minimize button

## Troubleshooting

- **System Tray Icon Not Visible**: Check Windows 11 notification settings to ensure icons are set to "always show"
- **Missing Lyrics**: Some songs may not have lyrics available in the Genius database
- **Authentication Issues**: Ensure your Spotify Client ID is correctly entered in the settings


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
- [Genius API](https://docs.genius.com/)
- [pystray](https://github.com/moses-palmer/pystray)

<div style="text-align: center">⁂</div>


