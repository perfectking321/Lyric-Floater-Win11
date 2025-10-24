"""
Animation utilities for smooth UI transitions
"""
import time
from typing import Callable, Any, Optional


class AnimationEngine:
    """Handles smooth property animations with various easing functions"""
    
    def __init__(self, root):
        self.root = root
        self.active_animations = {}
        self.animation_id_counter = 0
    
    def animate_property(self, start_val: float, end_val: float, duration_ms: int, 
                        callback: Callable[[float], None], 
                        easing: str = "ease-in-out",
                        on_complete: Callable[[], None] | None = None) -> int:
        """
        Smoothly interpolate between values over duration
        
        Args:
            start_val: Starting value
            end_val: Ending value
            duration_ms: Animation duration in milliseconds
            callback: Function called with current value each frame
            easing: Easing function ("linear", "ease-in", "ease-out", "ease-in-out")
            on_complete: Optional callback when animation completes
            
        Returns:
            Animation ID that can be used to cancel the animation
        """
        animation_id = self.animation_id_counter
        self.animation_id_counter += 1
        
        start_time = time.time() * 1000  # Convert to milliseconds
        frames_per_second = 60
        frame_duration = 1000 / frames_per_second
        
        def animate_frame():
            if animation_id not in self.active_animations:
                return  # Animation was cancelled
                
            current_time = time.time() * 1000
            elapsed = current_time - start_time
            progress = min(elapsed / duration_ms, 1.0)
            
            # Apply easing function
            eased_progress = self._apply_easing(progress, easing)
            
            # Calculate current value
            current_val = start_val + (end_val - start_val) * eased_progress
            
            # Call the callback with current value
            try:
                callback(current_val)
            except Exception as e:
                print(f"Animation callback error: {e}")
            
            # Continue animation or complete
            if progress < 1.0:
                self.active_animations[animation_id] = self.root.after(
                    int(frame_duration), animate_frame
                )
            else:
                if animation_id in self.active_animations:
                    del self.active_animations[animation_id]
                if on_complete:
                    try:
                        on_complete()
                    except Exception as e:
                        print(f"Animation complete callback error: {e}")
        
        self.active_animations[animation_id] = self.root.after(
            int(frame_duration), animate_frame
        )
        return animation_id
    
    def cancel_animation(self, animation_id: int):
        """Cancel an active animation"""
        if animation_id in self.active_animations:
            self.root.after_cancel(self.active_animations[animation_id])
            del self.active_animations[animation_id]
    
    def cancel_all_animations(self):
        """Cancel all active animations"""
        for animation_id in list(self.active_animations.keys()):
            self.cancel_animation(animation_id)
    
    def _apply_easing(self, t: float, easing: str) -> float:
        """Apply easing function to progress value (0.0 to 1.0)"""
        if easing == "linear":
            return t
        elif easing == "ease-in":
            return t * t
        elif easing == "ease-out":
            return t * (2 - t)
        elif easing == "ease-in-out":
            if t < 0.5:
                return 2 * t * t
            else:
                return -1 + (4 - 2 * t) * t
        else:
            return t  # Default to linear


def interpolate_color(color1: str, color2: str, progress: float) -> str:
    """
    Interpolate between two hex colors
    
    Args:
        color1: Starting color (hex string like "#FF0000")
        color2: Ending color (hex string)
        progress: Progress from 0.0 to 1.0
        
    Returns:
        Interpolated color as hex string
    """
    # Remove # if present
    c1 = color1.lstrip('#')
    c2 = color2.lstrip('#')
    
    # Convert to RGB
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    
    # Interpolate
    r = int(r1 + (r2 - r1) * progress)
    g = int(g1 + (g2 - g1) * progress)
    b = int(b1 + (b2 - b1) * progress)
    
    # Convert back to hex
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> tuple:
    """
    Convert hex color to RGBA tuple
    
    Args:
        hex_color: Hex color string like "#FF0000"
        alpha: Alpha value (0.0 to 1.0)
        
    Returns:
        RGBA tuple (r, g, b, a) with values 0-255 for RGB and 0-1 for A
    """
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b, alpha)


def calculate_opacity_for_line(current_line_index: int, line_index: int, 
                               total_lines: int) -> float:
    """
    Calculate opacity for a lyric line based on its position relative to current line
    
    Args:
        current_line_index: Index of currently playing line
        line_index: Index of the line to calculate opacity for
        total_lines: Total number of lines
        
    Returns:
        Opacity value from 0.0 to 1.0
    """
    distance = line_index - current_line_index
    
    if distance == 0:
        # Current line - full opacity
        return 1.0
    elif distance > 0 and distance <= 3:
        # Upcoming lines - decreasing opacity
        opacities = [0.7, 0.5, 0.3]
        return opacities[distance - 1] if distance - 1 < len(opacities) else 0.2
    elif distance < 0 and distance >= -2:
        # Previous lines - low opacity
        return 0.4
    else:
        # Far away lines
        return 0.2


def ease_in_out_cubic(t: float) -> float:
    """Cubic ease-in-out function"""
    if t < 0.5:
        return 4 * t * t * t
    else:
        p = 2 * t - 2
        return 1 + p * p * p / 2


def ease_out_expo(t: float) -> float:
    """Exponential ease-out function"""
    if t == 1:
        return 1
    return 1 - pow(2, -10 * t)
