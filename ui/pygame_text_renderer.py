"""
Pygame Text Renderer - Hardware-accelerated text rendering with caching
"""
import pygame
import os
from typing import Tuple, Dict, List, Union
from ui.styles import *


class TextRenderer:
    """Manages text rendering with caching and GPU acceleration"""
    
    def __init__(self):
        pygame.font.init()
        
        # Font cache
        self.fonts = {}
        self._init_fonts()
        
        # Rendered text cache: {(text, size, color, bold): surface}
        self.text_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Pre-calculated color cache for opacity levels
        self.color_cache = self._build_color_cache()
    
    def _init_fonts(self):
        """Initialize all font sizes with system font"""
        try:
            # Try fonts in order of Unicode support (best to worst)
            font_candidates = [
                ('nirmalaui', 'Nirmala UI (Best Hindi support)'),  # Windows 10+ Hindi font
                ('segoeui', 'Segoe UI (Standard)'),                 # Fallback to Segoe UI
                ('arial', 'Arial (Universal fallback)'),            # Arial has good Unicode
            ]
            
            font_path = None
            font_name = 'Unknown'
            
            for candidate, description in font_candidates:
                try:
                    test_path = pygame.font.match_font(candidate)
                    if test_path and os.path.exists(test_path):
                        # Avoid Light variants (limited Unicode)
                        if 'light' not in test_path.lower():
                            font_path = test_path
                            font_name = description
                            break
                except:
                    continue
            
            if not font_path:
                # Last resort: system default
                font_path = pygame.font.get_default_font()
                font_name = 'System Default'
            
            # Create fonts for different sizes
            self.fonts['small'] = pygame.font.Font(font_path, FONT_SIZE_SMALL)
            self.fonts['normal'] = pygame.font.Font(font_path, FONT_SIZE)
            self.fonts['current'] = pygame.font.Font(font_path, FONT_SIZE_CURRENT)
            self.fonts['title'] = pygame.font.Font(font_path, FONT_SIZE_TITLE)
            self.fonts['info'] = pygame.font.Font(font_path, FONT_SIZE_INFO)
            
            print(f"[TextRenderer] ✅ Loaded {font_name}")
            print(f"[TextRenderer]    Path: {font_path}")
            
        except Exception as e:
            print(f"[TextRenderer] ⚠️ Error loading fonts: {e}")
            # Ultimate fallback
            self.fonts['small'] = pygame.font.Font(None, FONT_SIZE_SMALL)
            self.fonts['normal'] = pygame.font.Font(None, FONT_SIZE)
            self.fonts['current'] = pygame.font.Font(None, FONT_SIZE_CURRENT)
            self.fonts['title'] = pygame.font.Font(None, FONT_SIZE_TITLE)
            self.fonts['info'] = pygame.font.Font(None, FONT_SIZE_INFO)
            print(f"[TextRenderer]    Using built-in default font")
    
    def _build_color_cache(self) -> Dict[float, Tuple[int, int, int]]:
        """Pre-calculate colors for all opacity levels"""
        cache = {}
        base_color = self._hex_to_rgb(TEXT_COLOR)
        
        # Cache opacity levels from 0.0 to 1.0 in 0.05 steps
        for i in range(21):  # 0.0, 0.05, 0.10, ..., 1.0
            opacity = i / 20.0
            cache[opacity] = self._apply_opacity(base_color, opacity)
        
        print(f"[TextRenderer] Built color cache with {len(cache)} entries")
        return cache
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)
    
    def _apply_opacity(self, rgb: Tuple[int, int, int], opacity: float) -> Tuple[int, int, int]:
        """Apply opacity to RGB color"""
        r, g, b = rgb
        return (int(r * opacity), int(g * opacity), int(b * opacity))
    
    def get_color_for_opacity(self, opacity: float) -> Tuple[int, int, int]:
        """Get cached color for opacity level (rounded to nearest 0.05)"""
        rounded_opacity = round(opacity * 20) / 20  # Round to nearest 0.05
        return self.color_cache.get(rounded_opacity, self._hex_to_rgb(TEXT_COLOR))
    
    def render_text(self, text: str, font_key: str, color: Tuple[int, int, int], 
                   antialias: bool = True) -> pygame.Surface:
        """Render text with caching"""
        cache_key = (text, font_key, color, antialias)
        
        if cache_key in self.text_cache:
            self.cache_hits += 1
            return self.text_cache[cache_key]
        
        self.cache_misses += 1
        
        # Render new text
        font = self.fonts.get(font_key, self.fonts['normal'])
        surface = font.render(text, antialias, color)
        
        # Cache it
        self.text_cache[cache_key] = surface
        
        # Limit cache size
        if len(self.text_cache) > 500:
            # Remove oldest 100 entries
            keys_to_remove = list(self.text_cache.keys())[:100]
            for key in keys_to_remove:
                del self.text_cache[key]
        
        return surface
    
    def measure_text(self, text: str, font_key: str) -> Tuple[int, int]:
        """Get text dimensions without rendering"""
        font = self.fonts.get(font_key, self.fonts['normal'])
        return font.size(text)
    
    def clear_cache(self):
        """Clear text cache"""
        self.text_cache.clear()
        print(f"[TextRenderer] Cache cleared (hits: {self.cache_hits}, misses: {self.cache_misses})")
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_cache_stats(self) -> Dict[str, Union[int, float]]:
        """Get cache statistics"""
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total > 0 else 0
        
        return {
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'total': total,
            'hit_rate': hit_rate,
            'cache_size': len(self.text_cache)
        }


class TextLayout:
    """Handles text layout and line wrapping"""
    
    def __init__(self, renderer: TextRenderer):
        self.renderer = renderer
    
    def wrap_text(self, text: str, max_width: int, font_key: str) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            width, _ = self.renderer.measure_text(test_line, font_key)
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def center_text_position(self, text: str, font_key: str, 
                           container_width: int, y: int) -> Tuple[int, int]:
        """Calculate centered position for text"""
        width, height = self.renderer.measure_text(text, font_key)
        x = (container_width - width) // 2
        return (x, y)
