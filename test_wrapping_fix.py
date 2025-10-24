"""
Test case for lyrics wrapping fix
"""
import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.pygame_text_renderer import TextRenderer, TextLayout
from ui.pygame_sprite_manager import LyricSpriteManager
from ui.styles import *

def test_wrapping():
    """Test that long lines wrap correctly"""
    print("\n=== Testing Lyrics Wrapping Fix ===\n")
    
    pygame.init()
    screen = pygame.display.set_mode((600, 800))
    pygame.display.set_caption("Lyrics Wrapping Test")
    
    renderer = TextRenderer()
    sprite_manager = LyricSpriteManager(renderer, 600, 800)
    
    # Test lyrics - mix of short and long lines (like "Alone" song)
    test_lyrics = [
        "Alone",  # Short title
        "We all need that someone who gets you like no other",  # LONG LINE - should wrap
        "Someone to hold me close",  # Medium
        "And I think about you every day and night",  # Long line
        "It's crazy",  # Short
        "I'm lost without you here",  # Medium
        "This is an extremely long line that definitely needs to wrap to multiple lines because it's way too long",  # Very long
        "Short",  # Short
        "Under the sea, under the sea",  # Medium (Faded reference)
    ]
    
    print("Loading test lyrics:")
    for i, line in enumerate(test_lyrics, 1):
        char_count = len(line)
        status = "LONG" if char_count > 40 else "OK"
        print(f"  {i}. [{char_count:2d} chars] [{status:4s}] {line[:50]}{'...' if len(line) > 50 else ''}")
    
    # Load lyrics
    sprite_manager.load_lyrics(test_lyrics)
    
    print(f"\n✓ Loaded {len(test_lyrics)} lyrics")
    print(f"✓ Created {len(sprite_manager.sprites)} sprites")
    
    # Analyze sprites
    print("\n" + "="*70)
    print("SPRITE ANALYSIS:")
    print("="*70)
    
    all_fit = True
    for i, sprite in enumerate(sprite_manager.sprites, 1):
        text = sprite.text
        surface = sprite.image
        width = surface.get_width()
        height = surface.get_height()
        
        # Check if sprite fits within window
        fits = width <= 600
        status = "✓ FITS" if fits else "✗ TOO WIDE"
        
        if not fits:
            all_fit = False
        
        print(f"\nSprite {i}: {status}")
        print(f"  Text: {text[:55]}{'...' if len(text) > 55 else ''}")
        print(f"  Chars: {len(text)}")
        print(f"  Surface: {width}x{height}px")
        
        if not fits:
            print(f"  ⚠️ ERROR: Width {width}px exceeds window width 600px!")
    
    print("\n" + "="*70)
    
    if all_fit:
        print("✅ SUCCESS: All sprites fit within window width!")
    else:
        print("❌ FAILURE: Some sprites are too wide!")
    
    # Visual test
    print("\n" + "="*70)
    print("VISUAL TEST")
    print("="*70)
    print("Instructions:")
    print("  - Check if long lines are wrapped properly")
    print("  - All text should be visible within the window")
    print("  - Use UP/DOWN arrows to scroll")
    print("  - Press SPACE to toggle test info")
    print("  - Press ESC to close")
    
    clock = pygame.time.Clock()
    running = True
    show_info = True
    font = pygame.font.SysFont("Arial", 14)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    show_info = not show_info
        
        # Draw
        screen.fill((20, 20, 20))
        
        # Draw sprites
        sprite_manager.draw(screen)
        
        # Draw window boundaries
        pygame.draw.rect(screen, (100, 50, 50), (0, 0, 600, 800), 2)
        pygame.draw.line(screen, (50, 50, 100), (20, 0), (20, 800), 1)  # Left margin
        pygame.draw.line(screen, (50, 50, 100), (580, 0), (580, 800), 1)  # Right margin
        
        # Draw info
        if show_info:
            info_lines = [
                "Lyrics Wrapping Test",
                f"Window: 600x800px",
                f"Sprites: {len(sprite_manager.sprites)}",
                "SPACE: Toggle info | ESC: Exit"
            ]
            
            y = 10
            for line in info_lines:
                text = font.render(line, True, (255, 255, 100))
                # Draw with background for readability
                bg_rect = pygame.Rect(5, y-2, text.get_width()+10, text.get_height()+4)
                pygame.draw.rect(screen, (0, 0, 0, 200), bg_rect)
                screen.blit(text, (10, y))
                y += 20
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    
    return all_fit

if __name__ == "__main__":
    print("="*70)
    print("LYRICS WRAPPING FIX TEST")
    print("="*70)
    
    try:
        success = test_wrapping()
        
        print("\n" + "="*70)
        if success:
            print("✅ TEST PASSED: All lyrics wrap correctly!")
        else:
            print("❌ TEST FAILED: Some lyrics still don't fit!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
