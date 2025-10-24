"""
virtual_scroller.py - Virtual Scrolling for Lyrics

Only renders visible lines + buffer, dramatically improving performance
for long songs with 50+ lyric lines.
"""

from typing import List, Dict, Optional, Tuple, Any
import tkinter as tk


class LyricLine:
    """Represents a single lyric line with metadata"""
    
    def __init__(
        self,
        index: int,
        text: str,
        y_position: float,
        canvas_id: Optional[int] = None,
        is_current: bool = False
    ):
        self.index = index
        self.text = text
        self.y_position = y_position
        self.canvas_id = canvas_id
        self.is_current = is_current
        self.opacity = 0.4  # Default opacity
        self.font_size = 14  # Default font size


class VirtualScroller:
    """
    Renders only visible lyric lines for optimal performance.
    
    Key optimizations:
    - Only creates canvas items for visible lines
    - Maintains a buffer of lines above/below viewport
    - Recycles canvas items when scrolling
    - Tracks which lines need updates
    """
    
    def __init__(
        self,
        canvas: tk.Canvas,
        window_width: int = 500,
        window_height: int = 600,
        line_height: float = 40.0,
        buffer_lines: int = 3
    ):
        """
        Initialize virtual scroller.
        
        Args:
            canvas: Tkinter Canvas widget
            window_width: Width of the viewport
            window_height: Height of the viewport
            line_height: Height of each lyric line
            buffer_lines: Extra lines to render above/below viewport
        """
        self.canvas = canvas
        self.window_width = window_width
        self.window_height = window_height
        self.line_height = line_height
        self.buffer_lines = buffer_lines
        
        # All lyric lines (data only, not rendered)
        self.all_lines: List[LyricLine] = []
        
        # Currently rendered lines {index: LyricLine}
        self.visible_lines: Dict[int, LyricLine] = {}
        
        # Viewport state
        self.viewport_y = 0.0  # Current scroll position
        self.total_content_height = 0.0
        
        # Performance tracking
        self.render_count = 0
        self.last_visible_range = (0, 0)
    
    def set_lyrics(self, lyrics_text: List[str]) -> None:
        """
        Set all lyric lines (doesn't render yet).
        
        Args:
            lyrics_text: List of lyric text strings
        """
        # Clear existing lines
        self.clear()
        
        # Create LyricLine objects
        self.all_lines = []
        for i, text in enumerate(lyrics_text):
            y_pos = i * self.line_height
            line = LyricLine(
                index=i,
                text=text,
                y_position=y_pos
            )
            self.all_lines.append(line)
        
        # Calculate total height
        self.total_content_height = len(self.all_lines) * self.line_height
        
        # Initial render
        self.update_viewport(self.viewport_y)
        
        print(f"[VirtualScroller] Set {len(self.all_lines)} lines, total height: {self.total_content_height}px")
    
    def update_viewport(self, scroll_y: float) -> None:
        """
        Update viewport position and render visible lines.
        
        Args:
            scroll_y: Y position of the viewport (pixels from top)
        """
        self.viewport_y = scroll_y
        
        # Calculate visible range
        first_visible, last_visible = self._calculate_visible_range()
        
        # Only update if range changed
        if (first_visible, last_visible) != self.last_visible_range:
            self._update_visible_lines(first_visible, last_visible)
            self.last_visible_range = (first_visible, last_visible)
    
    def _calculate_visible_range(self) -> Tuple[int, int]:
        """
        Calculate which line indices are visible in viewport.
        
        Returns:
            (first_index, last_index) tuple
        """
        if not self.all_lines:
            return (0, 0)
        
        # Calculate visible range with buffer
        first_visible = int(self.viewport_y / self.line_height) - self.buffer_lines
        last_visible = int((self.viewport_y + self.window_height) / self.line_height) + self.buffer_lines + 1
        
        # Clamp to valid range
        first_visible = max(0, first_visible)
        last_visible = min(len(self.all_lines), last_visible)
        
        return (first_visible, last_visible)
    
    def _update_visible_lines(self, start_idx: int, end_idx: int) -> None:
        """
        Update rendered lines to match visible range.
        
        Args:
            start_idx: First visible line index
            end_idx: Last visible line index (exclusive)
        """
        # Remove lines outside visible range
        lines_to_remove = []
        for idx in self.visible_lines.keys():
            if idx < start_idx or idx >= end_idx:
                lines_to_remove.append(idx)
        
        for idx in lines_to_remove:
            self._remove_line(idx)
        
        # Add lines inside visible range
        for idx in range(start_idx, end_idx):
            if idx not in self.visible_lines and idx < len(self.all_lines):
                self._add_line(idx)
        
        self.render_count += 1
    
    def _add_line(self, index: int) -> None:
        """
        Create and render a lyric line.
        
        Args:
            index: Line index to add
        """
        if index >= len(self.all_lines):
            return
        
        line = self.all_lines[index]
        
        # Create canvas text item
        canvas_id = self.canvas.create_text(
            self.window_width / 2,
            line.y_position,
            text=line.text,
            font=('Segoe UI', int(line.font_size)),
            fill=self._opacity_to_color('#FFFFFF', line.opacity),
            anchor='center',
            width=self.window_width - 80  # Padding
        )
        
        line.canvas_id = canvas_id
        self.visible_lines[index] = line
    
    def _remove_line(self, index: int) -> None:
        """
        Remove a rendered line.
        
        Args:
            index: Line index to remove
        """
        if index in self.visible_lines:
            line = self.visible_lines[index]
            if line.canvas_id:
                self.canvas.delete(line.canvas_id)
            del self.visible_lines[index]
    
    def update_line_visual(
        self,
        index: int,
        opacity: Optional[float] = None,
        font_size: Optional[int] = None,
        color: Optional[str] = None,
        is_current: Optional[bool] = None
    ) -> None:
        """
        Update visual properties of a line.
        
        Args:
            index: Line index to update
            opacity: New opacity (0.0 to 1.0)
            font_size: New font size
            color: New color (hex)
            is_current: Whether this is the current line
        """
        if index >= len(self.all_lines):
            return
        
        line = self.all_lines[index]
        
        # Update line properties
        if opacity is not None:
            line.opacity = opacity
        if font_size is not None:
            line.font_size = font_size
        if is_current is not None:
            line.is_current = is_current
        
        # Update canvas item if visible
        if index in self.visible_lines and line.canvas_id:
            updates = {}
            
            if color:
                updates['fill'] = color
            elif opacity is not None:
                updates['fill'] = self._opacity_to_color('#FFFFFF', opacity)
            
            if font_size is not None:
                updates['font'] = ('Segoe UI', int(font_size))
            
            if updates:
                self.canvas.itemconfig(line.canvas_id, **updates)
    
    def get_line_canvas_id(self, index: int) -> Optional[int]:
        """
        Get canvas ID for a line (if visible).
        
        Args:
            index: Line index
            
        Returns:
            Canvas ID or None if not visible
        """
        if index in self.visible_lines:
            return self.visible_lines[index].canvas_id
        return None
    
    def get_line_position(self, index: int) -> float:
        """
        Get Y position of a line.
        
        Args:
            index: Line index
            
        Returns:
            Y position in pixels
        """
        if index < len(self.all_lines):
            return self.all_lines[index].y_position
        return 0.0
    
    def scroll_to_line(self, index: int, align: str = 'center') -> float:
        """
        Calculate scroll position to show a specific line.
        
        Args:
            index: Line index to scroll to
            align: 'top', 'center', or 'bottom'
            
        Returns:
            Target scroll Y position
        """
        if index >= len(self.all_lines):
            return self.viewport_y
        
        line_y = self.all_lines[index].y_position
        
        if align == 'center':
            # Center the line in viewport
            target_y = line_y - (self.window_height / 2) + (self.line_height / 2)
        elif align == 'top':
            # Align to top of viewport
            target_y = line_y
        elif align == 'bottom':
            # Align to bottom of viewport
            target_y = line_y - self.window_height + self.line_height
        else:
            target_y = line_y - (self.window_height / 2)
        
        # Clamp to valid scroll range
        max_scroll = max(0, self.total_content_height - self.window_height)
        target_y = max(0, min(max_scroll, target_y))
        
        return target_y
    
    def clear(self) -> None:
        """Clear all lines"""
        # Remove all visible lines
        for idx in list(self.visible_lines.keys()):
            self._remove_line(idx)
        
        # Clear data
        self.all_lines.clear()
        self.visible_lines.clear()
        self.viewport_y = 0.0
        self.total_content_height = 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        visible_count = len(self.visible_lines)
        total_count = len(self.all_lines)
        reduction = (1 - visible_count / max(1, total_count)) * 100
        
        return {
            'total_lines': total_count,
            'visible_lines': visible_count,
            'reduction_percent': round(reduction, 1),
            'render_count': self.render_count,
            'viewport_y': round(self.viewport_y, 1),
            'total_height': round(self.total_content_height, 1)
        }
    
    @staticmethod
    def _opacity_to_color(base_color: str, opacity: float) -> str:
        """
        Convert base color with opacity to hex color.
        (Simple version - will be replaced with ColorCache in integration)
        
        Args:
            base_color: Base hex color
            opacity: Opacity (0.0 to 1.0)
            
        Returns:
            Hex color with opacity applied
        """
        if opacity >= 1.0:
            return base_color
        if opacity <= 0.0:
            return '#000000'
        
        # Parse hex
        r = int(base_color[1:3], 16)
        g = int(base_color[3:5], 16)
        b = int(base_color[5:7], 16)
        
        # Apply opacity
        r = int(r * opacity)
        g = int(g * opacity)
        b = int(b * opacity)
        
        return f'#{r:02x}{g:02x}{b:02x}'
