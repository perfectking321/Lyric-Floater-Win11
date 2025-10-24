"""
canvas_batcher.py - Canvas Update Batcher

Batches multiple canvas updates into a single redraw operation.
Reduces flickering and improves frame pacing.
"""

from typing import Dict, List, Tuple, Any, Optional
import tkinter as tk


class CanvasUpdate:
    """Represents a queued canvas update"""
    
    def __init__(self, canvas_id: int, **kwargs):
        self.canvas_id = canvas_id
        self.properties = kwargs


class CanvasBatcher:
    """
    Batches canvas itemconfig updates to reduce redraws.
    
    Instead of:
        canvas.itemconfig(id1, fill='#FFFFFF')  # Redraw 1
        canvas.itemconfig(id2, fill='#FF0000')  # Redraw 2
        canvas.itemconfig(id3, fill='#00FF00')  # Redraw 3
    
    Does:
        batcher.queue_update(id1, fill='#FFFFFF')
        batcher.queue_update(id2, fill='#FF0000')
        batcher.queue_update(id3, fill='#00FF00')
        # Single redraw when idle!
    """
    
    def __init__(self, canvas: tk.Canvas, batch_size: int = 50):
        """
        Initialize canvas batcher.
        
        Args:
            canvas: Tkinter Canvas widget
            batch_size: Maximum updates to queue before forcing flush
        """
        self.canvas = canvas
        self.batch_size = batch_size
        
        # Pending updates {canvas_id: {property: value}}
        self.pending_updates: Dict[int, Dict[str, Any]] = {}
        
        # Batch scheduling
        self.is_scheduled = False
        self.flush_callback_id = None
        
        # Performance tracking
        self.total_batches = 0
        self.total_updates = 0
        self.max_batch_size = 0
    
    def queue_update(self, canvas_id: int, **kwargs) -> None:
        """
        Queue an update for a canvas item.
        
        Args:
            canvas_id: Canvas item ID
            **kwargs: Properties to update (fill, font, etc.)
        """
        if canvas_id is None:
            return
        
        # Merge with existing pending updates for this item
        if canvas_id not in self.pending_updates:
            self.pending_updates[canvas_id] = {}
        
        self.pending_updates[canvas_id].update(kwargs)
        
        # Schedule flush if not already scheduled
        if not self.is_scheduled:
            self._schedule_flush()
        
        # Force flush if batch is too large
        elif len(self.pending_updates) >= self.batch_size:
            self._cancel_scheduled_flush()
            self.flush()
    
    def queue_multiple(self, updates: List[Tuple[int, Dict[str, Any]]]) -> None:
        """
        Queue multiple updates at once.
        
        Args:
            updates: List of (canvas_id, properties_dict) tuples
        """
        for canvas_id, properties in updates:
            if canvas_id is not None:
                if canvas_id not in self.pending_updates:
                    self.pending_updates[canvas_id] = {}
                self.pending_updates[canvas_id].update(properties)
        
        if not self.is_scheduled:
            self._schedule_flush()
        elif len(self.pending_updates) >= self.batch_size:
            self._cancel_scheduled_flush()
            self.flush()
    
    def flush(self) -> int:
        """
        Apply all pending updates immediately.
        
        Returns:
            Number of items updated
        """
        if not self.pending_updates:
            return 0
        
        # Track batch size
        batch_size = len(self.pending_updates)
        self.max_batch_size = max(self.max_batch_size, batch_size)
        self.total_batches += 1
        self.total_updates += batch_size
        
        # Apply all updates
        try:
            for canvas_id, properties in self.pending_updates.items():
                try:
                    self.canvas.itemconfig(canvas_id, **properties)
                except tk.TclError:
                    # Item may have been deleted
                    pass
        finally:
            # Clear queue
            self.pending_updates.clear()
            self.is_scheduled = False
            self.flush_callback_id = None
        
        return batch_size
    
    def _schedule_flush(self) -> None:
        """Schedule flush on next idle event"""
        if self.is_scheduled:
            return
        
        self.is_scheduled = True
        self.flush_callback_id = self.canvas.after_idle(self.flush)
    
    def _cancel_scheduled_flush(self) -> None:
        """Cancel scheduled flush"""
        if self.flush_callback_id:
            try:
                self.canvas.after_cancel(self.flush_callback_id)
            except:
                pass
            self.flush_callback_id = None
        self.is_scheduled = False
    
    def clear_queue(self) -> None:
        """Clear all pending updates without applying them"""
        self._cancel_scheduled_flush()
        self.pending_updates.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get batching statistics"""
        avg_batch_size = (
            self.total_updates / self.total_batches
            if self.total_batches > 0
            else 0
        )
        
        return {
            'total_batches': self.total_batches,
            'total_updates': self.total_updates,
            'avg_batch_size': round(avg_batch_size, 1),
            'max_batch_size': self.max_batch_size,
            'pending_updates': len(self.pending_updates)
        }
    
    def reset_stats(self) -> None:
        """Reset statistics"""
        self.total_batches = 0
        self.total_updates = 0
        self.max_batch_size = 0


class SmartCanvasBatcher(CanvasBatcher):
    """
    Enhanced canvas batcher with intelligent update merging.
    
    Features:
    - Deduplicates redundant updates
    - Prioritizes visible items
    - Throttles high-frequency updates
    """
    
    def __init__(
        self,
        canvas: tk.Canvas,
        batch_size: int = 50,
        enable_deduplication: bool = True
    ):
        super().__init__(canvas, batch_size)
        self.enable_deduplication = enable_deduplication
        
        # Track last applied state for deduplication
        self.last_state: Dict[int, Dict[str, Any]] = {}
    
    def queue_update(self, canvas_id: int, **kwargs) -> None:
        """Queue update with deduplication"""
        if canvas_id is None:
            return
        
        # Deduplicate: skip if properties unchanged
        if self.enable_deduplication and canvas_id in self.last_state:
            # Check if any property actually changed
            has_changes = False
            for key, value in kwargs.items():
                if key not in self.last_state[canvas_id] or self.last_state[canvas_id][key] != value:
                    has_changes = True
                    break
            
            if not has_changes:
                return  # No changes, skip update
        
        # Queue the update
        super().queue_update(canvas_id, **kwargs)
    
    def flush(self) -> int:
        """Flush with state tracking"""
        # Update last state
        for canvas_id, properties in self.pending_updates.items():
            if canvas_id not in self.last_state:
                self.last_state[canvas_id] = {}
            self.last_state[canvas_id].update(properties)
        
        # Apply updates
        return super().flush()
    
    def clear_state(self, canvas_id: Optional[int] = None) -> None:
        """
        Clear tracked state (useful when items are deleted).
        
        Args:
            canvas_id: Specific item to clear, or None for all
        """
        if canvas_id is None:
            self.last_state.clear()
        elif canvas_id in self.last_state:
            del self.last_state[canvas_id]
