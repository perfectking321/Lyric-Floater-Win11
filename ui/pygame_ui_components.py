"""
Pygame UI Components - Buttons, Progress Bar, etc.
"""
import pygame
from typing import Callable, Optional, Tuple
from ui.styles import *


class Button:
    """Pygame button with hover effects"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 font: pygame.font.Font, callback: Optional[Callable] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.callback = callback
        
        # Colors
        self.bg_color = self._hex_to_rgb(SECONDARY_COLOR)
        self.hover_color = self._hex_to_rgb(BUTTON_HOVER_COLOR)
        self.text_color = self._hex_to_rgb(TEXT_COLOR)
        
        # State
        self.is_hovered = False
        self.is_pressed = False
        
        # Render text once
        self.text_surface = font.render(text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        hex_color = hex_color.lstrip('#')
        return (int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events, return True if clicked"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            return False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                self.is_pressed = True
                return False
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_pressed and self.is_hovered:
                self.is_pressed = False
                if self.callback:
                    self.callback()
                return True
            self.is_pressed = False
        
        return False
    
    def draw(self, surface: pygame.Surface):
        """Draw button"""
        # Background
        color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.rect(surface, color, self.rect, border_radius=BORDER_RADIUS)
        
        # Text
        surface.blit(self.text_surface, self.text_rect)


class ImageButton(Button):
    """Button with icon instead of text"""
    
    def __init__(self, x: int, y: int, size: int, icon_surface: pygame.Surface,
                 callback: Optional[Callable] = None):
        self.rect = pygame.Rect(x, y, size, size)
        self.icon = pygame.transform.scale(icon_surface, (size - 20, size - 20))
        self.icon_rect = self.icon.get_rect(center=self.rect.center)
        self.callback = callback
        
        # Colors
        self.bg_color = self._hex_to_rgb(SECONDARY_COLOR)
        self.hover_color = self._hex_to_rgb(BUTTON_HOVER_COLOR)
        
        # State
        self.is_hovered = False
        self.is_pressed = False
    
    def _hex_to_rgb(self, hex_color: str):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def draw(self, surface: pygame.Surface):
        """Draw button with icon"""
        # Background circle
        color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.circle(surface, color, self.rect.center, self.rect.width // 2)
        
        # Icon
        surface.blit(self.icon, self.icon_rect)


class ProgressBar:
    """Progress bar with scrubbing support"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 on_scrub: Optional[Callable[[float], None]] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.on_scrub = on_scrub
        
        # Colors
        self.bg_color = self._hex_to_rgb(PROGRESS_BG)
        self.fg_color = self._hex_to_rgb(PROGRESS_COLOR)
        
        # State
        self.progress = 0.0  # 0.0 to 1.0
        self.is_dragging = False
        self.is_hovered = False
    
    def _hex_to_rgb(self, hex_color: str):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            
            if self.is_dragging:
                # Calculate progress from mouse position
                x = event.pos[0] - self.rect.x
                self.progress = max(0.0, min(1.0, x / self.rect.width))
                if self.on_scrub:
                    self.on_scrub(self.progress)
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                self.is_dragging = True
                # Immediate scrub
                x = event.pos[0] - self.rect.x
                self.progress = max(0.0, min(1.0, x / self.rect.width))
                if self.on_scrub:
                    self.on_scrub(self.progress)
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                was_dragging = self.is_dragging
                self.is_dragging = False
                return was_dragging
        
        return False
    
    def set_progress(self, progress: float):
        """Set progress value (0.0 to 1.0)"""
        if not self.is_dragging:
            self.progress = max(0.0, min(1.0, progress))
    
    def draw(self, surface: pygame.Surface):
        """Draw progress bar"""
        # Background
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=2)
        
        # Foreground (progress)
        if self.progress > 0:
            progress_width = int(self.rect.width * self.progress)
            progress_rect = pygame.Rect(self.rect.x, self.rect.y, progress_width, self.rect.height)
            pygame.draw.rect(surface, self.fg_color, progress_rect, border_radius=2)


class Label:
    """Simple text label"""
    
    def __init__(self, x: int, y: int, text: str, font: pygame.font.Font, 
                 color: str = TEXT_COLOR, centered: bool = False):
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.color = self._hex_to_rgb(color)
        self.centered = centered
        
        # Render
        self.surface = font.render(text, True, self.color)
        self.rect = self.surface.get_rect()
        
        if centered:
            self.rect.centerx = x
            self.rect.y = y
        else:
            self.rect.x = x
            self.rect.y = y
    
    def _hex_to_rgb(self, hex_color: str):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def set_text(self, text: str):
        """Update label text"""
        if text != self.text:
            self.text = text
            self.surface = self.font.render(text, True, self.color)
            old_rect = self.rect.copy()
            self.rect = self.surface.get_rect()
            
            if self.centered:
                self.rect.centerx = old_rect.centerx
                self.rect.y = old_rect.y
            else:
                self.rect.topleft = old_rect.topleft
    
    def draw(self, surface: pygame.Surface):
        """Draw label"""
        surface.blit(self.surface, self.rect)


class AlbumArt:
    """Circular album art display"""
    
    def __init__(self, x: int, y: int, size: int):
        self.x = x
        self.y = y
        self.size = size
        self.image = None
        
        # Create placeholder
        self._create_placeholder()
    
    def _create_placeholder(self):
        """Create placeholder image"""
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(surface, (40, 40, 40), (self.size//2, self.size//2), self.size//2)
        self.image = surface
    
    def set_image(self, image_surface: pygame.Surface):
        """Set album art image (will be made circular)"""
        if image_surface:
            # Scale to size
            scaled = pygame.transform.scale(image_surface, (self.size, self.size))
            
            # Create circular mask
            mask = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.circle(mask, (255, 255, 255, 255), 
                             (self.size//2, self.size//2), self.size//2)
            
            # Apply mask
            result = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            result.fill((0, 0, 0, 0))
            result.blit(scaled, (0, 0))
            result.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            
            self.image = result
    
    def draw(self, surface: pygame.Surface):
        """Draw album art"""
        if self.image:
            surface.blit(self.image, (self.x, self.y))


class OpacitySlider:
    """Vertical slider for opacity control (0.3 to 1.0)"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 initial_value: float = 0.95,
                 on_change: Optional[Callable[[float], None]] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.on_change = on_change
        
        # Range: 0.3 (30%) to 1.0 (100%)
        self.min_value = 0.3
        self.max_value = 1.0
        self.value = max(self.min_value, min(self.max_value, initial_value))
        
        # Colors
        self.bg_color = self._hex_to_rgb(PROGRESS_BG)
        self.fg_color = self._hex_to_rgb(PROGRESS_COLOR)
        self.handle_color = (255, 255, 255)
        
        # State
        self.is_dragging = False
        self.is_hovered = False
        
        # Handle (small circle that moves)
        self.handle_radius = 8
    
    def _hex_to_rgb(self, hex_color: str):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _value_to_y(self, value: float) -> int:
        """Convert value to y position"""
        # Top = 1.0, Bottom = 0.3 (inverted for intuitive control)
        normalized = (value - self.min_value) / (self.max_value - self.min_value)
        return self.rect.y + int((1.0 - normalized) * self.rect.height)
    
    def _y_to_value(self, y: int) -> float:
        """Convert y position to value"""
        # Top = 1.0, Bottom = 0.3
        y_offset = y - self.rect.y
        normalized = 1.0 - (y_offset / self.rect.height)
        value = self.min_value + normalized * (self.max_value - self.min_value)
        return max(self.min_value, min(self.max_value, value))
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events"""
        if event.type == pygame.MOUSEMOTION:
            handle_y = self._value_to_y(self.value)
            handle_rect = pygame.Rect(self.rect.x - 5, handle_y - self.handle_radius,
                                    self.rect.width + 10, self.handle_radius * 2)
            self.is_hovered = handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos)
            
            if self.is_dragging:
                self.value = self._y_to_value(event.pos[1])
                if self.on_change:
                    self.on_change(self.value)
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                self.is_dragging = True
                self.value = self._y_to_value(event.pos[1])
                if self.on_change:
                    self.on_change(self.value)
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                was_dragging = self.is_dragging
                self.is_dragging = False
                return was_dragging
        
        return False
    
    def set_value(self, value: float):
        """Set slider value (0.3 to 1.0)"""
        if not self.is_dragging:
            self.value = max(self.min_value, min(self.max_value, value))
    
    def draw(self, surface: pygame.Surface):
        """Draw vertical slider"""
        # Background track
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=2)
        
        # Filled portion (from bottom to handle position)
        handle_y = self._value_to_y(self.value)
        filled_height = self.rect.bottom - handle_y
        if filled_height > 0:
            filled_rect = pygame.Rect(self.rect.x, handle_y, 
                                    self.rect.width, filled_height)
            pygame.draw.rect(surface, self.fg_color, filled_rect, border_radius=2)
        
        # Handle (circle)
        pygame.draw.circle(surface, self.handle_color, 
                         (self.rect.centerx, handle_y), self.handle_radius)
        
        # Outline for handle
        pygame.draw.circle(surface, self.fg_color,
                         (self.rect.centerx, handle_y), self.handle_radius, 2)

