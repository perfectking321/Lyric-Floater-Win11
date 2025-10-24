"""
Pygame-based Lyrics Window - Hardware Accelerated
Main window using Pygame for GPU-accelerated rendering
"""
import pygame
import sys
import os
from typing import List, Tuple, Optional, Dict
import threading
import requests
from io import BytesIO

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.styles import *
from ui.pygame_text_renderer import TextRenderer, TextLayout
from ui.pygame_sprite_manager import LyricSpriteManager
from ui.pygame_ui_components import Button, ImageButton, ProgressBar, Label, AlbumArt, OpacitySlider



class PygameLyricsWindow:
    """Hardware-accelerated lyrics window using Pygame"""
    
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.display.set_caption("Lyrics Floater - Pygame")
        
        # Create window (with RESIZABLE flag)
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 
                                              pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
        
        # Window dimensions (for resizing)
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        self.min_width = 400
        self.min_height = 500
        
        # Set window to stay on top (platform-specific)
        self._set_window_on_top()
        
        # Clock for FPS control
        self.clock = pygame.time.Clock()
        self.target_fps = 60
        
        # Core components
        self.text_renderer = TextRenderer()
        self.text_layout = TextLayout(self.text_renderer)
        self.sprite_manager = LyricSpriteManager(self.text_renderer, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Controllers
        self.spotify_controller = None
        self.lyrics_fetcher = None
        
        # State
        self.running = True
        self.current_song_id = None
        self.is_playing = False
        self.current_progress_ms = 0
        self.current_duration_ms = 0
        self.timed_lyrics: List[Tuple[str, int, int]] = []
        
        # Transparency control
        self.window_opacity = 0.95  # 95% opacity (5% transparent)
        self.show_opacity_popup = False
        self.opacity_slider_value = self.window_opacity
        
        # Background color
        self.bg_color = self._hex_to_rgb(BACKGROUND_COLOR)
        
        # Apply initial transparency
        self._set_window_opacity(self.window_opacity)
        
        # UI Components
        self._create_ui_components()
        
        # Window dragging
        self.is_dragging = False
        self.drag_offset = (0, 0)
        
        # Performance stats
        self.frame_count = 0
        self.fps = 60
        self.show_stats = False
        
        print("[PygameLyricsWindow] Initialized successfully")
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex to RGB"""
        hex_color = hex_color.lstrip('#')
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return (r, g, b)
    
    def _set_window_on_top(self):
        """Platform-specific always-on-top"""
        try:
            # Windows
            import ctypes
            hwnd = pygame.display.get_wm_info()['window']
            ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)
        except:
            print("[Window] Could not set always-on-top")
    
    def _set_window_opacity(self, opacity: float):
        """Set window transparency (Windows only)"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Get window handle
            hwnd = pygame.display.get_wm_info()['window']
            
            # Constants for Windows API
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000
            LWA_ALPHA = 0x00000002
            
            # Get current extended style
            user32 = ctypes.windll.user32
            ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            
            # Add layered window style
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED)
            
            # Set alpha (0-255, where 255 is fully opaque)
            alpha = int(opacity * 255)
            user32.SetLayeredWindowAttributes(hwnd, 0, alpha, LWA_ALPHA)
            
            print(f"[Window] Opacity set to {opacity*100:.0f}%")
        except Exception as e:
            print(f"[Window] Could not set opacity: {e}")
    
    def _reposition_ui_components(self):
        """Update UI component positions after window resize"""
        # Get fonts
        font_small = self.text_renderer.fonts['small']
        font_normal = self.text_renderer.fonts['normal']
        font_title = self.text_renderer.fonts['title']
        
        # Update progress bar position and width
        progress_y = self.window_height - CONTROL_HEIGHT + 10
        self.progress_bar.rect = pygame.Rect(20, progress_y, self.window_width - 40, 4)
        
        # Update time labels
        self.time_current_label.rect.topleft = (20, progress_y + 10)
        self.time_total_label.rect.topleft = (self.window_width - 60, progress_y + 10)
        
        # Update control buttons (centered)
        control_y = progress_y + 35
        button_center_x = self.window_width // 2
        self.play_button.rect.center = (button_center_x, control_y + 20)
        self.prev_button.rect.center = (button_center_x - 70, control_y + 20)
        self.next_button.rect.center = (button_center_x + 70, control_y + 20)
        
        # Update transparency button (top right)
        self.transparency_button.rect.topleft = (self.window_width - 70, 20)
        
        # Update opacity slider (right side)
        popup_x = self.window_width - 90
        self.opacity_slider.rect.x = popup_x
        self.opacity_label.x = popup_x + 10
        
        # Update stats label (bottom right)
        self.stats_label.rect.topleft = (self.window_width - 250, self.window_height - 20)
        
        print(f"[Window] UI components repositioned for {self.window_width}x{self.window_height}")
    
    def _create_ui_components(self):
        """Create all UI components"""
        # Fonts for UI
        font_small = self.text_renderer.fonts['small']
        font_normal = self.text_renderer.fonts['normal']
        font_title = self.text_renderer.fonts['title']
        
        # Header components
        header_y = 20
        
        # Album art
        self.album_art = AlbumArt(20, header_y, ALBUM_ART_SIZE)
        
        # Song info labels
        info_x = 20 + ALBUM_ART_SIZE + 15
        self.song_title_label = Label(info_x, header_y, "No song playing", font_title, TEXT_INFO)
        self.artist_label = Label(info_x, header_y + 25, "", font_normal, TEXT_SECONDARY)
        self.album_label = Label(info_x, header_y + 45, "", font_small, TEXT_SECONDARY)
        
        # Progress bar
        progress_y = WINDOW_HEIGHT - CONTROL_HEIGHT + 10
        self.progress_bar = ProgressBar(
            20, progress_y, WINDOW_WIDTH - 40, 4,
            on_scrub=self._on_progress_scrub
        )
        
        # Time labels
        self.time_current_label = Label(20, progress_y + 10, "0:00", font_small, TEXT_SECONDARY)
        self.time_total_label = Label(WINDOW_WIDTH - 60, progress_y + 10, "0:00", 
                                      font_small, TEXT_SECONDARY)
        
        # Control buttons
        control_y = progress_y + 35
        button_center_x = WINDOW_WIDTH // 2
        
        # Create simple button surfaces (we'll use text for now, icons later)
        self.play_button = Button(
            button_center_x - 30, control_y, 60, 40,
            "⏸" if self.is_playing else "▶",
            font_normal,
            callback=self._on_play_pause_clicked
        )
        
        self.prev_button = Button(
            button_center_x - 100, control_y, 50, 40,
            "⏮",
            font_small,
            callback=self._on_prev_clicked
        )
        
        self.next_button = Button(
            button_center_x + 50, control_y, 50, 40,
            "⏭",
            font_small,
            callback=self._on_next_clicked
        )
        
        # Transparency button (top right corner)
        self.transparency_button = Button(
            WINDOW_WIDTH - 70, 20, 50, 30,
            "◐",  # Half-circle icon for transparency
            font_small,
            callback=self._on_transparency_clicked
        )
        
        # Opacity slider popup (hidden by default)
        popup_x = WINDOW_WIDTH - 90
        popup_y = 60
        self.opacity_slider = OpacitySlider(
            popup_x, popup_y, 20, 150,
            initial_value=self.window_opacity,
            on_change=self._on_opacity_changed
        )
        self.opacity_label = Label(popup_x - 20, popup_y + 160, "95%", 
                                   font_small, TEXT_INFO, centered=True)
        
        # Stats label (bottom right, hidden by default)
        self.stats_label = Label(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 20, 
                                 "FPS: 60", font_small, TEXT_SECONDARY)
    
    def set_controllers(self, spotify_controller, lyrics_fetcher):
        """Set Spotify and lyrics controllers"""
        self.spotify_controller = spotify_controller
        self.lyrics_fetcher = lyrics_fetcher
        
        # Bind progress callback
        if self.spotify_controller:
            self.spotify_controller.bind_progress_callback(self.on_progress_update)
            print("[PygameLyricsWindow] Controllers set")
    
    def run(self):
        """Main game loop"""
        print("[PygameLyricsWindow] Starting main loop (60 FPS target)")
        
        while self.running:
            # Handle events
            self._handle_events()
            
            # Update
            self._update()
            
            # Draw
            self._draw()
            
            # Control FPS
            self.clock.tick(self.target_fps)
            self.frame_count += 1
            
            # Update FPS counter every second
            if self.frame_count % 60 == 0:
                self.fps = self.clock.get_fps()
        
        self.quit()
    
    def _handle_events(self):
        """Handle all Pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.VIDEORESIZE:
                # Window resized - update dimensions and recreate surface
                new_width = max(event.w, self.min_width)
                new_height = max(event.h, self.min_height)
                
                print(f"[Window] Resized to {new_width}x{new_height}")
                
                self.window_width = new_width
                self.window_height = new_height
                
                # Recreate screen surface
                self.screen = pygame.display.set_mode(
                    (new_width, new_height), 
                    pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
                )
                
                # Recreate sprite manager with new dimensions
                self.sprite_manager = LyricSpriteManager(
                    self.text_renderer, new_width, new_height
                )
                
                # Reload current lyrics if available
                if self.timed_lyrics:
                    lines = [item[0] for item in self.timed_lyrics]
                    self.sprite_manager.load_lyrics(lines)
                
                # Update UI component positions
                self._reposition_ui_components()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F1:
                    self.show_stats = not self.show_stats
                elif event.key == pygame.K_SPACE:
                    self._on_play_pause_clicked()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check if clicking header for drag
                    if event.pos[1] < HEADER_HEIGHT:
                        self.is_dragging = True
                        window_pos = pygame.display.get_surface().get_abs_offset()
                        self.drag_offset = (event.pos[0], event.pos[1])
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging:
                    # Move window (requires OS-specific code)
                    pass
            
            # UI component events
            self.progress_bar.handle_event(event)
            self.play_button.handle_event(event)
            self.prev_button.handle_event(event)
            self.next_button.handle_event(event)
            self.transparency_button.handle_event(event)
            
            # Opacity slider (only if popup is shown)
            if self.show_opacity_popup:
                self.opacity_slider.handle_event(event)
    
    def _update(self):
        """Update game state"""
        # Update sprite manager
        self.sprite_manager.update()
        
        # Update stats label
        if self.show_stats:
            cache_stats = self.text_renderer.get_cache_stats()
            self.stats_label.set_text(
                f"FPS: {int(self.fps)} | Cache: {cache_stats['cache_size']} "
                f"({cache_stats['hit_rate']:.1f}% hit)"
            )
    
    def _draw(self):
        """Draw everything"""
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Draw header
        self._draw_header()
        
        # Draw lyrics (sprite manager)
        self.sprite_manager.draw(self.screen)
        
        # Draw controls
        self._draw_controls()
        
        # Draw stats if enabled
        if self.show_stats:
            self.stats_label.draw(self.screen)
        
        # Flip buffers
        pygame.display.flip()
    
    def _draw_header(self):
        """Draw header with song info"""
        # Album art
        self.album_art.draw(self.screen)
        
        # Song info
        self.song_title_label.draw(self.screen)
        self.artist_label.draw(self.screen)
        self.album_label.draw(self.screen)
        
        # Separator line
        separator_y = HEADER_HEIGHT - 5
        pygame.draw.line(self.screen, (40, 40, 40), 
                        (20, separator_y), (WINDOW_WIDTH - 20, separator_y), 1)
    
    def _draw_controls(self):
        """Draw control panel"""
        # Separator line
        control_top = WINDOW_HEIGHT - CONTROL_HEIGHT
        pygame.draw.line(self.screen, (40, 40, 40), 
                        (20, control_top), (WINDOW_WIDTH - 20, control_top), 1)
        
        # Progress bar
        self.progress_bar.draw(self.screen)
        
        # Time labels
        self.time_current_label.draw(self.screen)
        self.time_total_label.draw(self.screen)
        
        # Buttons
        self.play_button.draw(self.screen)
        self.prev_button.draw(self.screen)
        self.next_button.draw(self.screen)
        self.transparency_button.draw(self.screen)
        
        # Opacity slider popup (if shown)
        if self.show_opacity_popup:
            # Draw semi-transparent background
            popup_bg = pygame.Surface((110, 210), pygame.SRCALPHA)
            popup_bg.fill((20, 20, 20, 230))
            popup_x = self.window_width - 100
            self.screen.blit(popup_bg, (popup_x - 10, 50))
            
            # Draw slider and label
            self.opacity_slider.draw(self.screen)
            self.opacity_label.draw(self.screen)
    
    # ===== Callbacks =====
    
    def on_progress_update(self, progress_ms: int, duration_ms: int):
        """Called by Spotify controller with progress updates"""
        self.current_progress_ms = progress_ms
        self.current_duration_ms = duration_ms
        
        # Update progress bar
        if duration_ms > 0:
            # Apply timing offset
            from ui.styles import LYRICS_OFFSET_MS
            adjusted_progress = progress_ms - LYRICS_OFFSET_MS
            
            progress = adjusted_progress / duration_ms
            self.progress_bar.set_progress(progress)
            
            # Update time labels
            self.time_current_label.set_text(self._format_time(progress_ms))
            self.time_total_label.set_text(self._format_time(duration_ms))
            
            # Update lyrics highlighting
            if self.timed_lyrics and self.spotify_controller:
                current_index = self.spotify_controller.get_current_line_index(
                    adjusted_progress, self.timed_lyrics
                )
                if current_index >= 0:
                    self.sprite_manager.set_current_line(current_index)
        
        # Check for song change
        if self.spotify_controller:
            track = self.spotify_controller.get_current_track()
            if track:
                track_id = track.get('id')
                if track_id != self.current_song_id:
                    self.current_song_id = track_id
                    self._on_song_changed(track)
    
    def _on_song_changed(self, track: Dict):
        """Handle song change"""
        print(f"[PygameLyricsWindow] Song changed: {track.get('name')}")
        
        # Update UI
        self.song_title_label.set_text(track.get('name', 'Unknown'))
        self.artist_label.set_text(track.get('artists', [{}])[0].get('name', 'Unknown'))
        self.album_label.set_text(track.get('album', {}).get('name', ''))
        
        # Load album art in background thread
        album_art_url = track.get('album', {}).get('images', [{}])[0].get('url')
        if album_art_url:
            threading.Thread(target=self._load_album_art, args=(album_art_url,), 
                           daemon=True).start()
        
        # Fetch lyrics
        if self.lyrics_fetcher:
            artist = track.get('artists', [{}])[0].get('name', '')
            title = track.get('name', '')
            album = track.get('album', {}).get('name', '')
            duration_ms = track.get('duration_ms', 0)
            duration_sec = duration_ms // 1000  # Convert milliseconds to seconds for LRClib
            
            threading.Thread(target=self._fetch_lyrics, 
                           args=(artist, title, album, duration_sec),
                           daemon=True).start()
    
    def _load_album_art(self, url: str):
        """Load album art from URL (runs in thread)"""
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                # Load with Pygame
                image = pygame.image.load(image_data)
                # Update on main thread (Pygame is thread-safe for this)
                self.album_art.set_image(image)
        except Exception as e:
            print(f"[AlbumArt] Error loading: {e}")
    
    def _fetch_lyrics(self, artist: str, title: str, album: str, duration: int):
        """Fetch lyrics (runs in thread)"""
        if not self.lyrics_fetcher:
            print("[Lyrics] No lyrics fetcher available")
            return
        
        try:
            lyrics = self.lyrics_fetcher.fetch_lyrics(artist, title, album, duration)
            
            # Check if synced or plain
            if isinstance(lyrics, list) and len(lyrics) > 0:
                first_item = lyrics[0]
                
                if isinstance(first_item, (tuple, list)) and len(first_item) == 3:
                    # Synced lyrics
                    self.timed_lyrics = [(item[0], item[1], item[2]) for item in lyrics]
                    lines = [item[0] for item in lyrics]
                    print(f"[Lyrics] Loaded {len(lines)} synced lines")
                    
                    # Load into sprite manager
                    self.sprite_manager.load_lyrics(lines)
                
                elif isinstance(first_item, dict):
                    # Plain text lyrics
                    text = first_item.get('text', '')
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    print(f"[Lyrics] Loaded {len(lines)} plain lines")
                    
                    # Calculate timing if we have duration
                    if duration > 0 and self.spotify_controller:
                        self.timed_lyrics = self.spotify_controller.calculate_line_timing(
                            lines, duration
                        )
                    
                    # Load into sprite manager
                    self.sprite_manager.load_lyrics(lines)
        
        except Exception as e:
            print(f"[Lyrics] Error fetching: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_play_pause_clicked(self):
        """Play/pause toggle"""
        if self.spotify_controller:
            if self.is_playing:
                self.spotify_controller.pause()
                self.play_button.text = "▶"
            else:
                self.spotify_controller.play()
                self.play_button.text = "⏸"
            
            self.is_playing = not self.is_playing
    
    def _on_prev_clicked(self):
        """Previous track"""
        if self.spotify_controller:
            self.spotify_controller.previous()
    
    def _on_next_clicked(self):
        """Next track"""
        if self.spotify_controller:
            self.spotify_controller.next()
    
    def _on_progress_scrub(self, progress: float):
        """Progress bar scrubbed"""
        if self.spotify_controller and self.current_duration_ms > 0:
            position_ms = int(progress * self.current_duration_ms)
            self.spotify_controller.seek_to_position(position_ms)
    
    def _on_transparency_clicked(self):
        """Toggle opacity slider popup"""
        self.show_opacity_popup = not self.show_opacity_popup
        print(f"[Window] Opacity popup: {'shown' if self.show_opacity_popup else 'hidden'}")
    
    def _on_opacity_changed(self, value: float):
        """Opacity slider value changed"""
        self.window_opacity = value
        self._set_window_opacity(value)
        self.opacity_label.set_text(f"{int(value * 100)}%")
    
    def _format_time(self, ms: int) -> str:
        """Format milliseconds to MM:SS"""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    def quit(self):
        """Clean up and quit"""
        print("[PygameLyricsWindow] Shutting down")
        pygame.quit()
