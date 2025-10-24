"""
color_cache.py - Pre-calculated Color Cache

Dramatically speeds up color opacity calculations by pre-computing
common color/opacity combinations.
"""

from typing import Dict, Tuple


class ColorCache:
    """
    Pre-calculates and caches opacity colors.
    Avoids expensive hex parsing and interpolation every frame.
    """
    
    def __init__(self):
        self.cache: Dict[Tuple[str, float], str] = {}
        self._build_cache()
    
    def _build_cache(self) -> None:
        """Pre-calculate common color/opacity combinations"""
        # Common colors from styles.py
        base_colors = [
            '#FFFFFF',  # White (TEXT_ACTIVE)
            '#6B7280',  # Gray (TEXT_MUTED)
            '#9CA3AF',  # Light gray (TEXT_UPCOMING)
            '#4B5563',  # Dark gray (TEXT_PAST)
            '#D1D5DB',  # Info gray (TEXT_INFO)
            '#FF2D55',  # Highlight pink (HIGHLIGHT_COLOR)
            '#1DB954',  # Spotify green (ACCENT_SECONDARY)
            '#000000',  # Black (BACKGROUND_COLOR)
        ]
        
        # Pre-calculate opacity values from 0.0 to 1.0 in 0.05 steps
        # This gives us 21 opacity levels (plenty for smooth transitions)
        opacities = [i * 0.05 for i in range(21)]  # 0.0, 0.05, 0.10, ..., 1.0
        
        # Build cache
        for base_color in base_colors:
            for opacity in opacities:
                key = (base_color, opacity)
                self.cache[key] = self._calculate_opacity_color(base_color, opacity)
        
        print(f"[ColorCache] Pre-calculated {len(self.cache)} color combinations")
    
    def get_color(self, base_color: str, opacity: float) -> str:
        """
        Get color with opacity applied.
        
        Args:
            base_color: Hex color string (e.g., '#FFFFFF')
            opacity: Opacity value from 0.0 to 1.0
        
        Returns:
            Hex color string with opacity applied
        """
        # Clamp opacity to valid range
        opacity = max(0.0, min(1.0, opacity))
        
        # Round to nearest 0.05 for better cache hit rate
        rounded_opacity = round(opacity * 20) / 20  # Rounds to nearest 0.05
        
        # Check cache
        key = (base_color, rounded_opacity)
        if key in self.cache:
            return self.cache[key]
        
        # Cache miss - calculate and store
        result = self._calculate_opacity_color(base_color, opacity)
        self.cache[key] = result
        return result
    
    def _calculate_opacity_color(self, base_color: str, opacity: float) -> str:
        """
        Calculate color with opacity applied (expensive operation).
        
        This method does the actual color interpolation.
        Called only on cache misses.
        """
        # Handle edge cases
        if opacity <= 0.0:
            return '#000000'
        if opacity >= 1.0:
            return base_color
        
        # Parse hex color
        if not base_color.startswith('#'):
            base_color = '#' + base_color
        
        if len(base_color) != 7:
            return base_color  # Invalid format, return as-is
        
        try:
            # Extract RGB components
            r = int(base_color[1:3], 16)
            g = int(base_color[3:5], 16)
            b = int(base_color[5:7], 16)
            
            # Apply opacity (interpolate towards black)
            r = int(r * opacity)
            g = int(g * opacity)
            b = int(b * opacity)
            
            # Clamp values
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            # Convert back to hex
            return f'#{r:02x}{g:02x}{b:02x}'
        
        except (ValueError, IndexError):
            # Invalid color format
            return base_color
    
    def get_interpolated_color(
        self,
        color1: str,
        color2: str,
        progress: float
    ) -> str:
        """
        Interpolate between two colors.
        
        Args:
            color1: Start color (hex)
            color2: End color (hex)
            progress: Interpolation progress (0.0 to 1.0)
        
        Returns:
            Interpolated color (hex)
        """
        # Clamp progress
        progress = max(0.0, min(1.0, progress))
        
        # Handle edge cases
        if progress <= 0.0:
            return color1
        if progress >= 1.0:
            return color2
        
        # Round progress for caching
        rounded_progress = round(progress * 20) / 20
        
        # Check cache
        key = (f'{color1}_{color2}', rounded_progress)
        if key in self.cache:
            return self.cache[key]
        
        # Parse colors
        try:
            r1 = int(color1[1:3], 16)
            g1 = int(color1[3:5], 16)
            b1 = int(color1[5:7], 16)
            
            r2 = int(color2[1:3], 16)
            g2 = int(color2[3:5], 16)
            b2 = int(color2[5:7], 16)
            
            # Interpolate
            r = int(r1 + (r2 - r1) * progress)
            g = int(g1 + (g2 - g1) * progress)
            b = int(b1 + (b2 - b1) * progress)
            
            # Clamp and convert
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            result = f'#{r:02x}{g:02x}{b:02x}'
            
            # Cache result
            self.cache[key] = result
            return result
        
        except (ValueError, IndexError):
            return color1
    
    def clear_cache(self) -> None:
        """Clear the cache and rebuild"""
        self.cache.clear()
        self._build_cache()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'total_entries': len(self.cache),
            'memory_bytes': len(self.cache) * 40  # Rough estimate
        }
    
    def warm_up_colors(self, colors: list) -> None:
        """
        Pre-calculate additional colors for better cache hits.
        
        Args:
            colors: List of hex color strings to pre-calculate
        """
        opacities = [i * 0.05 for i in range(21)]
        
        for color in colors:
            for opacity in opacities:
                key = (color, opacity)
                if key not in self.cache:
                    self.cache[key] = self._calculate_opacity_color(color, opacity)
        
        print(f"[ColorCache] Warmed up {len(colors)} additional colors")


# Utility function for quick color operations
def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple"""
    if not hex_color.startswith('#'):
        hex_color = '#' + hex_color
    
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    
    return (r, g, b)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB tuple to hex color"""
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    
    return f'#{r:02x}{g:02x}{b:02x}'
