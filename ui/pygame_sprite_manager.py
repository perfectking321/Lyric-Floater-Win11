"""
Pygame Lyric Sprite Manager - Manages individual lyric line sprites
"""
import pygame
from typing import List, Tuple, Optional
from ui.styles import *
from ui.pygame_text_renderer import TextRenderer, TextLayout


class LyricSprite(pygame.sprite.Sprite):
    """Individual lyric line sprite with animation support"""
    
    def __init__(self, text: str, index: int, renderer: TextRenderer, 
                 x: int, y: int, width: int):
        super().__init__()
        
        self.text = text
        self.index = index
        self.renderer = renderer
        self.text_layout = TextLayout(renderer)
        self.width = width
        
        # Position
        self.x = x
        self.y = y
        self.target_y = y
        
        # Visual state
        self.opacity = OPACITY_FAR
        self.target_opacity = OPACITY_FAR
        self.font_key = 'normal'
        self.is_current = False
        
        # Animation state
        self.animation_speed = 0.15  # Lerp factor
        
        # Render initial surface
        self.update_surface()
    
    def update_surface(self):
        """Re-render the text surface with word wrapping"""
        color = self.renderer.get_color_for_opacity(self.opacity)
        
        # Wrap text to fit within width (leave margins on sides)
        max_text_width = self.width - 40  # 20px margin on each side
        wrapped_lines = self.text_layout.wrap_text(self.text, max_text_width, self.font_key)
        
        # Render each wrapped line
        line_surfaces = []
        total_height = 0
        max_line_width = 0
        
        for line in wrapped_lines:
            line_surface = self.renderer.render_text(line, self.font_key, color)
            line_surfaces.append(line_surface)
            total_height += line_surface.get_height()
            max_line_width = max(max_line_width, line_surface.get_width())
        
        # Add spacing between wrapped lines
        line_spacing = 5
        total_height += line_spacing * (len(wrapped_lines) - 1) if len(wrapped_lines) > 1 else 0
        
        # Create surface with proper dimensions
        # Use fixed minimum height for consistent spacing between different lyrics
        fixed_height = max(50, total_height + 20)
        
        self.image = pygame.Surface((self.width, fixed_height), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))  # Transparent background
        
        # Draw each line centered horizontally, stacked vertically
        current_y = (fixed_height - total_height) // 2
        
        for line_surface in line_surfaces:
            text_x = (self.width - line_surface.get_width()) // 2
            self.image.blit(line_surface, (text_x, current_y))
            current_y += line_surface.get_height() + line_spacing
        
        # Update rect
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = int(self.y)
    
    def set_target_opacity(self, opacity: float):
        """Set target opacity for smooth transition"""
        self.target_opacity = max(0.0, min(1.0, opacity))
    
    def set_target_y(self, y: float):
        """Set target Y position for smooth scrolling"""
        self.target_y = y
    
    def set_current(self, is_current: bool):
        """Mark as current line"""
        self.is_current = is_current
        self.font_key = 'current' if is_current else 'normal'
    
    def update(self):
        """Update sprite state with smooth animations"""
        needs_update = False
        
        # Smooth opacity transition
        if abs(self.opacity - self.target_opacity) > 0.01:
            self.opacity += (self.target_opacity - self.opacity) * self.animation_speed
            needs_update = True
        
        # Smooth position transition
        if abs(self.y - self.target_y) > 0.5:
            self.y += (self.target_y - self.y) * self.animation_speed
            needs_update = True
        
        # Re-render if changed
        if needs_update:
            self.update_surface()
    
    def is_visible(self, screen_height: int) -> bool:
        """Check if sprite is visible on screen"""
        return -100 < self.rect.y < screen_height + 100


class LyricSpriteManager:
    """Manages all lyric line sprites"""
    
    def __init__(self, renderer: TextRenderer, screen_width: int, screen_height: int):
        self.renderer = renderer
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Sprite group for efficient rendering
        self.sprites = pygame.sprite.Group()
        self.lyric_sprites: List[LyricSprite] = []
        
        # Layout settings
        self.lyrics_area_y = HEADER_HEIGHT
        self.lyrics_area_height = screen_height - HEADER_HEIGHT - CONTROL_HEIGHT
        # Increase line height to prevent overlap (50px minimum for 18pt font)
        self.line_height = max(50, int(FONT_SIZE_CURRENT * LINE_SPACING))
        
        # Current state
        self.current_index = -1
        self.scroll_offset = 0
        self.target_scroll_offset = 0
    
    def load_lyrics(self, lyrics: List[str]):
        """Load lyrics and create sprites"""
        # Clear existing sprites
        self.sprites.empty()
        self.lyric_sprites.clear()
        
        # Create sprites
        y_pos = self.lyrics_area_y + LYRICS_PADDING
        
        for i, line_text in enumerate(lyrics):
            sprite = LyricSprite(
                text=line_text,
                index=i,
                renderer=self.renderer,
                x=0,
                y=y_pos,
                width=self.screen_width
            )
            
            self.lyric_sprites.append(sprite)
            self.sprites.add(sprite)
            
            y_pos += self.line_height
        
        print(f"[SpriteManager] Loaded {len(self.lyric_sprites)} lyric sprites")
    
    def set_current_line(self, index: int):
        """Set current highlighted line"""
        if index == self.current_index:
            return
        
        # Update old current line
        if 0 <= self.current_index < len(self.lyric_sprites):
            self.lyric_sprites[self.current_index].set_current(False)
            self.lyric_sprites[self.current_index].set_target_opacity(OPACITY_PAST)
        
        # Update new current line
        self.current_index = index
        if 0 <= index < len(self.lyric_sprites):
            current_sprite = self.lyric_sprites[index]
            current_sprite.set_current(True)
            current_sprite.set_target_opacity(OPACITY_CURRENT)
            
            # Update surrounding lines
            self._update_surrounding_opacities(index)
            
            # Auto-scroll to current line
            self._scroll_to_line(index)
    
    def _update_surrounding_opacities(self, current_index: int):
        """Update opacity for lines around current line"""
        for i, sprite in enumerate(self.lyric_sprites):
            if i == current_index:
                continue
            
            distance = abs(i - current_index)
            
            if distance == 1:
                sprite.set_target_opacity(OPACITY_NEXT_1)
            elif distance == 2:
                sprite.set_target_opacity(OPACITY_NEXT_2)
            elif distance == 3:
                sprite.set_target_opacity(OPACITY_NEXT_3)
            elif i < current_index:
                sprite.set_target_opacity(OPACITY_PAST)
            else:
                sprite.set_target_opacity(OPACITY_FAR)
    
    def _scroll_to_line(self, index: int):
        """Smooth scroll to bring line into view"""
        if not (0 <= index < len(self.lyric_sprites)):
            return
        
        # Calculate BASE position of sprite (before scroll offset applied)
        base_y = self.lyrics_area_y + LYRICS_PADDING + (index * self.line_height)
        
        # Calculate target scroll to center the line
        center_y = self.lyrics_area_y + (self.lyrics_area_height // 2)
        target_scroll = base_y - center_y
        
        # Calculate scroll bounds
        # Min scroll: can be negative to center top lines
        # Max scroll: ensure bottom of content doesn't go above bottom of lyrics area
        total_content_height = len(self.lyric_sprites) * self.line_height
        max_scroll = total_content_height - self.lyrics_area_height
        
        # Allow negative scroll for centering top lines, but don't scroll past bottom
        self.target_scroll_offset = min(target_scroll, max_scroll)
    
    def update(self):
        """Update all sprites"""
        # Smooth scroll transition
        if abs(self.scroll_offset - self.target_scroll_offset) > 0.5:
            self.scroll_offset += (self.target_scroll_offset - self.scroll_offset) * 0.15
            
            # Update sprite positions
            for sprite in self.lyric_sprites:
                base_y = self.lyrics_area_y + LYRICS_PADDING + (sprite.index * self.line_height)
                sprite.set_target_y(base_y - self.scroll_offset)
        
        # Update all sprites
        self.sprites.update()
    
    def draw(self, surface: pygame.Surface):
        """Draw visible sprites"""
        # Only draw visible sprites for performance
        visible_sprites = [s for s in self.lyric_sprites if s.is_visible(self.screen_height)]
        
        for sprite in visible_sprites:
            surface.blit(sprite.image, sprite.rect)
    
    def get_sprite_count(self) -> int:
        """Get total sprite count"""
        return len(self.lyric_sprites)
