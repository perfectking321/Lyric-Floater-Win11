"""
Modern Apple Music-inspired lyrics window with smooth animations
"""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.styles import *
from ui.icon import get_icon
from utils.animations import AnimationEngine, interpolate_color, calculate_opacity_for_line
from utils.image_processing import create_circular_image, download_image, create_placeholder_image


class ModernLyricsWindow:
    """Modern Apple Music-inspired lyrics display window"""
    
    def __init__(self, root):
        self.root = root
        self.spotify_controller = None
        self.lyrics_fetcher = None
        
        # Animation system
        self.animation_engine = AnimationEngine(root)
        
        # Lyrics data
        self.lyric_lines = []  # List of dicts: {text, canvas_id, y_pos, index, opacity}
        self.timed_lyrics = []  # List of tuples: (line_text, start_ms, end_ms)
        self.current_line_index = -1
        self.current_song_id = None
        
        # Image references
        self.album_art_image = None
        
        # Scroll state
        self.scroll_offset = 0
        self.target_scroll_offset = 0
        self.total_lyrics_height = 0
        self.is_scrolling = False
        
        # Playback state
        self.is_playing = False
        self.current_progress_ms = 0
        self.current_duration_ms = 0
        
        # Window state
        self.window_opacity = BACKGROUND_OPACITY
        self.is_maximized = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Setup window
        self._setup_window()
        self._create_main_container()
        self._create_header()
        self._create_lyrics_display()
        self._create_controls()
        self._bind_events()
        
        # Start update loop
        self._start_update_loop()
    
    def _setup_window(self):
        """Configure main window with Apple Music aesthetics"""
        self.root.title("Lyrics Floater")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        # Set window attributes
        try:
            self.root.attributes('-alpha', self.window_opacity)
        except:
            print("Transparency not supported")
        
        self.root.attributes('-topmost', True)
        self.root.configure(bg=BACKGROUND_COLOR)
        
        # Center window on screen
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        
        # Set icon
        try:
            icon_image = get_icon()
            icon_photo = ImageTk.PhotoImage(icon_image)
            self.root.iconphoto(True, icon_photo)
            self.icon_photo = icon_photo
        except Exception as e:
            print(f"Error setting icon: {e}")
    
    def _create_main_container(self):
        """Create main container frame"""
        self.main_container = tk.Frame(
            self.root,
            bg=BACKGROUND_COLOR
        )
        self.main_container.pack(fill='both', expand=True)
    
    def _create_header(self):
        """Create compact modern header with album art and info"""
        # Header frame with fixed height
        self.header_frame = tk.Frame(
            self.main_container,
            bg=SECONDARY_COLOR,
            height=HEADER_HEIGHT
        )
        self.header_frame.pack(fill='x', padx=0, pady=0)
        self.header_frame.pack_propagate(False)
        
        # Album art (left side) - circular 80x80
        self.album_art_label = tk.Label(
            self.header_frame,
            bg=SECONDARY_COLOR,
            width=80,
            height=80
        )
        self.album_art_label.place(x=20, y=20)
        
        # Load default placeholder
        self._set_placeholder_album_art()
        
        # Song info container (middle)
        info_frame = tk.Frame(self.header_frame, bg=SECONDARY_COLOR)
        info_frame.place(x=115, y=20, width=320, height=80)
        
        # Song Title
        self.title_label = tk.Label(
            info_frame,
            text="Not Playing",
            font=(FONT_FAMILY, FONT_SIZE_TITLE, "bold"),
            fg=TEXT_ACTIVE,
            bg=SECONDARY_COLOR,
            anchor='w',
            justify='left'
        )
        self.title_label.pack(fill='x', pady=(5, 2))
        
        # Artist Name
        self.artist_label = tk.Label(
            info_frame,
            text="",
            font=(FONT_FAMILY, FONT_SIZE_INFO),
            fg=TEXT_SECONDARY,
            bg=SECONDARY_COLOR,
            anchor='w',
            justify='left'
        )
        self.artist_label.pack(fill='x', pady=(0, 2))
        
        # Album Name
        self.album_label = tk.Label(
            info_frame,
            text="",
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            fg=TEXT_SECONDARY,
            bg=SECONDARY_COLOR,
            anchor='w',
            justify='left'
        )
        self.album_label.pack(fill='x')
        
        # Transparency button (top-right)
        self.transparency_btn = tk.Button(
            self.header_frame,
            text="◐",
            font=(FONT_FAMILY, 20),
            fg=TEXT_SECONDARY,
            bg=SECONDARY_COLOR,
            relief='flat',
            bd=0,
            cursor='hand2',
            activebackground=BUTTON_HOVER_COLOR,
            activeforeground=TEXT_ACTIVE,
            command=self.show_transparency_popup
        )
        self.transparency_btn.place(x=445, y=20, width=35, height=35)
        
        # Window control buttons (close, minimize)
        close_btn = tk.Button(
            self.header_frame,
            text="×",
            font=(FONT_FAMILY, 18),
            fg=TEXT_SECONDARY,
            bg=SECONDARY_COLOR,
            relief='flat',
            bd=0,
            cursor='hand2',
            activebackground="#FF0000",
            activeforeground=TEXT_ACTIVE,
            command=self.on_close
        )
        close_btn.place(x=445, y=60, width=35, height=35)
        
        minimize_btn = tk.Button(
            self.header_frame,
            text="−",
            font=(FONT_FAMILY, 18),
            fg=TEXT_SECONDARY,
            bg=SECONDARY_COLOR,
            relief='flat',
            bd=0,
            cursor='hand2',
            activebackground=BUTTON_HOVER_COLOR,
            activeforeground=TEXT_ACTIVE,
            command=self.minimize_window
        )
        minimize_btn.place(x=410, y=60, width=35, height=35)
    
    def _create_lyrics_display(self):
        """Create canvas-based lyrics display for smooth animations"""
        # Container frame for lyrics
        self.lyrics_container = tk.Frame(
            self.main_container,
            bg=BACKGROUND_COLOR
        )
        self.lyrics_container.pack(fill='both', expand=True, pady=(0, 0))
        
        # Canvas for lyrics with scrollbar
        self.lyrics_canvas = tk.Canvas(
            self.lyrics_container,
            bg=BACKGROUND_COLOR,
            highlightthickness=0,
            bd=0
        )
        self.lyrics_canvas.pack(fill='both', expand=True, padx=LYRICS_PADDING)
        
        # Bind mouse wheel for scrolling
        self.lyrics_canvas.bind('<MouseWheel>', self._on_mouse_wheel)
        
        # Show loading message
        self._show_loading_message()
    
    def _create_controls(self):
        """Create floating control bar at bottom"""
        # Control bar frame with fixed height
        self.control_frame = tk.Frame(
            self.main_container,
            bg=SECONDARY_COLOR,
            height=CONTROL_HEIGHT
        )
        self.control_frame.pack(fill='x', side='bottom')
        self.control_frame.pack_propagate(False)
        
        # Progress bar container
        progress_container = tk.Frame(self.control_frame, bg=SECONDARY_COLOR)
        progress_container.pack(fill='x', padx=20, pady=(15, 5))
        
        # Create custom progress bar (using Canvas for smooth rendering)
        self.progress_canvas = tk.Canvas(
            progress_container,
            bg=SECONDARY_COLOR,
            height=6,
            highlightthickness=0,
            bd=0
        )
        self.progress_canvas.pack(fill='x', pady=5)
        
        # Draw progress bar background
        self.progress_bg_rect = self.progress_canvas.create_rectangle(
            0, 1, 460, 5,
            fill=PROGRESS_BG,
            outline=''
        )
        
        # Draw progress bar foreground
        self.progress_fg_rect = self.progress_canvas.create_rectangle(
            0, 1, 0, 5,
            fill=PROGRESS_COLOR,
            outline=''
        )
        
        # Bind progress bar click for seeking
        self.progress_canvas.bind('<Button-1>', self._on_progress_click)
        
        # Timestamps frame
        timestamp_frame = tk.Frame(self.control_frame, bg=SECONDARY_COLOR)
        timestamp_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # Current time
        self.current_time_label = tk.Label(
            timestamp_frame,
            text="0:00",
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            fg=TEXT_SECONDARY,
            bg=SECONDARY_COLOR
        )
        self.current_time_label.pack(side='left')
        
        # Total time
        self.total_time_label = tk.Label(
            timestamp_frame,
            text="0:00",
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            fg=TEXT_SECONDARY,
            bg=SECONDARY_COLOR
        )
        self.total_time_label.pack(side='right')
        
        # Playback controls
        controls_container = tk.Frame(self.control_frame, bg=SECONDARY_COLOR)
        controls_container.pack(pady=(5, 15))
        
        # Previous button
        self.prev_btn = tk.Button(
            controls_container,
            text="⏮",
            font=(FONT_FAMILY, 20),
            fg=TEXT_ACTIVE,
            bg=SECONDARY_COLOR,
            relief='flat',
            bd=0,
            width=3,
            cursor='hand2',
            activebackground=BUTTON_HOVER_COLOR,
            activeforeground=TEXT_ACTIVE,
            command=self.previous_track
        )
        self.prev_btn.pack(side='left', padx=10)
        
        # Play/Pause button (larger)
        self.play_pause_btn = tk.Button(
            controls_container,
            text="▶",
            font=(FONT_FAMILY, 24),
            fg=TEXT_ACTIVE,
            bg=SECONDARY_COLOR,
            relief='flat',
            bd=0,
            width=3,
            cursor='hand2',
            activebackground=BUTTON_HOVER_COLOR,
            activeforeground=TEXT_ACTIVE,
            command=self.toggle_playback
        )
        self.play_pause_btn.pack(side='left', padx=15)
        
        # Next button
        self.next_btn = tk.Button(
            controls_container,
            text="⏭",
            font=(FONT_FAMILY, 20),
            fg=TEXT_ACTIVE,
            bg=SECONDARY_COLOR,
            relief='flat',
            bd=0,
            width=3,
            cursor='hand2',
            activebackground=BUTTON_HOVER_COLOR,
            activeforeground=TEXT_ACTIVE,
            command=self.next_track
        )
        self.next_btn.pack(side='left', padx=10)
    
    def _bind_events(self):
        """Bind keyboard and window events"""
        # Keyboard shortcuts
        self.root.bind('<space>', lambda e: self.toggle_playback())
        self.root.bind('<Right>', lambda e: self.next_track())
        self.root.bind('<Left>', lambda e: self.previous_track())
        self.root.bind('<t>', lambda e: self.show_transparency_popup())
        self.root.bind('<T>', lambda e: self.show_transparency_popup())
        self.root.bind('<Escape>', lambda e: self.hide_transparency_popup())
        
        # Window dragging
        self.header_frame.bind('<Button-1>', self._start_drag)
        self.header_frame.bind('<B1-Motion>', self._on_drag)
        self.title_label.bind('<Button-1>', self._start_drag)
        self.title_label.bind('<B1-Motion>', self._on_drag)
        self.artist_label.bind('<Button-1>', self._start_drag)
        self.artist_label.bind('<B1-Motion>', self._on_drag)
        self.album_label.bind('<Button-1>', self._start_drag)
        self.album_label.bind('<B1-Motion>', self._on_drag)
        
        # Window resize
        self.root.bind('<Configure>', self._on_window_resize)
    
    # ==================== Spotify Controller Integration ====================
    
    def set_spotify_controller(self, controller):
        """Set Spotify controller and bind callbacks"""
        self.spotify_controller = controller
        if controller:
            controller.bind_progress_callback(self.on_progress_update)
    
    def set_lyrics_fetcher(self, fetcher):
        """Set lyrics fetcher"""
        self.lyrics_fetcher = fetcher
    
    def on_progress_update(self, progress_ms, duration_ms):
        """Handle playback progress updates"""
        self.current_progress_ms = progress_ms
        self.current_duration_ms = duration_ms
        
        # Update progress bar
        self._update_progress_bar(progress_ms, duration_ms)
        
        # Update timestamps
        self._update_timestamps(progress_ms, duration_ms)
        
        # Check for song change
        if self.spotify_controller:
            track = self.spotify_controller.get_current_track()
            if track:
                track_id = track.get('id')
                if track_id != self.current_song_id:
                    self.current_song_id = track_id
                    # Pass duration from track data
                    track_duration = track.get('duration_ms', duration_ms)
                    self._on_song_changed(track, track_duration)
        
        # Recalculate timing if we have lyrics but no timing yet
        if self.lyric_lines and not self.timed_lyrics and duration_ms > 0 and self.spotify_controller:
            print(f"Recalculating timing with duration: {duration_ms}ms")
            lines = [line['text'] for line in self.lyric_lines]
            self.timed_lyrics = self.spotify_controller.calculate_line_timing(lines, duration_ms)
            print(f"Timing calculated: {len(self.timed_lyrics)} lines")
        
        # Update lyrics highlighting with offset
        if self.timed_lyrics and self.spotify_controller:
            # Apply timing offset: subtract delay to make lyrics appear later
            # If offset is +1000ms, lyrics at 10s will highlight at 11s playback
            from .styles import LYRICS_OFFSET_MS
            adjusted_progress = progress_ms - LYRICS_OFFSET_MS
            
            current_index = self.spotify_controller.get_current_line_index(
                adjusted_progress, self.timed_lyrics
            )
            if current_index != self.current_line_index and current_index >= 0:
                print(f"Highlighting line {current_index} at {progress_ms}ms")
                self.highlight_current_line(current_index)
    
    def _on_song_changed(self, track, duration_ms=None):
        """Handle song change"""
        # Store duration immediately from track data
        if duration_ms:
            self.current_duration_ms = duration_ms
            print(f"Song changed - Duration: {duration_ms}ms ({duration_ms/1000:.1f}s)")
        elif track.get('duration_ms'):
            self.current_duration_ms = track.get('duration_ms')
            print(f"Song changed - Duration from track: {self.current_duration_ms}ms")
        
        # Update song info
        self.update_song_info(track)
        
        # Fetch and display lyrics in background thread
        if self.lyrics_fetcher:
            artist = track['artists'][0]['name'] if track.get('artists') else "Unknown"
            title = track.get('name', 'Unknown')
            
            # Get additional metadata for LRClib API
            album = track.get('album', {}).get('name', None)
            duration_sec = self.current_duration_ms / 1000 if self.current_duration_ms else None
            
            # Show loading message
            self._show_loading_message_lyrics()
            
            # Fetch lyrics in background thread
            import threading
            def fetch_lyrics_thread():
                try:
                    if not self.lyrics_fetcher:
                        print("Lyrics fetcher not available")
                        self.root.after(0, self._show_error_message)
                        return
                    
                    print(f"Fetching lyrics for: {artist} - {title}")
                    if album:
                        print(f"Album: {album}")
                    
                    # Pass album and duration to improve LRClib matching
                    lyrics = self.lyrics_fetcher.fetch_lyrics(
                        artist, title, album=album, duration=duration_sec
                    )
                    print(f"Lyrics fetched: {type(lyrics)} - {len(lyrics) if lyrics else 0} items")
                    
                    # Update UI in main thread
                    self.root.after(0, lambda: self._handle_lyrics_result(lyrics))
                except Exception as e:
                    print(f"Error fetching lyrics: {e}")
                    import traceback
                    traceback.print_exc()
                    self.root.after(0, self._show_error_message)
            
            thread = threading.Thread(target=fetch_lyrics_thread, daemon=True)
            thread.start()
    
    def _handle_lyrics_result(self, lyrics):
        """Handle lyrics fetch result in main thread"""
        if not lyrics:
            self._show_no_lyrics_message()
            return
        
        # Check format: LRClib synced format (tuple/list) or Genius format (dict)
        if isinstance(lyrics, list) and len(lyrics) > 0:
            first_item = lyrics[0]
            
            # LRClib synced format: [(text, start_ms, end_ms), ...] or [[text, start_ms, end_ms], ...]
            # Note: JSON converts tuples to lists, so we check for both
            if (isinstance(first_item, (tuple, list)) and 
                len(first_item) == 3 and 
                isinstance(first_item[1], (int, float)) and 
                isinstance(first_item[2], (int, float))):
                
                print(f"✅ Received SYNCED lyrics with timestamps from LRClib!")
                print(f"   Format: List of {type(first_item).__name__}s (text, start_ms, end_ms)")
                print(f"   Lines: {len(lyrics)}")
                
                # Convert to tuples if needed (JSON loads as lists)
                if isinstance(first_item, list):
                    self.timed_lyrics = [(line[0], line[1], line[2]) for line in lyrics]
                else:
                    self.timed_lyrics = lyrics
                
                # Extract text for display
                lyrics_text = '\n'.join([line[0] for line in lyrics])
                
                # Update display with synced flag
                self.update_lyrics(lyrics_text, has_synced_timing=True)
                return
            
            # Genius format: [{'text': ..., 'start_time': None, 'line_number': ...}]
            elif isinstance(first_item, dict) and 'text' in first_item:
                print(f"⚠️ Received plain lyrics from Genius (no timestamps)")
                print(f"   Format: List of dicts with 'text' key")
                lyrics_text = '\n'.join([line.get('text', '') for line in lyrics if line.get('text')])
                
                if lyrics_text and lyrics_text.strip():
                    self.update_lyrics(lyrics_text, has_synced_timing=False)
                else:
                    print("No lyrics text after conversion")
                    self._show_no_lyrics_message()
                return
        
        # Fallback: treat as string
        if isinstance(lyrics, str):
            print(f"⚠️ Received plain text lyrics")
            self.update_lyrics(lyrics, has_synced_timing=False)
            return
        
        print(f"⚠️ Unknown lyrics format: {type(lyrics)}")
        self._show_no_lyrics_message()
    
    # ==================== UI Update Methods ====================
    
    def update_song_info(self, track):
        """Update song information display"""
        if not track:
            self.title_label.config(text="Not Playing")
            self.artist_label.config(text="")
            self.album_label.config(text="")
            self._set_placeholder_album_art()
            return
        
        # Update text
        title = track.get('name', 'Unknown')
        artists = ', '.join([artist['name'] for artist in track.get('artists', [])])
        album = track.get('album', {}).get('name', '')
        
        self.title_label.config(text=title)
        self.artist_label.config(text=artists)
        self.album_label.config(text=album)
        
        # Update album art
        album_art_url = None
        if track.get('album', {}).get('images'):
            images = track['album']['images']
            album_art_url = images[0]['url'] if images else None
        
        if album_art_url:
            self._load_album_art(album_art_url)
        else:
            self._set_placeholder_album_art()
    
    def update_lyrics(self, lyrics_text, has_synced_timing=False):
        """
        Update lyrics display with new lyrics
        
        Args:
            lyrics_text: Plain text lyrics (newline separated)
            has_synced_timing: True if self.timed_lyrics already has accurate timestamps from LRClib
        """
        if not lyrics_text:
            self._show_no_lyrics_message()
            return
        
        # Clear existing lyrics
        self.lyrics_canvas.delete('all')
        self.lyric_lines.clear()
        
        # Don't clear timed_lyrics if we already have synced timing
        if not has_synced_timing:
            self.timed_lyrics = []
        
        # Clean and filter lyrics to remove metadata
        lyrics_text = self._clean_lyrics_text(lyrics_text)
        
        # Split lyrics into lines
        lines = [line.strip() for line in lyrics_text.split('\n') if line.strip()]
        
        if not lines:
            self._show_no_lyrics_message()
            return
        
        print(f"Rendering {len(lines)} lyric lines")
        
        # Render lyrics on canvas first
        self._render_lyrics(lines)
        
        # Handle timing
        if has_synced_timing and self.timed_lyrics:
            # We already have accurate timestamps from LRClib!
            print(f"✅ Using SYNCED timestamps from LRClib ({len(self.timed_lyrics)} lines)")
            if self.timed_lyrics:
                print(f"   First line: {self.timed_lyrics[0][1]}ms - {self.timed_lyrics[0][2]}ms")
                print(f"   Last line: {self.timed_lyrics[-1][1]}ms - {self.timed_lyrics[-1][2]}ms")
        elif self.spotify_controller and self.current_duration_ms > 0:
            # Calculate estimated timing (Genius fallback)
            print(f"⚠️ No synced timestamps, calculating ESTIMATED even distribution...")
            self.timed_lyrics = self.spotify_controller.calculate_line_timing(
                lines, self.current_duration_ms
            )
            print(f"   Timing calculated for {len(self.timed_lyrics)} lines")
            if self.timed_lyrics:
                print(f"   First line: {self.timed_lyrics[0][1]}ms - {self.timed_lyrics[0][2]}ms")
                print(f"   Last line: {self.timed_lyrics[-1][1]}ms - {self.timed_lyrics[-1][2]}ms")
        else:
            print(f"⚠️ No duration available yet (duration={self.current_duration_ms}ms), timing will be calculated on next progress update")
            self.timed_lyrics = []
        
        # Reset current line
        self.current_line_index = -1
    
    def _clean_lyrics_text(self, text):
        """Clean lyrics text by removing metadata and unwanted content"""
        if not text:
            return ""
        
        lines = text.split('\n')
        cleaned_lines = []
        
        # Metadata keywords to filter out
        metadata_keywords = [
            'title track', 'single', 'written by', 'produced by', 'album', 
            'debut', 'released', 'available', 'music video', 'official video',
            'lyrics from', 'copyright', '©', 'all rights reserved',
            'embed', 'see live', 'get tickets', 'more on genius',
            'contributors', 'transcribers', 'have the inside scoop',
            'verified by', 'genius', 'how to format'
        ]
        
        # Section markers to keep but clean
        section_markers = ['[verse', '[chorus', '[bridge', '[hook', '[intro', 
                          '[outro', '[pre-chorus', '[refrain', '[interlude']
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Skip empty lines
            if not line_lower:
                continue
            
            # Skip metadata lines
            if any(keyword in line_lower for keyword in metadata_keywords):
                print(f"Filtering out metadata line: {line[:50]}...")
                continue
            
            # Skip lines that are just numbers (likely footnotes)
            if line.strip().isdigit():
                continue
            
            # Skip lines with URLs
            if 'http://' in line_lower or 'https://' in line_lower or '.com' in line_lower:
                continue
            
            # Keep section markers but don't duplicate them
            is_section_marker = any(marker in line_lower for marker in section_markers)
            if is_section_marker:
                # Only add if the previous line wasn't also a section marker
                if not cleaned_lines or not any(marker in cleaned_lines[-1].lower() for marker in section_markers):
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines)
        print(f"Cleaned lyrics: {len(lines)} lines -> {len(cleaned_lines)} lines")
        return result
    
    def _render_lyrics(self, lines):
        """Render lyrics lines on canvas"""
        canvas_width = self.lyrics_canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = WINDOW_WIDTH - (LYRICS_PADDING * 2)
        
        y_position = 100  # Start position
        line_spacing = int(FONT_SIZE * LINE_SPACING)
        
        for i, line_text in enumerate(lines):
            # Start all lines with very low opacity (will be updated immediately)
            opacity = 0.1  # Very dim initially
            color = self._opacity_to_color(TEXT_MUTED, opacity)
            
            # Create text on canvas
            canvas_id = self.lyrics_canvas.create_text(
                canvas_width // 2,
                y_position,
                text=line_text,
                font=(FONT_FAMILY, FONT_SIZE),
                fill=color,
                width=canvas_width - 40,
                justify='center',
                anchor='center'
            )
            
            # Store line data
            self.lyric_lines.append({
                'text': line_text,
                'canvas_id': canvas_id,
                'y_pos': y_position,
                'index': i,
                'opacity': opacity
            })
            
            y_position += line_spacing
        
        # Update total height and configure scroll region
        self.total_lyrics_height = y_position + 100
        self.lyrics_canvas.configure(scrollregion=(0, 0, canvas_width, self.total_lyrics_height))
        
        # Immediately update highlighting based on current playback position
        if self.timed_lyrics and self.spotify_controller and self.current_progress_ms > 0:
            current_index = self.spotify_controller.get_current_line_index(
                self.current_progress_ms, self.timed_lyrics
            )
            if current_index >= 0:
                print(f"Initial highlight at line {current_index}")
                self.highlight_current_line(current_index)
        else:
            # If no timing yet, just highlight first line
            print("No timing available, highlighting first line")
            self.highlight_current_line(0)
    
    def highlight_current_line(self, line_index):
        """Smoothly highlight the current playing line"""
        if line_index < 0 or line_index >= len(self.lyric_lines):
            return
        
        if line_index == self.current_line_index:
            return
        
        print(f"Highlighting line {line_index}: {self.lyric_lines[line_index]['text'][:50]}...")
        
        old_index = self.current_line_index
        self.current_line_index = line_index
        
        # Update all lines based on their distance from current
        for i, line in enumerate(self.lyric_lines):
            target_opacity = calculate_opacity_for_line(line_index, i, len(self.lyric_lines))
            target_size = FONT_SIZE_CURRENT if i == line_index else FONT_SIZE
            
            # Animate opacity and size
            self._animate_line(i, target_opacity, target_size)
        
        # Smooth scroll to keep line centered
        self.smooth_scroll_to_line(line_index)
    
    def _animate_line(self, line_index, target_opacity, target_size):
        """Animate a lyric line to target state"""
        if line_index < 0 or line_index >= len(self.lyric_lines):
            return
        
        line = self.lyric_lines[line_index]
        current_opacity = line['opacity']
        
        # Animate opacity
        def update_opacity(value):
            line['opacity'] = value
            color = self._opacity_to_color(TEXT_ACTIVE, value)
            self.lyrics_canvas.itemconfig(line['canvas_id'], fill=color)
        
        self.animation_engine.animate_property(
            current_opacity,
            target_opacity,
            ANIMATION_NORMAL,
            update_opacity,
            easing="ease-in-out"
        )
        
        # Update font size
        weight = "bold" if line_index == self.current_line_index else "normal"
        self.lyrics_canvas.itemconfig(
            line['canvas_id'],
            font=(FONT_FAMILY, target_size, weight)
        )
    
    def smooth_scroll_to_line(self, line_index):
        """Smooth scroll to keep line at center"""
        if line_index < 0 or line_index >= len(self.lyric_lines):
            return
        
        line = self.lyric_lines[line_index]
        canvas_height = self.lyrics_canvas.winfo_height()
        
        # Target position: 45% from top
        target_y_center = canvas_height * 0.45
        
        # Calculate required scroll offset
        self.target_scroll_offset = line['y_pos'] - target_y_center
        
        # Clamp to valid range
        max_scroll = max(0, self.total_lyrics_height - canvas_height)
        self.target_scroll_offset = max(0, min(self.target_scroll_offset, max_scroll))
        
        # Start smooth scroll animation
        if not self.is_scrolling:
            self.is_scrolling = True
            self._animate_scroll()
    
    def _animate_scroll(self):
        """Smoothly animate scroll position"""
        diff = self.target_scroll_offset - self.scroll_offset
        
        if abs(diff) < 1:
            self.scroll_offset = self.target_scroll_offset
            self.is_scrolling = False
            return
        
        # Ease towards target (exponential decay)
        self.scroll_offset += diff * 0.15  # 15% per frame
        
        # Update canvas scroll
        if self.total_lyrics_height > 0:
            self.lyrics_canvas.yview_moveto(self.scroll_offset / self.total_lyrics_height)
        
        # Continue animation
        if self.is_scrolling:
            self.root.after(16, self._animate_scroll)  # ~60fps
    
    # ==================== Playback Control Methods ====================
    
    def toggle_playback(self):
        """Toggle play/pause"""
        if self.spotify_controller:
            if self.is_playing:
                self.spotify_controller.pause_playback()
                self.play_pause_btn.config(text="▶")
                self.is_playing = False
            else:
                self.spotify_controller.start_playback()
                self.play_pause_btn.config(text="⏸")
                self.is_playing = True
    
    def next_track(self):
        """Skip to next track"""
        if self.spotify_controller:
            self.spotify_controller.next_track()
    
    def previous_track(self):
        """Skip to previous track"""
        if self.spotify_controller:
            self.spotify_controller.previous_track()
    
    # ==================== Helper Methods ====================
    
    def _update_progress_bar(self, progress_ms, duration_ms):
        """Update progress bar visual"""
        if duration_ms <= 0:
            return
        
        progress_ratio = progress_ms / duration_ms
        canvas_width = self.progress_canvas.winfo_width()
        
        if canvas_width > 1:
            progress_width = int(canvas_width * progress_ratio)
            self.progress_canvas.coords(
                self.progress_fg_rect,
                0, 1, progress_width, 5
            )
    
    def _update_timestamps(self, progress_ms, duration_ms):
        """Update timestamp labels"""
        current_time = self._format_time(progress_ms)
        total_time = self._format_time(duration_ms)
        
        self.current_time_label.config(text=current_time)
        self.total_time_label.config(text=total_time)
    
    def _format_time(self, ms):
        """Format milliseconds to MM:SS"""
        seconds = int(ms / 1000)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    def _opacity_to_color(self, base_color, opacity):
        """Convert opacity to color with fade effect"""
        # Parse base color (assuming hex format like "#RRGGBB")
        if base_color.startswith('#'):
            base_color = base_color[1:]
        
        # Extract RGB components
        r = int(base_color[0:2], 16)
        g = int(base_color[2:4], 16)
        b = int(base_color[4:6], 16)
        
        # Interpolate with background color based on opacity
        bg_color = BACKGROUND_COLOR[1:] if BACKGROUND_COLOR.startswith('#') else BACKGROUND_COLOR
        bg_r = int(bg_color[0:2], 16)
        bg_g = int(bg_color[2:4], 16)
        bg_b = int(bg_color[4:6], 16)
        
        # Blend colors
        final_r = int(r * opacity + bg_r * (1 - opacity))
        final_g = int(g * opacity + bg_g * (1 - opacity))
        final_b = int(b * opacity + bg_b * (1 - opacity))
        
        return f"#{final_r:02x}{final_g:02x}{final_b:02x}"
    
    def _load_album_art(self, url):
        """Load and display circular album art"""
        try:
            image = download_image(url)
            circular_image = create_circular_image(image, (ALBUM_ART_SIZE, ALBUM_ART_SIZE))
            self.album_art_image = circular_image  # Keep reference
            self.album_art_label.config(image=circular_image)
        except Exception as e:
            print(f"Error loading album art: {e}")
            self._set_placeholder_album_art()
    
    def _set_placeholder_album_art(self):
        """Set placeholder album art"""
        try:
            placeholder = create_placeholder_image(ACCENT_COLOR, (ALBUM_ART_SIZE, ALBUM_ART_SIZE))
            circular_image = create_circular_image(placeholder, (ALBUM_ART_SIZE, ALBUM_ART_SIZE))
            self.album_art_image = circular_image  # Keep reference
            self.album_art_label.config(image=circular_image)
        except Exception as e:
            print(f"Error setting placeholder: {e}")
    
    def _show_loading_message(self):
        """Show loading message on canvas"""
        canvas_width = self.lyrics_canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = WINDOW_WIDTH - (LYRICS_PADDING * 2)
        
        self.lyrics_canvas.create_text(
            canvas_width // 2,
            200,
            text="Waiting for playback...",
            font=(FONT_FAMILY, FONT_SIZE_INFO),
            fill=TEXT_MUTED,
            anchor='center'
        )
    
    def _show_loading_message_lyrics(self):
        """Show loading lyrics message"""
        self.lyrics_canvas.delete('all')
        canvas_width = self.lyrics_canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = WINDOW_WIDTH - (LYRICS_PADDING * 2)
        
        self.lyrics_canvas.create_text(
            canvas_width // 2,
            200,
            text="Loading lyrics...",
            font=(FONT_FAMILY, FONT_SIZE_INFO),
            fill=TEXT_MUTED,
            anchor='center'
        )
    
    def _show_no_lyrics_message(self):
        """Show no lyrics available message"""
        self.lyrics_canvas.delete('all')
        canvas_width = self.lyrics_canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = WINDOW_WIDTH - (LYRICS_PADDING * 2)
        
        self.lyrics_canvas.create_text(
            canvas_width // 2,
            200,
            text="No lyrics available",
            font=(FONT_FAMILY, FONT_SIZE_INFO),
            fill=TEXT_MUTED,
            anchor='center'
        )
    
    def _show_error_message(self):
        """Show error message"""
        self.lyrics_canvas.delete('all')
        canvas_width = self.lyrics_canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = WINDOW_WIDTH - (LYRICS_PADDING * 2)
        
        self.lyrics_canvas.create_text(
            canvas_width // 2,
            200,
            text="Error loading lyrics",
            font=(FONT_FAMILY, FONT_SIZE_INFO),
            fill=TEXT_MUTED,
            anchor='center'
        )
    
    # ==================== Transparency Popup ====================
    
    def show_transparency_popup(self):
        """Show transparency adjustment popup"""
        # Create overlay
        self.transparency_overlay = tk.Frame(
            self.root,
            bg='#000000'
        )
        self.transparency_overlay.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Make overlay semi-transparent
        try:
            # Use a separate toplevel for better transparency control
            self.transparency_popup = tk.Toplevel(self.root)
            self.transparency_popup.overrideredirect(True)
            self.transparency_popup.attributes('-topmost', True)
            
            # Position popup
            popup_width = 300
            popup_height = 150
            x = self.root.winfo_x() + (WINDOW_WIDTH - popup_width) // 2
            y = self.root.winfo_y() + (WINDOW_HEIGHT - popup_height) // 2
            self.transparency_popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
            
            # Popup background
            popup_bg = tk.Frame(
                self.transparency_popup,
                bg=SECONDARY_COLOR,
                relief='solid',
                bd=1
            )
            popup_bg.pack(fill='both', expand=True)
            
            # Title
            title = tk.Label(
                popup_bg,
                text="Window Transparency",
                font=(FONT_FAMILY, FONT_SIZE_TITLE, "bold"),
                fg=TEXT_ACTIVE,
                bg=SECONDARY_COLOR
            )
            title.pack(pady=(20, 15))
            
            # Slider
            current_alpha = int(self.window_opacity * 100)
            self.transparency_slider = tk.Scale(
                popup_bg,
                from_=30,
                to=100,
                orient='horizontal',
                bg=SECONDARY_COLOR,
                fg=TEXT_ACTIVE,
                troughcolor=PROGRESS_BG,
                activebackground=ACCENT_COLOR,
                highlightthickness=0,
                relief='flat',
                command=self.on_transparency_change
            )
            self.transparency_slider.set(current_alpha)
            self.transparency_slider.pack(padx=30, fill='x', pady=(0, 10))
            
            # Close button
            close_btn = tk.Button(
                popup_bg,
                text="Close",
                font=(FONT_FAMILY, FONT_SIZE),
                fg=TEXT_ACTIVE,
                bg=BUTTON_HOVER_COLOR,
                relief='flat',
                cursor='hand2',
                command=self.hide_transparency_popup
            )
            close_btn.pack(pady=10)
            
            # Bind ESC to close
            self.transparency_popup.bind('<Escape>', lambda e: self.hide_transparency_popup())
            
        except Exception as e:
            print(f"Error showing transparency popup: {e}")
            self.hide_transparency_popup()
    
    def on_transparency_change(self, value):
        """Update window transparency in real-time"""
        alpha = float(value) / 100
        self.window_opacity = alpha
        try:
            self.root.attributes('-alpha', alpha)
        except:
            pass
    
    def hide_transparency_popup(self):
        """Hide transparency popup"""
        if hasattr(self, 'transparency_popup'):
            self.transparency_popup.destroy()
            del self.transparency_popup
        if hasattr(self, 'transparency_overlay'):
            self.transparency_overlay.destroy()
            del self.transparency_overlay
    
    # ==================== Window Management ====================
    
    def _start_drag(self, event):
        """Start window drag"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def _on_drag(self, event):
        """Handle window dragging"""
        x = self.root.winfo_x() + (event.x - self.drag_start_x)
        y = self.root.winfo_y() + (event.y - self.drag_start_y)
        self.root.geometry(f"+{x}+{y}")
    
    def minimize_window(self):
        """Minimize window"""
        self.root.iconify()
    
    def _on_window_resize(self, event):
        """Handle window resize"""
        if event.widget == self.root:
            # Update progress canvas width
            if hasattr(self, 'progress_canvas'):
                self.progress_canvas.coords(
                    self.progress_bg_rect,
                    0, 1, event.width - 40, 5
                )
    
    def _on_mouse_wheel(self, event):
        """Handle mouse wheel scrolling"""
        # Manual scroll (overrides auto-scroll temporarily)
        self.lyrics_canvas.yview_scroll(-1 * (event.delta // 120), "units")
    
    def _on_progress_click(self, event):
        """Handle progress bar click for seeking"""
        if self.spotify_controller and self.current_duration_ms > 0:
            canvas_width = self.progress_canvas.winfo_width()
            click_ratio = event.x / canvas_width
            seek_position = int(self.current_duration_ms * click_ratio)
            
            # Note: Seeking requires additional Spotify API implementation
            print(f"Seek to: {seek_position}ms")
    
    def on_close(self):
        """Handle window close"""
        if self.spotify_controller:
            self.spotify_controller.cleanup()
        self.animation_engine.cancel_all_animations()
        self.root.quit()
        self.root.destroy()
    
    def _start_update_loop(self):
        """Start main update loop"""
        # This ensures UI stays responsive
        self.root.after(100, self._update_loop)
    
    def _update_loop(self):
        """Main update loop"""
        # Update playback state if needed
        if self.spotify_controller:
            playback = self.spotify_controller.get_playback_state()
            if playback:
                self.is_playing = playback.get('is_playing', False)
                self.play_pause_btn.config(text="⏸" if self.is_playing else "▶")
        
        # Schedule next update
        self.root.after(100, self._update_loop)


# Alias for compatibility
LyricsWindow = ModernLyricsWindow
