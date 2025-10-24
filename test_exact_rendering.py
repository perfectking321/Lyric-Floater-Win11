"""
Test Case 3: Exact Simulation of Pygame Window Rendering
Reproduce the exact rendering pipeline to find where boxes appear
"""
import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.styles import *
from ui.pygame_text_renderer import TextRenderer
from ui.pygame_sprite_manager import LyricSprite

def test_exact_rendering():
    """Simulate exact rendering as in the app"""
    print("\n" + "="*60)
    print("EXACT RENDERING SIMULATION")
    print("="*60)
    
    pygame.init()
    screen = pygame.display.set_mode((500, 700))
    pygame.display.set_caption("Rendering Test - Exact Simulation")
    clock = pygame.time.Clock()
    
    # Create text renderer (exactly as in app)
    renderer = TextRenderer()
    
    # Test lyrics (from your screenshot)
    test_lyrics = [
        "आपण सुरू करूया का बाबा, कसा ना घेतो तक्रार",
        "आहो, तुमच्या आणि माझा प्रेमाच प्रकार",
        "हो मारू मी, माल तो काढू तुझा धावून",
        "फुंकू भुसू भुसून ना जारा, कसा ना घेतो तक्रार"
    ]
    
    print(f"\n📝 Test lyrics ({len(test_lyrics)} lines):")
    for i, line in enumerate(test_lyrics):
        print(f"   {i+1}. {line}")
        # Check encoding
        try:
            line.encode('utf-8')
            print(f"      ✅ UTF-8 encoding OK")
        except:
            print(f"      ❌ UTF-8 encoding FAILED")
    
    # Create sprites
    sprites = []
    y_pos = 150
    
    for i, line in enumerate(test_lyrics):
        sprite = LyricSprite(
            text=line,
            index=i,
            renderer=renderer,
            x=0,
            y=y_pos,
            width=500
        )
        sprite.set_target_opacity(0.7 if i == 0 else 0.4)
        sprites.append(sprite)
        y_pos += 50
    
    print(f"\n🎨 Created {len(sprites)} sprites")
    
    # Check what was actually rendered
    print(f"\n🔍 Inspecting rendered sprites:")
    for i, sprite in enumerate(sprites):
        print(f"\n   Sprite {i+1}: {sprite.text[:30]}...")
        print(f"      Image size: {sprite.image.get_size()}")
        print(f"      Rect: {sprite.rect}")
        print(f"      Opacity: {sprite.opacity}")
        print(f"      Font key: {sprite.font_key}")
    
    # Main loop
    print(f"\n🎮 Starting render loop...")
    print(f"   Press ESC to close, SPACE to change opacity")
    
    running = True
    frame = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Toggle opacity
                    for sprite in sprites:
                        new_opacity = 1.0 if sprite.target_opacity < 0.9 else 0.3
                        sprite.set_target_opacity(new_opacity)
        
        # Update
        for sprite in sprites:
            sprite.update()
        
        # Draw
        screen.fill((0, 0, 0))
        
        # Title
        title_font = pygame.font.Font(None, 24)
        title = title_font.render("Exact Rendering Test - Press SPACE", True, (100, 100, 100))
        screen.blit(title, (20, 20))
        
        # Render sprites
        for sprite in sprites:
            screen.blit(sprite.image, sprite.rect)
        
        # FPS counter
        fps_text = title_font.render(f"FPS: {int(clock.get_fps())}", True, (100, 100, 100))
        screen.blit(fps_text, (20, 650))
        
        pygame.display.flip()
        clock.tick(60)
        
        frame += 1
        
        # Log first frame
        if frame == 1:
            print(f"   ✅ First frame rendered")
    
    pygame.quit()
    print(f"\n✅ Test complete")
    
    # Check cache stats
    stats = renderer.get_cache_stats()
    print(f"\n📊 Cache statistics:")
    print(f"   Hits: {stats['hits']}")
    print(f"   Misses: {stats['misses']}")
    print(f"   Hit rate: {stats['hit_rate']:.1f}%")
    print(f"   Cache size: {stats['cache_size']}")


def test_direct_font_rendering():
    """Test direct font rendering without any caching"""
    print("\n" + "="*60)
    print("DIRECT FONT RENDERING TEST (No Cache)")
    print("="*60)
    
    pygame.init()
    screen = pygame.display.set_mode((500, 400))
    pygame.display.set_caption("Direct Font Test")
    clock = pygame.time.Clock()
    
    # Load font directly
    font_path = pygame.font.match_font('segoeui')
    print(f"\n📂 Font path: {font_path}")
    
    font = pygame.font.Font(font_path, 18)
    
    test_text = "आपण सुरू करूया का बाबा, कसा ना घेतो तक्रार"
    
    # Test different rendering options
    rendering_tests = [
        ("Antialias=True, White", True, (255, 255, 255)),
        ("Antialias=False, White", False, (255, 255, 255)),
        ("Antialias=True, Gray", True, (150, 150, 150)),
        ("Antialias=True, Red", True, (255, 0, 0)),
    ]
    
    surfaces = []
    for label, antialias, color in rendering_tests:
        surface = font.render(test_text, antialias, color)
        surfaces.append((label, surface))
        print(f"✅ {label:30s} -> {surface.get_size()}")
    
    # Render
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        
        screen.fill((0, 0, 0))
        
        y = 50
        for label, surface in surfaces:
            # Label
            label_font = pygame.font.Font(None, 16)
            label_surface = label_font.render(label, True, (100, 100, 100))
            screen.blit(label_surface, (20, y))
            
            # Text
            screen.blit(surface, (20, y + 20))
            
            y += 80
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    print("✅ Direct rendering test complete")


def main():
    print("\n🔬" + "="*58 + "🔬")
    print("  EXACT RENDERING SIMULATION TEST SUITE")
    print("🔬" + "="*58 + "🔬")
    
    # Test 1: Direct rendering
    test_direct_font_rendering()
    
    # Test 2: Exact simulation
    test_exact_rendering()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
