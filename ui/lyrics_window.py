import tkinter as tk
from tkinter import scrolledtext, ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import os
import sys

# Add parent directory to path to find modules in main directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spotify_client import SpotifyClient
from lyrics_fetcher import GeniusLyricsFetcher
from ui.styles import (
    BACKGROUND_COLOR, TEXT_COLOR, HIGHLIGHT_COLOR, FONT_FAMILY, FONT_SIZE,
    BUTTON_STYLE, PROGRESS_BAR_STYLE, BUTTON_FONT_SIZE, TITLE_FONT_SIZE,
    SECONDARY_COLOR
)
from ui.icon import get_icon
import time
import threading
from config import GENIUS_ACCESS_TOKEN

class LyricsWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Spotify Lyrics")
        self.root.configure(bg=BACKGROUND_COLOR)
        
        # Set window icon
        try:
            # Get the icon image
            icon_image = get_icon()
            # Convert to PhotoImage for Tkinter
            icon_photo = ImageTk.PhotoImage(icon_image)
            # Set as window icon
            self.root.iconphoto(True, icon_photo)
            # Save icon for taskbar
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.ico")
            icon_image.save(icon_path, format="ICO")
            # Set taskbar icon (Windows specific)
            if os.name == 'nt':  # Windows
                import ctypes
                myappid = 'mycompany.spotifylyrics.1.0'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                self.root.iconbitmap(icon_path)
            # Keep a reference to prevent garbage collection
            self.icon_photo = icon_photo
        except Exception as e:
            print(f"Error setting icon: {e}")
        
        # Set window properties
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.attributes("-topmost", True)  # Keep window on top
        
        try:
            self.root.attributes("-alpha", 0.85)  # Set transparency
        except Exception:
            print("Transparency not supported on this system")
        
        # Set window size and position
        self.window_width = 400
        self.window_height = 600
        self.set_window_position()
        
        # Create main container frame
        self.container = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        self.container.pack(fill='both', expand=True)
        
        # Create a frame for the title bar
        self.title_bar = tk.Frame(self.container, bg=BACKGROUND_COLOR, relief='flat', bd=2)
        self.title_bar.pack(fill='x')
        
        # Add title label
        self.title_label = tk.Label(self.title_bar, text="Spotify Lyrics", 
                                  bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                                  font=(FONT_FAMILY, TITLE_FONT_SIZE, "bold"))
        self.title_label.pack(side='left', padx=5)
        
        # Add window control buttons frame
        self.control_frame = tk.Frame(self.title_bar, bg=BACKGROUND_COLOR)
        self.control_frame.pack(side='right')
        
        # Add minimize button with updated style
        self.minimize_button = tk.Button(self.control_frame, text="−", **BUTTON_STYLE,
                                       font=(FONT_FAMILY, BUTTON_FONT_SIZE),
                                       command=self.minimize_window)
        self.minimize_button.pack(side='left', padx=2)
        
        # Add maximize/restore button
        self.maximize_button = tk.Button(self.control_frame, text="□", **BUTTON_STYLE,
                                       font=(FONT_FAMILY, BUTTON_FONT_SIZE),
                                       command=self.toggle_maximize)
        self.maximize_button.pack(side='left', padx=2)
        
        # Add close button with updated style
        self.close_button = tk.Button(self.control_frame, text="×", **BUTTON_STYLE,
                                    font=(FONT_FAMILY, BUTTON_FONT_SIZE),
                                    command=self.root.destroy)
        self.close_button.pack(side='left', padx=2)
        
        # Create resize grip
        self.resize_grip = ttk.Sizegrip(self.container)
        self.resize_grip.pack(side='right', anchor='se')
        
        # Create album art and info container with more compact layout
        self.info_container = tk.Frame(self.container, bg=BACKGROUND_COLOR)
        self.info_container.pack(fill='x', padx=5, pady=2)
        
        # Add album art label with smaller size
        self.album_art_label = tk.Label(self.info_container, bg=BACKGROUND_COLOR)
        self.album_art_label.pack(side='left', padx=(0, 5))
        
        # Create song info frame with more compact layout
        self.song_info_frame = tk.Frame(self.info_container, bg=BACKGROUND_COLOR)
        self.song_info_frame.pack(side='left', fill='x', expand=True)
        
        # Add song title and artist labels with smaller font
        self.song_title_label = tk.Label(self.song_info_frame, text="Not Playing", 
                                       bg=BACKGROUND_COLOR, fg=TEXT_COLOR, 
                                       font=(FONT_FAMILY, FONT_SIZE - 1, "bold"),
                                       wraplength=250,
                                       anchor='w',
                                       justify='left')
        self.song_title_label.pack(fill='x')
        
        self.artist_label = tk.Label(self.song_info_frame, text="", 
                                   bg=BACKGROUND_COLOR, fg=TEXT_COLOR, 
                                   font=(FONT_FAMILY, FONT_SIZE - 2),
                                   wraplength=250,
                                   anchor='w',
                                   justify='left')
        self.artist_label.pack(fill='x')
        
        # Create compact playback control frame
        self.playback_frame = tk.Frame(self.container, bg=BACKGROUND_COLOR)
        self.playback_frame.pack(fill='x', padx=5, pady=2)
        
        # Add playback controls with smaller buttons
        control_frame = tk.Frame(self.playback_frame, bg=BACKGROUND_COLOR)
        control_frame.pack(side='left', padx=2)
        
        self.prev_button = tk.Button(control_frame, text="⏮", **BUTTON_STYLE,
                                   font=(FONT_FAMILY, BUTTON_FONT_SIZE - 2),
                                   command=self.previous_track)
        self.prev_button.pack(side='left', padx=2)
        
        self.play_pause_button = tk.Button(control_frame, text="⏯", **BUTTON_STYLE,
                                         font=(FONT_FAMILY, BUTTON_FONT_SIZE - 2),
                                         command=self.toggle_playback)
        self.play_pause_button.pack(side='left', padx=2)
        
        self.next_button = tk.Button(control_frame, text="⏭", **BUTTON_STYLE,
                                   font=(FONT_FAMILY, BUTTON_FONT_SIZE - 2),
                                   command=self.next_track)
        self.next_button.pack(side='left', padx=2)
        
        # Progress bar and time in same frame
        progress_frame = tk.Frame(self.playback_frame, bg=BACKGROUND_COLOR)
        progress_frame.pack(fill='x', expand=True, padx=5)
        
        self.current_time_label = tk.Label(progress_frame, text="0:00", 
                                         bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                                         font=(FONT_FAMILY, FONT_SIZE - 3))
        self.current_time_label.pack(side='left')
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                          style="Custom.Horizontal.TProgressbar",
                                          variable=self.progress_var,
                                          mode='determinate')
        self.progress_bar.pack(side='left', fill='x', expand=True, padx=5)
        
        self.total_time_label = tk.Label(progress_frame, text="0:00", 
                                       bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                                       font=(FONT_FAMILY, FONT_SIZE - 3))
        self.total_time_label.pack(side='left')
        
        # Create lyrics display with synchronized lyrics support
        self.lyrics_container = ttk.Frame(self.container)
        self.lyrics_container.pack(fill='both', expand=True, padx=5, pady=2)
        
        # Initialize lyrics synchronization variables
        self.lyrics_lines = []
        self.line_positions = []  # Store the line positions for accurate highlighting
        self.current_line_index = 0
        self.sync_update_id = None
        
        # Create lyrics display with highlighting support
        self.lyrics_text = scrolledtext.ScrolledText(
            self.lyrics_container,
            wrap=tk.WORD,
            font=(FONT_FAMILY, FONT_SIZE + 4),  # Larger font size
            bg='#002649',  # Dark blue background
            fg='#FFFFFF',  # White text
            bd=0,
            padx=20,
            pady=20,
            spacing1=15,
            spacing2=0,
            spacing3=15,
            cursor=""  # Hide cursor
        )
        self.lyrics_text.pack(fill=tk.BOTH, expand=True)
        
        # Hide scrollbar but keep functionality
        scrollbar = self.lyrics_text.yview
        self.lyrics_text.configure(yscrollcommand=lambda *args: None)
        self.lyrics_text.yview = scrollbar
        
        # Configure tags for highlighting with glow effect
        self.lyrics_text.tag_configure(
            "current_line",
            background='#002649',  # Same as background
            foreground='#7CB7EB',  # Light blue for highlighted text
            font=(FONT_FAMILY, FONT_SIZE + 4, "bold")  # Bold for current line
        )
        
        # Configure additional tags for glow effect
        for i in range(10):
            alpha = (10 - i) / 10  # Create gradient effect
            color = self.interpolate_color('#7CB7EB', '#FFFFFF', alpha)
            self.lyrics_text.tag_configure(
                f"glow_{i}",
                foreground=color,
                font=(FONT_FAMILY, FONT_SIZE + 4, "bold")
            )
        
        # Initialize glow effect variables
        self.glow_step = 0
        self.glow_direction = 1  # 1 for increasing, -1 for decreasing
        self.glow_after_id = None
        
        # Initialize controllers (will be set later)
        self.spotify_controller = None
        self.lyrics_fetcher = None
        
        # Make the window draggable
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<ButtonRelease-1>", self.stop_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        
        # Bind double click on title bar to maximize/restore
        self.title_bar.bind("<Double-Button-1>", lambda e: self.toggle_maximize())
        
        # Store window state
        self.is_maximized = False
        self.normal_size = None
        
        # Bind window state events
        self.root.bind("<Map>", self.on_map)
        self.root.bind("<Configure>", self.on_configure)
        
        # Initialize variables
        self.current_track_id = None
        self.current_lyrics = None
        self.current_album_art = None
        self.is_playing = False
        self.current_progress_ms = 0
        self.total_duration_ms = 0
        
        # Store initial state
        self.minimized = False
        self.was_visible = True
        
        # Create system tray window (hidden)
        self.tray_window = tk.Toplevel(self.root)
        self.tray_window.withdraw()
        self.tray_window.title("Spotify Lyrics")
        
        # Start the update loop
        self.update_thread = None  # Will be started when spotify_controller is set
    
    def set_window_position(self):
        """Set the initial window position."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = screen_width - self.window_width - 20
        y_position = (screen_height - self.window_height) // 2
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x_position}+{y_position}")
    
    def minimize_window(self):
        """Minimize the window properly."""
        if not self.minimized:
            # Save current state
            self.was_visible = True
            self.minimized = True
            # Hide main window
            self.root.withdraw()
            # Show system tray window
            self.tray_window.deiconify()
            self.tray_window.protocol('WM_DELETE_WINDOW', self.restore_window)
            self.tray_window.state('iconic')
            # Bind the system tray window events
            self.tray_window.bind("<Map>", self.handle_tray_map)
    
    def handle_tray_map(self, event=None):
        """Handle system tray window map event."""
        if self.minimized and self.was_visible:
            self.restore_window()
    
    def restore_window(self, event=None):
        """Restore the window from minimized state."""
        if self.minimized:
            # Hide system tray window
            self.tray_window.withdraw()
            # Show main window
            self.root.deiconify()
            self.root.attributes("-topmost", True)
            # Update state
            self.minimized = False
            self.was_visible = True
            
    def restore_from_maximize(self):
        """Restore the window from maximized state."""
        if self.is_maximized:
            if self.normal_size:
                self.root.geometry(self.normal_size)
            else:
                self.set_window_position()
            self.maximize_button.configure(text="□")
            self.is_maximized = False
            
    def toggle_maximize(self):
        """Toggle between maximized and normal window state."""
        if self.is_maximized:
            self.restore_from_maximize()
        else:
            self.maximize_window()
    
    def maximize_window(self):
        """Maximize the window."""
        if not self.is_maximized:
            self.normal_size = self.root.geometry()
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")
            self.maximize_button.configure(text="❐")
            self.is_maximized = True
    
    def on_configure(self, event):
        """Handle window configure event (resize, move, etc.)."""
        if event.widget == self.root and not self.is_maximized:
            self.normal_size = self.root.geometry()
    
    def start_move(self, event):
        """Start window drag operation."""
        self.x = event.x
        self.y = event.y
        if self.is_maximized:
            # Calculate relative position for smooth transition
            self.restore_window()
            # Adjust the window position to follow the mouse
            width = self.root.winfo_width()
            self.x = width * (event.x / self.root.winfo_screenwidth())
    
    def stop_move(self, event):
        """Stop window drag operation."""
        self.x = None
        self.y = None
    
    def do_move(self, event):
        """Handle window drag operation."""
        if not self.is_maximized:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")
    
    def previous_track(self):
        if self.spotify_controller:
            self.spotify_controller.previous_track()
        
    def next_track(self):
        if self.spotify_controller:
            self.spotify_controller.next_track()
        
    def toggle_playback(self):
        if not self.spotify_controller:
            return
            
        if self.is_playing:
            self.spotify_controller.pause_playback()
        else:
            self.spotify_controller.start_playback()
        self.is_playing = not self.is_playing
        self.play_pause_button.config(text="⏸" if self.is_playing else "▶")
        
    def update_progress(self, progress_ms, duration_ms):
        self.current_progress_ms = progress_ms
        self.total_duration_ms = duration_ms
        
        # Update progress bar
        progress_percent = (progress_ms / duration_ms * 100) if duration_ms > 0 else 0
        self.progress_var.set(progress_percent)
        
        # Update time labels
        current_time = time.strftime('%M:%S', time.gmtime(progress_ms / 1000))
        total_time = time.strftime('%M:%S', time.gmtime(duration_ms / 1000))
        self.current_time_label.config(text=current_time)
        self.total_time_label.config(text=total_time)
        
    def update_album_art(self, track):
        if 'album' in track and 'images' in track['album'] and track['album']['images']:
            image_url = track['album']['images'][0]['url']
            try:
                response = requests.get(image_url)
                img_data = Image.open(BytesIO(response.content))
                img_data = img_data.resize((100, 100), Image.Resampling.LANCZOS)
                img_photo = ImageTk.PhotoImage(img_data)
                self.album_art_label.config(image=img_photo)
                self.current_album_art = img_photo  # Keep a reference to prevent garbage collection
            except Exception as e:
                print(f"Error loading album art: {e}")
                
    def update_loop(self):
        """Main update loop for the window."""
        last_update_time = 0
        update_interval = 0.1  # Update every 100ms for smooth progress
        fetch_interval = 1.0   # Fetch new data every 1 second
        
        while True:
            try:
                current_time = time.time()
                
                if not self.spotify_controller:
                    time.sleep(update_interval)
                    continue
                
                # Get playback state more frequently for smooth progress
                if current_time - last_update_time >= update_interval:
                    playback_state = self.spotify_controller.get_playback_state()
                    if playback_state:
                        self.is_playing = playback_state['is_playing']
                        self.play_pause_button.config(text="⏸" if self.is_playing else "▶")
                        
                        # Update progress and sync lyrics
                        if self.is_playing:
                            progress_ms = playback_state['progress_ms']
                            if hasattr(self, 'current_track') and self.current_track:
                                duration_ms = self.current_track['duration_ms']
                                self.update_progress(progress_ms, duration_ms)
                                self.update_lyrics_sync(progress_ms, duration_ms)
                
                # Check for track changes less frequently
                if current_time - last_update_time >= fetch_interval:
                    current_track = self.spotify_controller.get_current_track()
                    if current_track:
                        track_id = current_track.get('id')
                        if track_id != self.current_track_id:
                            self.current_track_id = track_id
                            self.current_track = current_track  # Store current track
                            self.update_song_info(current_track)
                            self.update_album_art(current_track)
                            self.update_lyrics()
                    last_update_time = current_time
                
                time.sleep(update_interval)
                
            except Exception as e:
                print(f"Error in update loop: {e}")
                time.sleep(update_interval)

    def update_song_info(self, track):
        """Update the song information display."""
        try:
            if not track:
                return
                
            # Update song title
            title = track.get('name', 'Unknown Title')
            self.song_title_label.config(text=title)
            
            # Update artist name
            artist = track.get('artists', [{'name': 'Unknown Artist'}])[0]['name']
            self.artist_label.config(text=artist)
            
        except Exception as e:
            print(f"Error updating song info: {e}")
            self.song_title_label.config(text="Error")
            self.artist_label.config(text="")
    
    def update_lyrics_sync(self, progress_ms, duration_ms):
        """Update the highlighted lyrics based on playback progress."""
        try:
            if not self.lyrics_lines or not duration_ms:
                return
            
            # Calculate the current position in the song
            position = progress_ms / duration_ms
            
            # Simple linear mapping of position to lyrics lines
            # This provides smoother highlighting without complex section detection
            current_line = int(position * len(self.lyrics_lines))
            current_line = max(0, min(current_line, len(self.lyrics_lines) - 1))
            
            # Update highlighting if needed
            if current_line != self.current_line_index:
                self.current_line_index = current_line
                self.root.after_idle(self.highlight_current_line)
                
        except Exception as e:
            print(f"Error in lyrics sync: {str(e)}")

    def highlight_current_line(self):
        """Highlight the current line in the lyrics display with glow effect."""
        try:
            if not self.lyrics_lines or not hasattr(self, 'line_positions'):
                return
                
            # Enable widget temporarily for updating
            self.lyrics_text.config(state='normal')
            
            # Remove all highlighting and glow tags
            self.lyrics_text.tag_remove("current_line", "1.0", tk.END)
            for i in range(10):
                self.lyrics_text.tag_remove(f"glow_{i}", "1.0", tk.END)
            
            if 0 <= self.current_line_index < len(self.lyrics_lines):
                # Get the actual line position
                line_num = self.line_positions[self.current_line_index]
                line_start = f"{line_num}.0"
                line_end = f"{line_num}.end"
                
                # Apply base highlighting
                self.lyrics_text.tag_add("current_line", line_start, line_end)
                
                # Start glow effect
                if not self.glow_after_id:
                    self.glow_step = 0
                    self.glow_direction = 1
                    self.update_glow_effect(line_start, line_end)
                
                # Calculate visible lines in the text widget
                visible_height = self.lyrics_text.winfo_height()
                dline_info = self.lyrics_text.dlineinfo(line_start)
                line_height = dline_info[3] if dline_info else 20
                visible_lines = visible_height // line_height
                
                # Calculate the line to center
                center_line = max(1, line_num - (visible_lines // 2))
                
                # Ensure the current line is centered
                self.lyrics_text.see(f"{center_line}.0")
                
                # Fine-tune the centering
                self.lyrics_text.update_idletasks()
                self.root.after(10, lambda: self.lyrics_text.yview_scroll(-2, "units"))
            
            # Make read-only again
            self.lyrics_text.config(state='disabled')
            
        except Exception as e:
            print(f"Error in highlight_current_line: {e}")
            self.lyrics_text.config(state='disabled')

    def update_glow_effect(self, line_start, line_end):
        """Update the glow effect animation."""
        try:
            # Cancel any existing glow update
            if self.glow_after_id:
                self.root.after_cancel(self.glow_after_id)
                self.glow_after_id = None
            
            # Enable widget for updating
            self.lyrics_text.config(state='normal')
            
            # Remove previous glow
            for i in range(10):
                self.lyrics_text.tag_remove(f"glow_{i}", line_start, line_end)
            
            # Apply current glow
            self.lyrics_text.tag_add(f"glow_{self.glow_step}", line_start, line_end)
            
            # Update glow step
            if self.glow_direction == 1:
                self.glow_step += 1
                if self.glow_step >= 9:
                    self.glow_direction = -1
            else:
                self.glow_step -= 1
                if self.glow_step <= 0:
                    self.glow_direction = 1
            
            # Make read-only
            self.lyrics_text.config(state='disabled')
            
            # Schedule next update
            self.glow_after_id = self.root.after(50, lambda: self.update_glow_effect(line_start, line_end))
            
        except Exception as e:
            print(f"Error in update_glow_effect: {e}")
            self.lyrics_text.config(state='disabled')

    def update_lyrics(self):
        """Update lyrics based on current track."""
        try:
            if not self.spotify_controller or not self.lyrics_fetcher:
                print("Spotify controller or lyrics fetcher not initialized")
                return

            current_track = self.spotify_controller.get_current_track()
            if not current_track:
                print("No current track information")
                self.display_lyrics("No track playing...")
                return

            # Extract track info
            try:
                artist = current_track['artists'][0]['name']
                title = current_track['name']
                print(f"\nUpdating lyrics for: {artist} - {title}")
            except (KeyError, TypeError, IndexError) as e:
                print(f"Error extracting track info: {e}")
                self.display_lyrics("Error getting track information")
                return

            # Always fetch new lyrics when update_lyrics is called
            print("Fetching lyrics...")
            lyrics = self.lyrics_fetcher.fetch_lyrics(artist, title)
            
            if not lyrics:
                print("No lyrics found")
                self.display_lyrics("No lyrics found for this song.")
                return

            print(f"Lyrics found, displaying...")
            self.current_song = (artist, title)
            self.display_lyrics(lyrics)

        except Exception as e:
            print(f"Error in update_lyrics: {e}")
            import traceback
            traceback.print_exc()
            self.display_lyrics("Error updating lyrics")

    def display_lyrics(self, lyrics):
        """Display lyrics in the text widget."""
        try:
            # Enable widget for updating
            self.lyrics_text.config(state='normal')
            
            # Clear existing lyrics
            self.lyrics_text.delete(1.0, tk.END)
            
            # Reset lyrics lines and line positions
            self.lyrics_lines = []
            self.line_positions = []  # Store the line positions for accurate highlighting
            self.current_line_index = 0
            
            # Configure base text widget style
            self.lyrics_text.configure(
                bg='#002649',  # Dark blue background like Spotify
                fg='#FFFFFF',  # White text for non-highlighted lines
                font=(FONT_FAMILY, FONT_SIZE + 4),  # Larger base font
                spacing1=15,   # Space before each line
                spacing2=0,    # Space within paragraph
                spacing3=15,   # Space after each line
                padx=20,      # Horizontal padding
                pady=20       # Vertical padding
            )
            
            current_position = 1  # Track the current line position
            
            if isinstance(lyrics, str):
                # Split string lyrics into sentences and clean them
                sentences = [s.strip() for s in lyrics.split('\n') if s.strip()]
                # Remove common formatting markers
                sentences = [s for s in sentences if not any(marker in s.lower() 
                    for marker in ['[verse', '[chorus', '[bridge', '[intro', '[outro'])]
                
                # Add each sentence with spacing and store its position
                for sentence in sentences:
                    if sentence:
                        self.lyrics_lines.append(sentence)
                        self.lyrics_text.insert(tk.END, sentence + '\n\n')
                        self.line_positions.append(current_position)
                        current_position += 2  # Account for the extra newline
                    
            elif isinstance(lyrics, list):
                # Process list of lyrics
                for line in lyrics:
                    text = None
                    if isinstance(line, dict) and 'text' in line:
                        text = line['text'].strip()
                    elif isinstance(line, str):
                        text = line.strip()
                    
                    if text and not any(marker in text.lower() 
                        for marker in ['[verse', '[chorus', '[bridge', '[intro', '[outro']):
                        self.lyrics_lines.append(text)
                        self.lyrics_text.insert(tk.END, text + '\n\n')
                        self.line_positions.append(current_position)
                        current_position += 2  # Account for the extra newline
            
            # Configure highlighting style
            self.lyrics_text.tag_configure(
                "current_line",
                background='#002649',  # Same as background for seamless look
                foreground='#7CB7EB',  # Light blue for highlighted text
                font=(FONT_FAMILY, FONT_SIZE + 4, "bold"),  # Bold for current line
                spacing1=15,
                spacing3=15
            )
            
            # Make read-only
            self.lyrics_text.config(state='disabled')
            
            # Scroll to top
            self.lyrics_text.see("1.0")
            
        except Exception as e:
            print(f"Error displaying lyrics: {e}")
            import traceback
            traceback.print_exc()
            self.lyrics_text.delete(1.0, tk.END)
            self.lyrics_text.insert(tk.END, "Error displaying lyrics")

    def on_restore(self, event=None):
        """Handle window restore event."""
        if event and str(event.widget) == str(self.root):
            self.root.attributes("-topmost", True)
            if self.is_maximized:
                self.maximize_window()
            else:
                self.restore_from_maximize()
            
    def on_map(self, event):
        """Handle window map event."""
        if str(event.widget) == str(self.root):
            self.root.attributes("-topmost", True)
            if self.is_maximized:
                self.maximize_window()
            else:
                self.restore_from_maximize()

    def update_current_song(self, song_info):
        """Update the current song information and fetch lyrics."""
        if not song_info:
            self.clear_lyrics()
            return
        
        artist = song_info.get('artist', '')
        title = song_info.get('title', '')
        
        # Update song info display
        self.update_song_info(song_info)
        
        # Fetch and display lyrics
        if self.lyrics_fetcher:
            lyrics = self.lyrics_fetcher.fetch_lyrics(artist, title)
            self.display_lyrics(lyrics)
        else:
            self.display_lyrics("Lyrics fetcher not initialized")

    def clear_lyrics(self):
        """Clear the lyrics display and reset synchronization."""
        # Cancel any existing glow effect
        if self.glow_after_id:
            self.root.after_cancel(self.glow_after_id)
            self.glow_after_id = None
            
        self.lyrics_text.config(state=tk.NORMAL)
        self.lyrics_text.delete("1.0", tk.END)
        self.lyrics_text.config(state=tk.DISABLED)
        self.lyrics_lines = []
        self.current_line_index = 0
        if self.sync_update_id:
            self.root.after_cancel(self.sync_update_id)
            self.sync_update_id = None

    def on_close(self):
        """Clean up when window is closed."""
        if self.sync_update_id:
            self.root.after_cancel(self.sync_update_id)
        # ... existing code ...

    def set_spotify_controller(self, controller):
        """Set the Spotify controller and bind callbacks."""
        self.spotify_controller = controller
        if self.spotify_controller:
            self.spotify_controller.bind_progress_callback(self.update_lyrics_sync)
            # Start the update loop now that we have the controller
            if not self.update_thread:
                self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
                self.update_thread.start()
    
    def set_lyrics_fetcher(self, fetcher):
        """Set the lyrics fetcher."""
        self.lyrics_fetcher = fetcher

    def interpolate_color(self, color1, color2, factor):
        """Interpolate between two colors."""
        # Convert hex to RGB
        r1 = int(color1[1:3], 16)
        g1 = int(color1[3:5], 16)
        b1 = int(color1[5:7], 16)
        r2 = int(color2[1:3], 16)
        g2 = int(color2[3:5], 16)
        b2 = int(color2[5:7], 16)
        
        # Interpolate
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'
