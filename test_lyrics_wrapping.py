"""
Test case to diagnose lyrics wrapping issue
Some songs display in one long line, others wrap correctly
"""
import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.pygame_text_renderer import TextRenderer
from ui.pygame_sprite_manager import LyricSpriteManager
from ui.styles import *

def test_text_wrapping():
    """Test if long lines are being wrapped correctly"""
    print("\n=== Testing Lyrics Text Wrapping ===\n")
    
    pygame.init()
    screen = pygame.display.set_mode((600, 800))
    
    renderer = TextRenderer()
    sprite_manager = LyricSpriteManager(renderer, 600, 800)
    
    # Test cases - different line lengths
    test_lyrics = [
        "Short line",  # Should fit
        "We all need that someone who gets you like no other",  # Long line - should wrap?
        "Under the sea, under the sea",  # Medium line
        "Where are you now?",  # Short question
        "Another dream",  # Short
        "The monster's running wild inside of me",  # Long line
        "I'm faded",  # Short
        "So lost, I'm faded",  # Medium
        "This is an extremely long line that should definitely wrap because it exceeds the window width significantly"  # Very long
    ]
    
    print("Test lyrics:")
    for i, line in enumerate(test_lyrics):
        print(f"  {i+1}. [{len(line)} chars] {line[:50]}{'...' if len(line) > 50 else ''}")
    
    print("\n" + "="*60)
    
    # Load lyrics into sprite manager
    sprite_manager.load_lyrics(test_lyrics)
    
    # Check if sprites were created
    print(f"\n✓ Loaded {len(test_lyrics)} lyrics lines")
    print(f"✓ Created {len(sprite_manager.sprites)} sprites")
    
    # Analyze each sprite
    print("\n" + "="*60)
    print("SPRITE ANALYSIS:")
    print("="*60)
    
    for i, sprite in enumerate(sprite_manager.sprites):
        text = sprite.text
        surface = sprite.surface
        width = surface.get_width() if surface else 0
        height = surface.get_height() if surface else 0
        
        # Check if text was rendered
        if surface:
            # Check if text fits within window width (600px)
            fits = width <= 580  # Allow 20px margin
            status = "✓ FITS" if fits else "✗ TOO WIDE"
            
            print(f"\nSprite {i+1}:")
            print(f"  Text: {text[:50]}{'...' if len(text) > 50 else ''}")
            print(f"  Text length: {len(text)} chars")
            print(f"  Surface size: {width}x{height} px")
            print(f"  Status: {status}")
            
            if not fits:
                print(f"  ⚠️ WARNING: Surface width {width}px exceeds window width!")
                print(f"  Expected: Should wrap or truncate to fit within 580px")
        else:
            print(f"\nSprite {i+1}: ✗ NO SURFACE CREATED")
    
    # Visual test
    print("\n" + "="*60)
    print("VISUAL TEST (close window when done)")
    print("="*60)
    print("Instructions:")
    print("  - Check if long lines are cut off or wrapped")
    print("  - All text should be visible within the window")
    print("  - Press ESC to close")
    
    clock = pygame.time.Clock()
    running = True
    scroll_y = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    scroll_y -= 50
                elif event.key == pygame.K_DOWN:
                    scroll_y += 50
        
        # Draw
        screen.fill((20, 20, 20))
        
        # Draw sprites at different Y positions to see all
        for i, sprite in enumerate(sprite_manager.sprites):
            if sprite.surface:
                y_pos = 50 + (i * 70) + scroll_y
                screen.blit(sprite.surface, (10, y_pos))
                
                # Draw window boundary
                pygame.draw.rect(screen, (100, 100, 100), (0, y_pos - 5, 600, 60), 1)
        
        # Draw instructions
        font = pygame.font.SysFont("Arial", 14)
        inst = font.render("UP/DOWN to scroll | ESC to exit", True, (150, 150, 150))
        screen.blit(inst, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

def test_text_renderer_directly():
    """Test the TextRenderer's render_text method"""
    print("\n=== Testing TextRenderer Directly ===\n")
    
    pygame.init()
    renderer = TextRenderer()
    
    test_lines = [
        "Short line",
        "We all need that someone who gets you like no other",
        "This is an extremely long line that should definitely wrap because it exceeds the window width significantly"
    ]
    
    print("Testing TextRenderer.render_text():")
    print("="*60)
    
    for text in test_lines:
        surface = renderer.render_text(
            text=text,
            opacity=1.0,
            color=(255, 255, 255)
        )
        
        print(f"\nInput: {text[:60]}{'...' if len(text) > 60 else ''}")
        print(f"  Length: {len(text)} chars")
        if surface:
            print(f"  Output: {surface.get_width()}x{surface.get_height()} px")
            print(f"  Fits in 600px window: {'✓ YES' if surface.get_width() <= 580 else '✗ NO'}")
        else:
            print(f"  Output: None")
    
    pygame.quit()

def check_sprite_manager_code():
    """Check how sprite manager creates surfaces"""
    print("\n=== Checking Sprite Manager Code ===\n")
    
    import inspect
    from ui.pygame_sprite_manager import LyricSprite
    
    # Check LyricSprite.update_surface method
    source = inspect.getsource(LyricSprite.update_surface)
    
    print("LyricSprite.update_surface() method:")
    print("="*60)
    print(source)
    print("="*60)
    
    # Look for text wrapping logic
    if "wrap" in source.lower():
        print("✓ Found text wrapping logic")
    else:
        print("✗ NO text wrapping logic found!")
        print("⚠️ This is likely the root cause - text is not being wrapped!")

if __name__ == "__main__":
    print("="*60)
    print("LYRICS WRAPPING DIAGNOSTIC TEST")
    print("="*60)
    
    try:
        # Test 1: Check the code
        check_sprite_manager_code()
        
        # Test 2: Test renderer directly
        test_text_renderer_directly()
        
        # Test 3: Visual test
        test_text_wrapping()
        
        print("\n" + "="*60)
        print("DIAGNOSTIC COMPLETE")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
