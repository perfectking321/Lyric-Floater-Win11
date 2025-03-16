import tkinter as tk
from tkinter import scrolledtext
import os
import sys
import threading
import time

# Add parent directory to path to find modules in main directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spotify_client import SpotifyClient
from lyrics_fetcher import GeniusLyricsFetcher
from lyricstify_fetcher import LyricstifyFetcher
from ui.styles import BACKGROUND_COLOR, TEXT_COLOR, HIGHLIGHT_COLOR, FONT_FAMILY, FONT_SIZE
from config import GENIUS_ACCESS_TOKEN

class LyricsWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Spotify Lyrics")
        self.root.configure(bg=BACKGROUND_COLOR)
        
        # Set window properties
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.attributes("-topmost", True)  # Keep window on top
        self.root.attributes("-alpha", 0.85)  # Set transparency
        
        # Set window size and position
        window_width = 400
        window_height = 500
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = screen_width - window_width - 20
        y_position = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Initialize variables
        self.current_track_id = None
        self.current_lyrics = None
        
        # Create a frame for the title bar
        self.title_bar = tk.Frame(self.root, bg=BACKGROUND_COLOR, relief='flat', bd=2)
        self.title_bar.pack(fill='x')

        # Make the window draggable
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<ButtonRelease-1>", self.stop_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)

        
        # Add title label
        self.title_label = tk.Label(self.title_bar, text="Spotify Lyrics", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        self.title_label.pack(side='left', padx=5)
        
        # Add close button
        self.close_button = tk.Button(self.title_bar, text="X", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, 
                                     relief='flat', command=self.root.destroy)
        self.close_button.pack(side='right')
        
        # Add minimize button
        self.minimize_button = tk.Button(self.title_bar, text="_", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, 
                                        relief='flat', command=self.minimize)
        self.minimize_button.pack(side='right')
        
        # Add refresh button
        self.refresh_button = tk.Button(self.title_bar, text="⟳", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, 
                                       relief='flat', command=self.refresh_lyrics)
        self.refresh_button.pack(side='right')
        
        # Add settings button
        self.settings_button = tk.Button(self.title_bar, text="⚙", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, 
                                        relief='flat', command=self.open_settings)
        self.settings_button.pack(side='right')
        
        # Create song info frame
        self.song_info_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        self.song_info_frame.pack(fill='x', padx=10, pady=5)
        
        # Add song title and artist labels
        self.song_title_label = tk.Label(self.song_info_frame, text="Not Playing", 
                                        bg=BACKGROUND_COLOR, fg=TEXT_COLOR, 
                                        font=(FONT_FAMILY, FONT_SIZE, "bold"),
                                        wraplength=380)
        self.song_title_label.pack(anchor='w')
        
        self.artist_label = tk.Label(self.song_info_frame, text="", 
                                    bg=BACKGROUND_COLOR, fg=TEXT_COLOR, 
                                    font=(FONT_FAMILY, FONT_SIZE - 2))
        self.artist_label.pack(anchor='w')
        
        # Create search frame
        self.search_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        self.search_frame.pack(fill='x', padx=10, pady=5)

        # Add search entry
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_var, 
                                    bg="#333333", fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.search_entry.pack(side='left', fill='x', expand=True)

        # Add search button
        self.search_button = tk.Button(self.search_frame, text="Search", bg=BACKGROUND_COLOR, 
                                      fg=TEXT_COLOR, command=self.search_lyrics)
        self.search_button.pack(side='right', padx=5)

        # Bind Enter key to search
        self.search_entry.bind("<Return>", lambda event: self.search_lyrics())
        
        # Create lyrics display using ScrolledText
        self.lyrics_display = scrolledtext.ScrolledText(self.root, 
                                                      wrap=tk.WORD,
                                                      bg=BACKGROUND_COLOR, 
                                                      fg=TEXT_COLOR,
                                                      font=(FONT_FAMILY, FONT_SIZE),
                                                      relief='flat',
                                                      padx=10,
                                                      pady=10,
                                                      selectbackground=HIGHLIGHT_COLOR,
                                                      selectforeground=TEXT_COLOR)
        self.lyrics_display.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Initialize Spotify client and lyrics fetchers
        self.spotify_client = SpotifyClient()
        self.genius_fetcher = GeniusLyricsFetcher(api_token=GENIUS_ACCESS_TOKEN)
        
        # Define lyricstify path - adjust this path to where your lyricstify files are located
        lyricstify_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lyricstify')
        self.lyricstify_fetcher = LyricstifyFetcher(lyricstify_path=lyricstify_path)
        
        # Create system tray icon
        self.setup_system_tray()
        
        # Start the update loop
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
    
    def setup_system_tray(self):
        try:
            from system_tray import SystemTray
            self.system_tray = SystemTray(
                self.root, 
                show_callback=self.show_window,
                exit_callback=self.exit_app
            )
            print("System tray initialized")
        except ImportError:
            print("Could not import SystemTray. System tray icon will not be available.")



    
    def show_window(self):
        self.root.deiconify()
        self.root.attributes("-topmost", True)
    
    def exit_app(self):
        self.root.quit()
    
    def open_settings(self):
        from ui.settings_window import SettingsWindow
        SettingsWindow(self.root, self.apply_settings)
    
    def apply_settings(self, settings):
        # Apply appearance settings
        bg_color = settings.get("background_color", BACKGROUND_COLOR)
        text_color = settings.get("text_color", TEXT_COLOR)
        font_family = settings.get("font_family", FONT_FAMILY)
        font_size = settings.get("font_size", FONT_SIZE)
        opacity = settings.get("opacity", 0.85)
        
        # Update window and widgets
        self.root.configure(bg=bg_color)
        self.root.attributes("-alpha", opacity)
        
        # Update title bar
        self.title_bar.configure(bg=bg_color)
        self.title_label.configure(bg=bg_color, fg=text_color)
        self.close_button.configure(bg=bg_color, fg=text_color)
        self.minimize_button.configure(bg=bg_color, fg=text_color)
        self.refresh_button.configure(bg=bg_color, fg=text_color)
        self.settings_button.configure(bg=bg_color, fg=text_color)
        
        # Update song info
        self.song_info_frame.configure(bg=bg_color)
        self.song_title_label.configure(bg=bg_color, fg=text_color, font=(font_family, font_size, "bold"))
        self.artist_label.configure(bg=bg_color, fg=text_color, font=(font_family, font_size - 2))
        
        # Update search frame
        self.search_frame.configure(bg=bg_color)
        self.search_button.configure(bg=bg_color, fg=text_color)
        
        # Update lyrics display
        self.lyrics_display.configure(bg=bg_color, fg=text_color, font=(font_family, font_size))
        
        # Restart Spotify client with new credentials
        self.spotify_client = SpotifyClient()
    
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    
    def stop_move(self, event):
        self.x = None
        self.y = None
    
    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
    
    def minimize(self):
        self.root.withdraw()  # Hide the window instead of minimizing
        # No need to set visibility with infi.systray as it handles this automatically
        # Remove or comment out: self.system_tray.icon.visible = True



    def deiconify(self, event):
        self.root.overrideredirect(True)  # Remove window decorations again
        self.root.attributes("-topmost", True)  # Keep window on top

    
    # Make sure to modify the refresh_lyrics method to not block the main thread
    def refresh_lyrics(self):
        """Force refresh the lyrics for the current track"""
        try:
            self.display_lyrics("Refreshing lyrics...")
            # Use after to schedule the refresh without blocking
            self.root.after(100, self._do_refresh_lyrics)
        except Exception as e:
            print(f"Error refreshing lyrics: {e}")
            self.display_lyrics("Error refreshing lyrics.")

    def _do_refresh_lyrics(self):
        try:
            current_track = self.spotify_client.get_current_track()
            if current_track:
                self.update_song_info(current_track)
                # Skip cache by passing force_refresh=True
                self.update_lyrics(current_track, force_refresh=True)
            else:
                self.display_lyrics("No track currently playing.")
        except Exception as e:
            print(f"Error in refresh: {e}")
            self.display_lyrics(f"Error: {str(e)}")

    
    def search_lyrics(self):
        """Search for lyrics based on user input"""
        search_text = self.search_var.get().strip()
        if not search_text:
            return
        
        # Display searching message
        self.display_lyrics(f"Searching for '{search_text}'...")
        
        try:
            # Try to parse artist - title format
            if " - " in search_text:
                artist, title = search_text.split(" - ", 1)
            else:
                # Assume it's just a title
                artist = ""
                title = search_text
            
            # Try to fetch lyrics
            lyrics = None
            if artist:
                lyrics = self.genius_fetcher.fetch_lyrics_from_genius(artist, title)
            else:
                # If no artist provided, search just by title
                lyrics = self.genius_fetcher.fetch_lyrics_from_genius("", title)
            
            # If we got lyrics, display them
            if lyrics:
                self.display_lyrics(lyrics)
                # Update the song info labels
                if artist:
                    self.song_title_label.config(text=title)
                    self.artist_label.config(text=artist)
                else:
                    self.song_title_label.config(text=title)
                    self.artist_label.config(text="Unknown Artist")
            else:
                self.display_lyrics(f"No lyrics found for '{search_text}'.\nTry using 'Artist - Title' format.")
        except Exception as e:
            print(f"Error searching lyrics: {e}")
            self.display_lyrics(f"Error searching for lyrics: {str(e)}")
    
    def update_loop(self):
        while True:
            try:
                current_track = self.spotify_client.get_current_track()
                
                if current_track and current_track['id'] != self.current_track_id:
                    self.current_track_id = current_track['id']
                    self.update_song_info(current_track)
                    self.update_lyrics(current_track)
            except Exception as e:
                print(f"Error in update loop: {e}")
            
            time.sleep(1)
    
    def update_song_info(self, track):
        title = track['name']
        artist = track['artists'][0]['name']
        
        # Update UI elements in the main thread
        self.root.after(0, lambda: self.song_title_label.config(text=title))
        self.root.after(0, lambda: self.artist_label.config(text=artist))
    
    def update_lyrics(self, track, force_refresh=False):
        title = track['name']
        artist = track['artists'][0]['name']
        
        # Try to get lyrics from cache first (unless force refresh)
        if not force_refresh:
            cached_lyrics = self.genius_fetcher.get_lyrics_from_cache(artist, title)
            if cached_lyrics:
                self.display_lyrics(cached_lyrics)
                return
        
        # Try to fetch lyrics from Genius
        lyrics = self.genius_fetcher.fetch_lyrics_from_genius(artist, title)
        
        # If Genius fails, try Lyricstify
        if not lyrics:
            lyrics = self.lyricstify_fetcher.fetch_lyrics(artist, title)
        
        # If we got lyrics, cache them and display
        if lyrics:
            self.genius_fetcher.save_lyrics_to_cache(artist, title, lyrics)
            self.display_lyrics(lyrics)
        else:
            self.display_lyrics("Lyrics not found.")
    
    def display_lyrics(self, lyrics):
        # Update UI in the main thread
        self.root.after(0, lambda: self._update_lyrics_display(lyrics))
    
    def _update_lyrics_display(self, lyrics):
        # Clear the current lyrics
        self.lyrics_display.config(state=tk.NORMAL)
        self.lyrics_display.delete(1.0, tk.END)
        
        # Insert the new lyrics
        self.lyrics_display.insert(tk.END, lyrics)
        
        # Disable editing
        self.lyrics_display.config(state=tk.DISABLED)
        
        # Scroll to the top
        self.lyrics_display.yview_moveto(0)
