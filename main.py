import tkinter as tk
import json
import os
import sys
import traceback

# Add the current directory to the path to ensure modules can be found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.lyrics_window import LyricsWindow
from controllers.spotify_controller import SpotifyController
from lyrics_fetcher import GeniusLyricsFetcher

def load_config():
    """Load configuration from config.json file."""
    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        print(f"Loading config from: {config_path}")
        
        if not os.path.exists(config_path):
            print("Config file not found!")
            return None
            
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        required_keys = [
            'spotify_client_id',
            'spotify_client_secret',
            'spotify_redirect_uri',
            'genius_access_token'
        ]
        
        missing_keys = [key for key in required_keys if not config.get(key)]
        if missing_keys:
            print(f"Missing required configuration keys: {', '.join(missing_keys)}")
            return None
            
        print("Successfully loaded config!")
        return config
        
    except FileNotFoundError:
        print("Config file not found. Please create a config.json file.")
        return None
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in config file: {e}")
        return None
    except Exception as e:
        print(f"Error loading config: {e}")
        traceback.print_exc()
        return None

def initialize_spotify(config, root):
    """Initialize Spotify controller with error handling."""
    try:
        print("Initializing Spotify controller...")
        spotify_controller = SpotifyController(
            client_id=config['spotify_client_id'],
            client_secret=config['spotify_client_secret'],
            redirect_uri=config['spotify_redirect_uri'],
            root=root
        )
        print("Spotify controller initialized!")
        return spotify_controller
    except Exception as e:
        print(f"Error initializing Spotify controller: {e}")
        traceback.print_exc()
        return None

def initialize_lyrics_fetcher(config):
    """Initialize lyrics fetcher with error handling."""
    try:
        print("Initializing lyrics fetcher...")
        lyrics_fetcher = GeniusLyricsFetcher(config['genius_access_token'])
        print("Lyrics fetcher initialized!")
        return lyrics_fetcher
    except Exception as e:
        print(f"Error initializing lyrics fetcher: {e}")
        traceback.print_exc()
        return None

def main():
    # Load configuration
    config = load_config()
    if not config:
        print("Failed to load configuration. Please ensure config.json exists and is properly formatted.")
        return
    
    try:
        # Create main window
        root = tk.Tk()
        root.title("Spotify Lyrics")
        
        # Create and configure the lyrics window first
        print("Creating lyrics window...")
        lyrics_window = LyricsWindow(root)
        
        # Initialize Spotify controller
        spotify_controller = initialize_spotify(config, root)
        if not spotify_controller:
            print("Failed to initialize Spotify controller!")
            return
        
        # Initialize lyrics fetcher
        lyrics_fetcher = initialize_lyrics_fetcher(config)
        if not lyrics_fetcher:
            print("Failed to initialize lyrics fetcher!")
            return
        
        # Set the controllers using the setter methods
        print("Setting up controllers...")
        lyrics_window.set_spotify_controller(spotify_controller)
        lyrics_window.set_lyrics_fetcher(lyrics_fetcher)
        
        print("Application initialized successfully!")
        print("Waiting for Spotify playback...")
        
        # Start the main event loop
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        traceback.print_exc()
    finally:
        # Cleanup
        if 'spotify_controller' in locals():
            spotify_controller.cleanup()

if __name__ == "__main__":
    main()
