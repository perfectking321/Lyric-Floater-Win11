import sys
import os
import json

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.pygame_lyrics_window import PygameLyricsWindow
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
        print(f"Error parsing config.json: {e}")
        return None
    except Exception as e:
        print(f"Error loading config: {e}")
        return None


def main():
    """Main entry point"""
    print("=" * 60)
    print("🎮 LYRICS FLOATER - PYGAME VERSION (Hardware Accelerated)")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    if not config:
        print("\n❌ Failed to load configuration. Please check config.json")
        input("Press Enter to exit...")
        return
    
    print("\n✅ Configuration loaded successfully")
    
    try:
        # Create Pygame window first
        print("\n🎮 Initializing Pygame window...")
        window = PygameLyricsWindow()
        print("✅ Pygame window created (60 FPS)")
        
        # Initialize Spotify controller (no root needed for Pygame)
        print("\n🎵 Initializing Spotify controller...")
        spotify_controller = SpotifyController(
            client_id=config['spotify_client_id'],
            client_secret=config['spotify_client_secret'],
            redirect_uri=config['spotify_redirect_uri'],
            root=None  # Pygame handles its own event loop
        )
        print("✅ Spotify controller initialized")
        
        # Initialize lyrics fetcher
        print("\n📝 Initializing lyrics fetcher...")
        lyrics_fetcher = GeniusLyricsFetcher(
            api_token=config['genius_access_token']
        )
        print("✅ Lyrics fetcher initialized")
        
        # Set controllers in window
        window.set_controllers(spotify_controller, lyrics_fetcher)
        
        # Start Spotify progress updates in background
        import threading
        def progress_update_loop():
            import time
            while window.running:
                try:
                    # Get current playback state
                    track = spotify_controller.get_current_track()
                    if track and spotify_controller.sp:
                        # Get progress from current playback
                        sp_playback = spotify_controller.sp.current_playback()
                        if sp_playback:
                            progress_ms = sp_playback.get('progress_ms', 0)
                            duration_ms = track.get('duration_ms', 0)
                            window.on_progress_update(progress_ms, duration_ms)
                except:
                    pass
                time.sleep(0.25)  # 250ms updates
        
        progress_thread = threading.Thread(target=progress_update_loop, daemon=True)
        progress_thread.start()
        
        print("\n" + "=" * 60)
        print("✨ READY! Window launched with hardware acceleration")
        print("=" * 60)
        print("\n📖 Controls:")
        print("   - ESC: Exit")
        print("   - SPACE: Play/Pause")
        print("   - F1: Toggle performance stats")
        print("   - Drag header: Move window")
        print("\n🚀 Running at 60 FPS with GPU acceleration\n")
        
        # Run main loop (blocking)
        window.run()
        
        print("\n👋 Goodbye!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()