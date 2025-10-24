"""
FINAL ROOT CAUSE TEST
Check exact rendering with actual fetched lyrics
"""
import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.pygame_text_renderer import TextRenderer
from ui.styles import *

def test_actual_lyrics_rendering():
    """Test with actual fetched lyrics"""
    print("\n" + "="*60)
    print("ACTUAL LYRICS RENDERING TEST")
    print("="*60)
    
    pygame.init()
    screen = pygame.display.set_mode((500, 700))
    pygame.display.set_caption("Actual Lyrics Test")
    clock = pygame.time.Clock()
    
    # Create renderer
    renderer = TextRenderer()
    
    # Actual lyrics from cache
    actual_lyrics = [
        'जनम, जनम, जनम साथ चलना यूँही',
        'क़सम, तुम्हें क़सम आके मिलना यहीं',
        'एक जाँ है, भले दो बदन हों जुदा',
        'मेरी होके हमेशा ही रहना, कभी ना कहना अलविदा'
    ]
    
    print(f"\n🎨 Rendering {len(actual_lyrics)} lines...")
    
    # Test each font size
    font_tests = [
        ('small', FONT_SIZE_SMALL),
        ('normal', FONT_SIZE),
        ('current', FONT_SIZE_CURRENT),
        ('title', FONT_SIZE_TITLE)
    ]
    
    rendered_surfaces = []
    
    for font_key, font_size in font_tests:
        print(f"\n📝 Testing font '{font_key}' (size {font_size}):")
        
        for i, text in enumerate(actual_lyrics[:2]):  # Test first 2 lines
            color = renderer.get_color_for_opacity(1.0)
            surface = renderer.render_text(text, font_key, color, antialias=True)
            
            width, height = surface.get_size()
            print(f"   Line {i+1}: {width}x{height}px")
            
            # Check if surface is blank (would indicate rendering failure)
            # Sample a few pixels to see if any are non-black
            pixel_sum = 0
            for x in range(0, min(width, 100), 10):
                for y in range(0, min(height, 20), 5):
                    try:
                        pixel = surface.get_at((x, y))
                        pixel_sum += pixel[0] + pixel[1] + pixel[2]
                    except:
                        pass
            
            if pixel_sum == 0:
                print(f"      ⚠️ WARNING: Surface appears blank!")
            else:
                print(f"      ✅ Surface has pixels (sum: {pixel_sum})")
            
            rendered_surfaces.append((f"{font_key} - Line {i+1}", surface, font_size))
    
    # Display all
    print(f"\n🎮 Displaying all rendered surfaces...")
    print(f"   Press ESC to close, 1-4 to toggle fonts")
    
    show_font_idx = 0
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    show_font_idx = 0
                elif event.key == pygame.K_2:
                    show_font_idx = 1
                elif event.key == pygame.K_3:
                    show_font_idx = 2
                elif event.key == pygame.K_4:
                    show_font_idx = 3
        
        screen.fill((0, 0, 0))
        
        # Title
        title_font = pygame.font.Font(None, 24)
        title_text = title_font.render(f"Font Test - Press 1-4 (Current: {show_font_idx+1})", True, (100, 100, 100))
        screen.blit(title_text, (20, 20))
        
        # Show selected font group
        y = 100
        start_idx = show_font_idx * 2
        end_idx = start_idx + 2
        
        for label, surface, font_size in rendered_surfaces[start_idx:end_idx]:
            # Label
            label_surf = title_font.render(label, True, (150, 150, 150))
            screen.blit(label_surf, (20, y))
            
            # Surface
            screen.blit(surface, (20, y + 30))
            
            y += 100
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    print(f"\n✅ Test complete")
    
    # Final check
    print(f"\n" + "="*60)
    print("ROOT CAUSE ANALYSIS")
    print("="*60)
    
    print(f"\n🔍 Checking font file...")
    font_path = renderer.fonts['normal'].get_file()
    print(f"   Font file: {font_path}")
    
    # Check if it's the light variant
    if 'light' in font_path.lower() or 'segoeuil' in font_path.lower():
        print(f"\n❌ ROOT CAUSE FOUND!")
        print(f"   Using Segoe UI LIGHT variant: {font_path}")
        print(f"   This variant has LIMITED Devanagari support!")
        print(f"\n🔧 SOLUTION:")
        print(f"   Update pygame_text_renderer.py line ~30:")
        print(f"   Change:")
        print(f"      font_path = pygame.font.match_font('segoeui')")
        print(f"   To:")
        print(f"      # Try regular variant first")
        print(f"      font_path = r'C:\\Windows\\Fonts\\segoeui.ttf'")
        print(f"      if not os.path.exists(font_path):")
        print(f"          font_path = pygame.font.match_font('nirmalaui')  # Better Hindi support")
        print(f"      if not font_path:")
        print(f"          font_path = pygame.font.match_font('segoeui')")
    else:
        print(f"\n✅ Font looks OK")
        print(f"   Issue might be antialias or color related")


if __name__ == "__main__":
    test_actual_lyrics_rendering()
