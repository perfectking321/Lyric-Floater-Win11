"""
Test to diagnose why current line is not centered after operations
"""
import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.pygame_text_renderer import TextRenderer
from ui.pygame_sprite_manager import LyricSpriteManager
from ui.styles import *

def test_centering_logic():
    """Test the centering calculation in sprite manager"""
    print("\n" + "="*70)
    print("SPRITE CENTERING LOGIC DIAGNOSTIC")
    print("="*70)
    
    pygame.init()
    
    # Create test setup
    screen_width = 600
    screen_height = 800
    screen = pygame.display.set_mode((screen_width, screen_height))
    
    renderer = TextRenderer()
    sprite_manager = LyricSpriteManager(renderer, screen_width, screen_height)
    
    # Create test lyrics (20 lines)
    lyrics = [f"Line {i+1}: Test lyric text here" for i in range(20)]
    
    print(f"\n📋 Setup:")
    print(f"  Screen: {screen_width}x{screen_height}")
    print(f"  Total lyrics: {len(lyrics)} lines")
    print(f"  Header height: {HEADER_HEIGHT}")
    print(f"  Control height: {CONTROL_HEIGHT}")
    
    # Calculate available area
    lyrics_area_height = screen_height - HEADER_HEIGHT - CONTROL_HEIGHT
    center_y = HEADER_HEIGHT + (lyrics_area_height // 2)
    
    print(f"  Lyrics area height: {lyrics_area_height}px")
    print(f"  Center Y position: {center_y}px")
    
    # Load lyrics
    sprite_manager.load_lyrics(lyrics)
    
    print(f"\n📍 Initial sprite positions (after load):")
    for i, sprite in enumerate(sprite_manager.lyric_sprites[:5]):
        print(f"  Sprite {i}: Y={sprite.y}, target_y={sprite.target_y}, rect.y={sprite.rect.y}")
    
    # Test setting different current lines
    test_indices = [0, 5, 10, 15, 19]  # First, middle, last
    
    for test_index in test_indices:
        print(f"\n{'='*70}")
        print(f"TEST: Setting current line to {test_index}")
        print(f"{'='*70}")
        
        # Set current line
        sprite_manager.set_current_line(test_index)
        
        # Check scroll calculation
        current_sprite = sprite_manager.lyric_sprites[test_index]
        print(f"\n📊 After set_current_line({test_index}):")
        print(f"  Current sprite initial Y: {current_sprite.y}")
        print(f"  Target scroll offset: {sprite_manager.target_scroll_offset}")
        print(f"  Scroll offset: {sprite_manager.scroll_offset}")
        
        # Calculate where sprite should be
        expected_center = center_y
        print(f"\n🎯 Centering calculation:")
        print(f"  Expected center Y: {expected_center}")
        print(f"  Sprite Y before scroll: {current_sprite.y}")
        print(f"  Scroll offset: {sprite_manager.scroll_offset}")
        print(f"  Sprite Y after scroll: {current_sprite.y - sprite_manager.scroll_offset}")
        
        # Update sprites (apply smooth transitions)
        for _ in range(100):  # Run enough updates for smooth transition to complete
            sprite_manager.update()
        
        print(f"\n📍 After update (smooth transition complete):")
        print(f"  Scroll offset: {sprite_manager.scroll_offset}")
        print(f"  Current sprite target_y: {current_sprite.target_y}")
        print(f"  Current sprite actual y: {current_sprite.y}")
        print(f"  Current sprite rect.y: {current_sprite.rect.y}")
        
        # Calculate actual position on screen
        actual_screen_y = current_sprite.rect.y - sprite_manager.scroll_offset
        distance_from_center = actual_screen_y - center_y
        
        print(f"\n🔍 Final position check:")
        print(f"  Screen center: {center_y}")
        print(f"  Sprite rect.y: {current_sprite.rect.y}")
        print(f"  Scroll offset: {sprite_manager.scroll_offset}")
        print(f"  Actual screen Y: {actual_screen_y}")
        print(f"  Distance from center: {distance_from_center:+.1f}px")
        
        if abs(distance_from_center) <= 50:
            print(f"  ✅ CENTERED (within 50px tolerance)")
        else:
            print(f"  ❌ NOT CENTERED (off by {distance_from_center:+.1f}px)")
    
    pygame.quit()

def test_scroll_to_line_method():
    """Directly test the _scroll_to_line method"""
    print("\n" + "="*70)
    print("TESTING _scroll_to_line METHOD")
    print("="*70)
    
    pygame.init()
    
    screen_width = 600
    screen_height = 800
    renderer = TextRenderer()
    sprite_manager = LyricSpriteManager(renderer, screen_width, screen_height)
    
    lyrics = [f"Line {i+1}" for i in range(20)]
    sprite_manager.load_lyrics(lyrics)
    
    print(f"\n📏 Sprite Manager State:")
    print(f"  Screen: {screen_width}x{screen_height}")
    print(f"  Lyrics area Y: {sprite_manager.lyrics_area_y}")
    print(f"  Lyrics area height: {sprite_manager.lyrics_area_height}")
    print(f"  Line height: {sprite_manager.line_height}")
    
    # Check the scroll calculation for each sprite
    center_y = sprite_manager.lyrics_area_y + (sprite_manager.lyrics_area_height // 2)
    
    print(f"\n🎯 Expected center Y: {center_y}")
    print(f"\n📍 Testing scroll calculation for each line:")
    
    for i in range(min(10, len(lyrics))):
        sprite = sprite_manager.lyric_sprites[i]
        
        # Manually calculate what scroll should be
        expected_scroll = sprite.y - center_y
        max_scroll = max(0, len(sprite_manager.lyric_sprites) * sprite_manager.line_height - sprite_manager.lyrics_area_height)
        expected_scroll = max(0, min(expected_scroll, max_scroll))
        
        # Trigger scroll calculation
        sprite_manager._scroll_to_line(i)
        
        actual_scroll = sprite_manager.target_scroll_offset
        
        print(f"  Line {i:2d}: sprite.y={sprite.y:4d}, "
              f"expected_scroll={expected_scroll:5.0f}, "
              f"actual_scroll={actual_scroll:5.0f}, "
              f"match={'✅' if abs(expected_scroll - actual_scroll) < 1 else '❌'}")
    
    pygame.quit()

def test_sprite_drawing_with_scroll():
    """Visual test showing sprite positions with scrolling"""
    print("\n" + "="*70)
    print("VISUAL TEST: Sprite positions with scroll offset")
    print("="*70)
    print("\nInstructions:")
    print("  - Press 1-5 to set current line")
    print("  - Press UP/DOWN to manually adjust scroll")
    print("  - Press R to reset")
    print("  - Press SPACE to auto-scroll to current line")
    print("  - Press ESC to exit")
    
    pygame.init()
    
    screen_width = 600
    screen_height = 800
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 12)
    
    renderer = TextRenderer()
    sprite_manager = LyricSpriteManager(renderer, screen_width, screen_height)
    
    lyrics = [f"Line {i+1}: Lyric text here" for i in range(20)]
    sprite_manager.load_lyrics(lyrics)
    
    current_line = 10
    sprite_manager.set_current_line(current_line)
    
    # Run updates to settle animations
    for _ in range(100):
        sprite_manager.update()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    current_line = 0
                    sprite_manager.set_current_line(current_line)
                elif event.key == pygame.K_2:
                    current_line = 5
                    sprite_manager.set_current_line(current_line)
                elif event.key == pygame.K_3:
                    current_line = 10
                    sprite_manager.set_current_line(current_line)
                elif event.key == pygame.K_4:
                    current_line = 15
                    sprite_manager.set_current_line(current_line)
                elif event.key == pygame.K_5:
                    current_line = 19
                    sprite_manager.set_current_line(current_line)
                elif event.key == pygame.K_UP:
                    sprite_manager.scroll_offset -= 20
                    sprite_manager.target_scroll_offset = sprite_manager.scroll_offset
                elif event.key == pygame.K_DOWN:
                    sprite_manager.scroll_offset += 20
                    sprite_manager.target_scroll_offset = sprite_manager.scroll_offset
                elif event.key == pygame.K_r:
                    sprite_manager.scroll_offset = 0
                    sprite_manager.target_scroll_offset = 0
                elif event.key == pygame.K_SPACE:
                    sprite_manager._scroll_to_line(current_line)
        
        # Update
        sprite_manager.update()
        
        # Draw
        screen.fill((20, 20, 20))
        
        # Draw lyrics area boundaries
        lyrics_area_top = HEADER_HEIGHT
        lyrics_area_bottom = screen_height - CONTROL_HEIGHT
        pygame.draw.line(screen, (50, 50, 100), (0, lyrics_area_top), (screen_width, lyrics_area_top), 2)
        pygame.draw.line(screen, (50, 50, 100), (0, lyrics_area_bottom), (screen_width, lyrics_area_bottom), 2)
        
        # Draw center line
        center_y = lyrics_area_top + ((lyrics_area_bottom - lyrics_area_top) // 2)
        pygame.draw.line(screen, (100, 100, 0), (0, center_y), (screen_width, center_y), 2)
        
        # Draw sprites with scroll offset applied
        for sprite in sprite_manager.lyric_sprites:
            # Apply scroll offset
            display_y = sprite.rect.y - sprite_manager.scroll_offset
            
            if -100 < display_y < screen_height + 100:
                screen.blit(sprite.image, (sprite.rect.x, display_y))
        
        # Draw info
        info_lines = [
            f"Current line: {current_line}",
            f"Scroll offset: {sprite_manager.scroll_offset:.0f}",
            f"Target scroll: {sprite_manager.target_scroll_offset:.0f}",
            f"Center Y: {center_y}",
            f"Current sprite Y: {sprite_manager.lyric_sprites[current_line].rect.y}",
            f"Display Y: {sprite_manager.lyric_sprites[current_line].rect.y - sprite_manager.scroll_offset:.0f}",
            "",
            "1-5: Set line | UP/DOWN: Manual scroll",
            "SPACE: Auto center | R: Reset | ESC: Exit"
        ]
        
        y = 10
        for line in info_lines:
            text = font.render(line, True, (255, 255, 100))
            bg_rect = pygame.Rect(5, y-2, text.get_width()+10, text.get_height()+4)
            pygame.draw.rect(screen, (0, 0, 0, 200), bg_rect)
            screen.blit(text, (10, y))
            y += 18
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    try:
        print("="*70)
        print("DIAGNOSING SPRITE CENTERING ISSUE")
        print("="*70)
        
        # Test 1: Check centering logic
        test_centering_logic()
        
        # Test 2: Check scroll_to_line calculation
        test_scroll_to_line_method()
        
        # Test 3: Visual test
        input("\nPress ENTER to start visual test...")
        test_sprite_drawing_with_scroll()
        
        print("\n" + "="*70)
        print("DIAGNOSTIC COMPLETE")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
