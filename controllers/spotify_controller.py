import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import os

class SpotifyController:
    def __init__(self, client_id, client_secret, redirect_uri, root=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.root = root
        self.sp = None
        self.current_playback = None
        self.token_info = None
        self.progress_callbacks = []
        self.update_progress_id = None
        
        # Create cache directory if it doesn't exist
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.spotify_cache')
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        # Set cache path
        self.cache_path = os.path.join(cache_dir, '.spotify_cache')
        
        # Initialize Spotify client
        self.initialize_spotify()
        
        if root:
            self.start_progress_updates()
    
    def initialize_spotify(self):
        """Initialize the Spotify client with proper authentication."""
        try:
            print("Initializing Spotify client...")
            scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing"
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=scope,
                cache_path=self.cache_path,
                open_browser=False  # Don't open browser automatically
            )
            
            print("Getting access token...")
            # Try to get cached token first
            token_info = auth_manager.get_cached_token()
            
            if not token_info:
                print("\n=== Spotify Authorization Steps ===")
                print("1. Copy and paste this URL into your browser:")
                auth_url = auth_manager.get_authorize_url()
                print(auth_url)
                print("\n2. Log in to Spotify and click 'Agree' to authorize the app")
                print("3. After clicking Agree, you'll be redirected to a URL that starts with 'http://localhost:8888/?code='")
                print("4. Copy the ENTIRE redirected URL (even if the page doesn't load)")
                print("\nPaste the redirected URL here (the one starting with http://localhost:8888/?code=):")
                
                while True:
                    try:
                        response_url = input("Enter the redirected URL: ").strip()
                        if "code=" not in response_url:
                            print("\nError: This looks like the wrong URL.")
                            print("Please paste the URL you were redirected to (it should contain 'code=')")
                            continue
                        
                        # Get the token using the response URL
                        code = auth_manager.parse_response_code(response_url)
                        token_info = auth_manager.get_access_token(code, as_dict=True)
                        break
                    except Exception as e:
                        print(f"\nError: {str(e)}")
                        print("Please try again with the correct redirected URL")
            
            if token_info:
                print("\nSuccessfully got token info!")
                self.token_info = token_info
                print("Creating Spotify client...")
                self.sp = spotipy.Spotify(auth_manager=auth_manager)
                print("Successfully authenticated with Spotify!")
                
                # Test the connection
                self.test_connection()
            else:
                print("\nFailed to get token info. Please check your Spotify credentials.")
                print("Make sure you complete the authentication process correctly.")
            
        except Exception as e:
            print(f"\nError initializing Spotify client: {e}")
            import traceback
            traceback.print_exc()
    
    def test_connection(self):
        """Test the Spotify connection by trying to get the current playback."""
        try:
            if self.is_authenticated() and self.sp is not None:
                print("Testing Spotify connection...")
                playback = self.sp.current_playback()
                if playback:
                    print("Successfully connected to Spotify!")
                    print(f"Current playback state: {'Playing' if playback.get('is_playing') else 'Paused'}")
                else:
                    print("No active playback found. Please start playing something on Spotify.")
            else:
                print("Not authenticated with Spotify")
        except Exception as e:
            print(f"Error testing Spotify connection: {e}")
            import traceback
            traceback.print_exc()
    
    def is_authenticated(self):
        """Check if the client is authenticated."""
        try:
            return self.sp is not None and self.token_info is not None
        except Exception as e:
            print(f"Error checking authentication: {e}")
            return False
    
    def get_current_track(self):
        """Get the currently playing track."""
        try:
            if self.is_authenticated() and self.sp is not None:
                playback = self.sp.current_playback()
                if playback and playback.get('item'):
                    self.current_playback = playback
                    return playback['item']
                else:
                    print("No track currently playing")
            else:
                print("Not authenticated with Spotify")
        except Exception as e:
            print(f"Error getting current track: {e}")
        return None
    
    def get_playback_state(self):
        """Get the current playback state."""
        try:
            if self.is_authenticated() and self.sp is not None:
                return self.sp.current_playback()
        except Exception as e:
            print(f"Error getting playback state: {e}")
        return None
    
    def start_playback(self):
        """Start or resume playback."""
        try:
            if self.is_authenticated() and self.sp is not None:
                self.sp.start_playback()
        except Exception as e:
            print(f"Error starting playback: {e}")
    
    def pause_playback(self):
        """Pause playback."""
        try:
            if self.is_authenticated() and self.sp is not None:
                self.sp.pause_playback()
        except Exception as e:
            print(f"Error pausing playback: {e}")
    
    def next_track(self):
        """Skip to next track."""
        try:
            if self.is_authenticated() and self.sp is not None:
                self.sp.next_track()
        except Exception as e:
            print(f"Error skipping to next track: {e}")
    
    def previous_track(self):
        """Skip to previous track."""
        try:
            if self.is_authenticated() and self.sp is not None:
                self.sp.previous_track()
        except Exception as e:
            print(f"Error skipping to previous track: {e}")
    
    def bind_progress_callback(self, callback):
        """Bind a callback function to receive playback progress updates."""
        if callback not in self.progress_callbacks:
            self.progress_callbacks.append(callback)
    
    def unbind_progress_callback(self, callback):
        """Unbind a progress callback function."""
        if callback in self.progress_callbacks:
            self.progress_callbacks.remove(callback)
    
    def start_progress_updates(self):
        """Start periodic progress updates."""
        self.update_progress()
    
    def update_progress(self):
        """Update playback progress and notify callbacks."""
        try:
            if self.is_authenticated() and self.sp is not None:
                playback = self.sp.current_playback()
                if playback and playback.get('is_playing'):
                    progress_ms = playback.get('progress_ms', 0)
                    duration_ms = playback.get('item', {}).get('duration_ms', 0)
                    
                    # Notify all callbacks
                    for callback in self.progress_callbacks:
                        try:
                            callback(progress_ms, duration_ms)
                        except Exception as e:
                            print(f"Error in progress callback: {e}")
        except Exception as e:
            print(f"Error updating progress: {e}")
        finally:
            # Schedule next update if root exists
            # IMPROVED: Update every 250ms instead of 1000ms for smoother highlighting
            if self.root:
                self.update_progress_id = self.root.after(250, self.update_progress)
    
    def calculate_line_timing(self, lyrics_lines, duration_ms):
        """
        Distribute lyrics across song duration
        Returns list of (line_text, start_time_ms, end_time_ms)
        
        Args:
            lyrics_lines: List of lyric line strings
            duration_ms: Total song duration in milliseconds
            
        Returns:
            List of tuples (line_text, start_ms, end_ms)
        """
        if not lyrics_lines or duration_ms <= 0:
            return []
        
        timed_lines = []
        num_lines = len(lyrics_lines)
        
        # Simple even distribution
        time_per_line = duration_ms / num_lines
        
        for i, line in enumerate(lyrics_lines):
            start_ms = int(i * time_per_line)
            end_ms = int((i + 1) * time_per_line)
            timed_lines.append((line, start_ms, end_ms))
        
        return timed_lines
    
    def get_current_line_index(self, progress_ms, timed_lines):
        """
        Get the index of currently playing lyric line
        
        Args:
            progress_ms: Current playback progress in milliseconds
            timed_lines: List of (line_text, start_ms, end_ms) tuples
            
        Returns:
            Index of current line, or -1 if not found
        """
        for i, (line, start_ms, end_ms) in enumerate(timed_lines):
            if start_ms <= progress_ms < end_ms:
                return i
        
        # Return last line if we're past the end
        if progress_ms >= timed_lines[-1][2] if timed_lines else 0:
            return len(timed_lines) - 1
        
        return 0
    
    def stop_progress_updates(self):
        """Stop progress updates."""
        if self.update_progress_id and self.root:
            self.root.after_cancel(self.update_progress_id)
            self.update_progress_id = None
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_progress_updates()
        self.progress_callbacks.clear()
        self.sp = None
        self.token_info = None 