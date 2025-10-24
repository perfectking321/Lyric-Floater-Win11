"""
Test sprite centering after window resize
"""
import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.pygame_text_renderer import TextRenderer
from ui.pygame_sprite_manager import LyricSpriteManager
from ui.styles import *

def test_sprite_centering():
    """Test that sprites stay centered after resize"""
    print("\n" + "="*70)
    print("SPRITE CENTERING TEST AFTER RESIZE")
    print("="*70)
    
    pygame.init()
    
    # Test lyrics
    lyrics = [
        "Line 1",
        "Line 2 - This is the current line",
        "Line 3",
        "Line 4",
        "Line 5"
    ]
    
    current_line_index = 1  # Line 2 should be centered
    
    print(f"\n📋 Test Setup:")
    print(f"  Total lines: {len(lyrics)}")
    print(f"  Current line: {current_line_index} ('{lyrics[current_line_index]}')")
    print(f"  Expected: Line 2 should be centered on screen")
    
    # Test different window sizes
    window_sizes = [
        (600, 800, "Original"),
        (800, 900, "Wider + Taller"),
        (500, 600, "Smaller"),
        (700, 1000, "Taller")
    ]
    
    for width, height, description in window_sizes:
        print(f"\n{'='*70}")
        print(f"Testing: {description} ({width}x{height})")
        print(f"{'='*70}")
        
        screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        renderer = TextRenderer()
        sprite_manager = LyricSpriteManager(renderer, width, height)
        
        # Load lyrics
        sprite_manager.load_lyrics(lyrics)
        
        # Set current line
        sprite_manager.set_current_line(current_line_index)
        
        # Update sprites (this should center the current line)
        sprite_manager.update()
        
        # Check sprite positions
        print(f"\n📍 Sprite Positions:")
        center_y = height // 2
        
        for i, sprite in enumerate(sprite_manager.sprites):
            sprite_center_y = sprite.rect.y + (sprite.rect.height // 2)
            distance_from_center = sprite_center_y - center_y
            
            is_current = (i == current_line_index)
            status = "👉 CURRENT" if is_current else "   "
            
            print(f"  {status} Sprite {i}: Y={sprite.rect.y:4d}, "
                  f"Center={sprite_center_y:4d}, "
                  f"Distance from center: {distance_from_center:+5d}px")
            
            # Check if current line is centered
            if is_current:
                if abs(distance_from_center) <= 50:  # Within 50px tolerance
                    print(f"       ✅ Current line is centered!")
                else:
                    print(f"       ❌ Current line NOT centered! Off by {distance_from_center:+d}px")
                    
                # Check if visible on screen
                if sprite.rect.y < 0:
                    print(f"       ⚠️ WARNING: Sprite is ABOVE screen (Y={sprite.rect.y})")
                elif sprite.rect.y > height:
                    print(f"       ⚠️ WARNING: Sprite is BELOW screen (Y={sprite.rect.y})")
        
        print(f"\n📊 Analysis:")
        print(f"  Screen center Y: {center_y}")
        print(f"  Current line Y: {sprite_manager.sprites[current_line_index].rect.y}")
        print(f"  Sprite manager dimensions: {sprite_manager.window_width}x{sprite_manager.window_height}")
        
        # Visual test
        print(f"\n👁️ Visual test - press SPACE to continue to next size")
        
        clock = pygame.time.Clock()
        waiting = True
        
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
            
            # Draw
            screen.fill((20, 20, 20))
            
            # Draw center line
            pygame.draw.line(screen, (100, 100, 0), (0, center_y), (width, center_y), 2)
            
            # Draw sprites
            sprite_manager.draw(screen)
            
            # Draw instructions
            font = pygame.font.SysFont("Arial", 14)
            text = font.render(f"{description}: {width}x{height} | Yellow line = center | SPACE=next ESC=exit", 
                             True, (255, 255, 100))
            screen.blit(text, (10, 10))
            
            pygame.display.flip()
            clock.tick(60)
    
    pygame.quit()
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)

def check_sprite_manager_centering_code():
    """Check how sprite manager calculates positions"""
    print("\n" + "="*70)
    print("CHECKING SPRITE MANAGER CODE")
    print("="*70)
    
    with open('ui/pygame_sprite_manager.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find set_current_line method
    import re
    method = re.search(r'def set_current_line.*?(?=\n    def |\nclass |\Z)', content, re.DOTALL)
    
    if method:
        print("\nset_current_line method:")
        print("-" * 70)
        lines = method.group(0).split('\n')[:30]
        for i, line in enumerate(lines, 1):
            print(f"{i:3d}: {line}")
    
    # Find update method
    update_method = re.search(r'def update\(self\):.*?(?=\n    def |\nclass |\Z)', content, re.DOTALL)
    
    if update_method:
        print("\n\nupdate method:")
        print("-" * 70)
        lines = update_method.group(0).split('\n')[:30]
        for i, line in enumerate(lines, 1):
            print(f"{i:3d}: {line}")

if __name__ == "__main__":
    try:
        # Check the code first
        check_sprite_manager_centering_code()
        
        # Run visual test
        test_sprite_centering()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
