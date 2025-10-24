"""
animation_manager.py - Master Animation Controller

Coordinates all animations in a single 60 FPS loop.
Replaces multiple uncoordinated timers with one synchronized loop.
"""

import time
from typing import Dict, Callable, Optional, Any


class AnimationState:
    """Represents a single animation's state"""
    
    def __init__(
        self,
        duration_ms: float,
        start_value: float,
        end_value: float,
        easing_func: Optional[Callable[[float], float]] = None,
        on_update: Optional[Callable[[float], None]] = None,
        on_complete: Optional[Callable[[], None]] = None
    ):
        self.duration_ms = duration_ms
        self.start_value = start_value
        self.end_value = end_value
        self.easing_func = easing_func or self._ease_in_out_cubic
        self.on_update = on_update
        self.on_complete = on_complete
        
        self.start_time = time.time() * 1000
        self.is_complete = False
        self.current_value = start_value
    
    def update(self, current_time_ms: float) -> float:
        """Update animation state and return current value"""
        if self.is_complete:
            return self.current_value
        
        # Calculate progress (0.0 to 1.0)
        elapsed = current_time_ms - self.start_time
        progress = min(1.0, elapsed / self.duration_ms)
        
        # Apply easing
        eased_progress = self.easing_func(progress)
        
        # Calculate current value
        self.current_value = self.start_value + (self.end_value - self.start_value) * eased_progress
        
        # Call update callback
        if self.on_update:
            self.on_update(self.current_value)
        
        # Check if complete
        if progress >= 1.0:
            self.is_complete = True
            self.current_value = self.end_value
            if self.on_complete:
                self.on_complete()
        
        return self.current_value
    
    @staticmethod
    def _ease_in_out_cubic(t: float) -> float:
        """Smooth easing function (cubic)"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            p = 2 * t - 2
            return 1 + p * p * p / 2


class MultiPropertyAnimation:
    """Animation that updates multiple properties simultaneously"""
    
    def __init__(
        self,
        duration_ms: float,
        properties: Dict[str, tuple],  # {prop_name: (start, end)}
        easing_func: Optional[Callable[[float], float]] = None,
        on_update: Optional[Callable[[Dict[str, float]], None]] = None,
        on_complete: Optional[Callable[[], None]] = None
    ):
        self.duration_ms = duration_ms
        self.properties = properties
        self.easing_func = easing_func or AnimationState._ease_in_out_cubic
        self.on_update = on_update
        self.on_complete = on_complete
        
        self.start_time = time.time() * 1000
        self.is_complete = False
        self.current_values = {prop: start for prop, (start, end) in properties.items()}
    
    def update(self, current_time_ms: float) -> Dict[str, float]:
        """Update all properties and return current values"""
        if self.is_complete:
            return self.current_values
        
        # Calculate progress (0.0 to 1.0)
        elapsed = current_time_ms - self.start_time
        progress = min(1.0, elapsed / self.duration_ms)
        
        # Apply easing
        eased_progress = self.easing_func(progress)
        
        # Calculate current values for all properties
        for prop_name, (start_value, end_value) in self.properties.items():
            self.current_values[prop_name] = start_value + (end_value - start_value) * eased_progress
        
        # Call update callback
        if self.on_update:
            self.on_update(self.current_values)
        
        # Check if complete
        if progress >= 1.0:
            self.is_complete = True
            # Set final values
            for prop_name, (start_value, end_value) in self.properties.items():
                self.current_values[prop_name] = end_value
            if self.on_complete:
                self.on_complete()
        
        return self.current_values


class AnimationManager:
    """
    Master animation controller running at 60 FPS.
    Coordinates all animations in a single synchronized loop.
    """
    
    def __init__(self, root, fps: int = 60):
        self.root = root
        self.fps = fps
        self.frame_time_ms = 1000.0 / fps  # ~16.67ms for 60 FPS
        
        self.animations: Dict[str, Any] = {}  # {id: AnimationState or MultiPropertyAnimation}
        self.is_running = False
        self.frame_count = 0
        self.last_frame_time = 0
        
        # Performance metrics
        self.frame_times = []
        self.max_frame_time = 0
    
    def add_animation(
        self,
        anim_id: str,
        animation: Any,  # AnimationState or MultiPropertyAnimation
        replace_existing: bool = True
    ) -> None:
        """
        Add an animation to the manager.
        
        Args:
            anim_id: Unique identifier for this animation
            animation: AnimationState or MultiPropertyAnimation instance
            replace_existing: If True, stops existing animation with same ID
        """
        if anim_id in self.animations and replace_existing:
            # Complete the old animation before replacing
            old_anim = self.animations[anim_id]
            old_anim.is_complete = True
        
        self.animations[anim_id] = animation
        
        # Start the loop if not running
        if not self.is_running:
            self.start()
    
    def remove_animation(self, anim_id: str) -> None:
        """Remove an animation from the manager"""
        if anim_id in self.animations:
            del self.animations[anim_id]
    
    def stop_all_animations(self) -> None:
        """Stop and clear all animations"""
        self.animations.clear()
    
    def start(self) -> None:
        """Start the master animation loop"""
        if self.is_running:
            return
        
        self.is_running = True
        self.last_frame_time = time.time() * 1000
        self._animation_loop()
    
    def stop(self) -> None:
        """Stop the master animation loop"""
        self.is_running = False
    
    def _animation_loop(self) -> None:
        """Main animation loop - runs at target FPS"""
        if not self.is_running:
            return
        
        # Calculate frame timing
        current_time = time.time() * 1000
        frame_delta = current_time - self.last_frame_time
        
        # Track performance
        if len(self.frame_times) > 100:
            self.frame_times.pop(0)
        self.frame_times.append(frame_delta)
        self.max_frame_time = max(self.max_frame_time, frame_delta)
        
        # Update all active animations
        completed_animations = []
        
        # Create a copy of items to avoid "dictionary changed size during iteration" error
        for anim_id, animation in list(self.animations.items()):
            animation.update(current_time)
            
            if animation.is_complete:
                completed_animations.append(anim_id)
        
        # Remove completed animations
        for anim_id in completed_animations:
            self.remove_animation(anim_id)
        
        # Update frame metrics
        self.frame_count += 1
        self.last_frame_time = current_time
        
        # Calculate time to next frame
        processing_time = (time.time() * 1000) - current_time
        time_to_next_frame = max(1, int(self.frame_time_ms - processing_time))
        
        # Schedule next frame
        self.root.after(time_to_next_frame, self._animation_loop)
    
    def get_performance_stats(self) -> Dict[str, float]:
        """Get performance statistics"""
        if not self.frame_times:
            return {
                'avg_frame_time': 0,
                'max_frame_time': 0,
                'current_fps': 0,
                'active_animations': 0
            }
        
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        current_fps = 1000.0 / avg_frame_time if avg_frame_time > 0 else 0
        
        return {
            'avg_frame_time': round(avg_frame_time, 2),
            'max_frame_time': round(self.max_frame_time, 2),
            'current_fps': round(current_fps, 1),
            'active_animations': len(self.animations)
        }
    
    def reset_performance_stats(self) -> None:
        """Reset performance tracking"""
        self.frame_times.clear()
        self.max_frame_time = 0
        self.frame_count = 0


# Easing functions library
class Easing:
    """Collection of easing functions for animations"""
    
    @staticmethod
    def linear(t: float) -> float:
        """No easing"""
        return t
    
    @staticmethod
    def ease_in_quad(t: float) -> float:
        """Quadratic ease-in"""
        return t * t
    
    @staticmethod
    def ease_out_quad(t: float) -> float:
        """Quadratic ease-out"""
        return t * (2 - t)
    
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """Quadratic ease-in-out"""
        return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t
    
    @staticmethod
    def ease_in_cubic(t: float) -> float:
        """Cubic ease-in"""
        return t * t * t
    
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Cubic ease-out"""
        return (t - 1) * (t - 1) * (t - 1) + 1
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """Cubic ease-in-out (smooth)"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            p = 2 * t - 2
            return 1 + p * p * p / 2
    
    @staticmethod
    def ease_out_elastic(t: float) -> float:
        """Elastic ease-out (bouncy)"""
        if t == 0 or t == 1:
            return t
        
        import math
        p = 0.3
        s = p / 4
        return math.pow(2, -10 * t) * math.sin((t - s) * (2 * math.pi) / p) + 1
    
    @staticmethod
    def ease_out_back(t: float) -> float:
        """Back ease-out (slight overshoot)"""
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)
