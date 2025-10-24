"""
Test Case: Pygame Text Rendering Diagnostics
Identifies font encoding and Unicode support issues
"""
import pygame
import sys
import os

# Add parent to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.styles import *


def test_font_loading():
    """Test 1: Font Loading and System Font Detection"""
    print("\n" + "="*60)
    print("TEST 1: Font Loading and System Font Detection")
    print("="*60)
    
    pygame.font.init()
    
    # Get all system fonts
    available_fonts = pygame.font.get_fonts()
    print(f"\n✅ Total system fonts available: {len(available_fonts)}")
    
    # Check for common Unicode-supporting fonts
    unicode_fonts = [
        'segoeui', 'arial', 'arialunicodems', 'noto', 'notosans',
        'dejavusans', 'freesans', 'liberation', 'mangal', 'kokila'
    ]
    
    found_unicode_fonts = [f for f in unicode_fonts if f in available_fonts]
    print(f"\n📝 Unicode-capable fonts found: {found_unicode_fonts}")
    
    # Try to load Segoe UI
    segoe_path = pygame.font.match_font('segoeui')
    print(f"\n🔍 Segoe UI path: {segoe_path}")
    
    if segoe_path:
        font = pygame.font.Font(segoe_path, 18)
        print(f"✅ Segoe UI loaded successfully")
    else:
        print(f"⚠️ Segoe UI not found, using default")
        font = pygame.font.Font(None, 18)
    
    return font, available_fonts


def test_unicode_rendering(font):
    """Test 2: Unicode Character Rendering"""
    print("\n" + "="*60)
    print("TEST 2: Unicode Character Rendering")
    print("="*60)
    
    # Test various scripts
    test_strings = {
        'English': 'Hello World',
        'Hindi/Devanagari': 'आपण सुरू करूया का बाबा, कसा ना घेतो तक्रार',
        'Arabic': 'مرحبا بك',
        'Chinese': '你好世界',
        'Emoji': '🎵 ▶ ⏸ ⏭',
        'Symbols': '□ ■ ◆ ◇'
    }
    
    results = {}
    
    for script, text in test_strings.items():
        try:
            # Try to render
            surface = font.render(text, True, (255, 255, 255))
            width, height = surface.get_size()
            
            # Check if it rendered (not just boxes)
            # If all characters are boxes, width will be suspiciously uniform
            expected_width = len(text) * 10  # Rough estimate
            
            if width > 0:
                results[script] = {
                    'success': True,
                    'width': width,
                    'height': height,
                    'text': text
                }
                print(f"✅ {script:20s} - Rendered ({width}x{height}px)")
            else:
                results[script] = {'success': False, 'error': 'Zero width'}
                print(f"❌ {script:20s} - Failed (zero width)")
        
        except Exception as e:
            results[script] = {'success': False, 'error': str(e)}
            print(f"❌ {script:20s} - Error: {e}")
    
    return results


def test_font_alternatives():
    """Test 3: Alternative Font Loading for Unicode"""
    print("\n" + "="*60)
    print("TEST 3: Alternative Unicode Fonts")
    print("="*60)
    
    # Fonts known to support Hindi/Devanagari
    hindi_fonts = [
        'mangal',          # Windows Hindi font
        'kokila',          # Windows Hindi font
        'nirmalaui',       # Windows 10+ Hindi font
        'notosansdevanagari',  # Google Noto
        'dejavusans',      # DejaVu Sans (good Unicode support)
        'arialunicodems',  # Arial Unicode MS
    ]
    
    loaded_fonts = {}
    
    for font_name in hindi_fonts:
        font_path = pygame.font.match_font(font_name)
        if font_path:
            try:
                font = pygame.font.Font(font_path, 18)
                
                # Test Hindi rendering
                test_text = 'आपण सुरू करूया'
                surface = font.render(test_text, True, (255, 255, 255))
                
                loaded_fonts[font_name] = {
                    'path': font_path,
                    'font': font,
                    'width': surface.get_width()
                }
                print(f"✅ {font_name:25s} - Loaded ({font_path})")
                print(f"   Hindi test width: {surface.get_width()}px")
            except Exception as e:
                print(f"⚠️ {font_name:25s} - Error: {e}")
        else:
            print(f"❌ {font_name:25s} - Not found")
    
    return loaded_fonts


def test_current_lyrics():
    """Test 4: Current Lyrics Text Analysis"""
    print("\n" + "="*60)
    print("TEST 4: Current Lyrics Text Analysis")
    print("="*60)
    
    # Sample lyric from your screenshot
    sample_lyric = "आपण सुरू करूया का बाबा, कसा ना घेतो तक्रार"
    
    print(f"\nSample lyric: {sample_lyric}")
    print(f"Length: {len(sample_lyric)} characters")
    
    # Analyze characters
    char_info = []
    for char in sample_lyric:
        unicode_code = ord(char)
        unicode_name = f"U+{unicode_code:04X}"
        char_info.append({
            'char': char,
            'code': unicode_code,
            'name': unicode_name,
            'is_devanagari': 0x0900 <= unicode_code <= 0x097F
        })
    
    # Count character types
    devanagari_count = sum(1 for c in char_info if c['is_devanagari'])
    ascii_count = sum(1 for c in char_info if ord(c['char']) < 128)
    
    print(f"\n📊 Character breakdown:")
    print(f"   Devanagari (Hindi): {devanagari_count}")
    print(f"   ASCII (Latin): {ascii_count}")
    print(f"   Other: {len(sample_lyric) - devanagari_count - ascii_count}")
    
    # Show first 10 characters
    print(f"\n🔍 First 10 characters:")
    for i, info in enumerate(char_info[:10]):
        marker = "🟢 Devanagari" if info['is_devanagari'] else "⚪ Other"
        print(f"   {i+1}. '{info['char']}' - {info['name']} - {marker}")
    
    return char_info


def test_visual_rendering():
    """Test 5: Visual Rendering Test Window"""
    print("\n" + "="*60)
    print("TEST 5: Visual Rendering Test")
    print("="*60)
    print("Opening test window... (Close window to continue)")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Font Rendering Test")
    clock = pygame.time.Clock()
    
    # Test text
    test_text = "आपण सुरू करूया का बाबा, कसा ना घेतो तक्रार"
    
    # Try different fonts
    fonts_to_test = []
    
    # Default font
    fonts_to_test.append(('Default', pygame.font.Font(None, 24)))
    
    # System fonts
    for font_name in ['segoeui', 'mangal', 'kokila', 'nirmalaui', 'arial']:
        font_path = pygame.font.match_font(font_name)
        if font_path:
            fonts_to_test.append((font_name, pygame.font.Font(font_path, 24)))
    
    print(f"\n✅ Testing {len(fonts_to_test)} fonts")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        screen.fill((0, 0, 0))
        
        # Title
        title_font = pygame.font.Font(None, 32)
        title = title_font.render("Font Rendering Test - Press ESC to close", True, (255, 255, 255))
        screen.blit(title, (20, 20))
        
        # Test each font
        y = 80
        for font_name, font in fonts_to_test:
            # Font name
            label_font = pygame.font.Font(None, 20)
            label = label_font.render(f"{font_name}:", True, (150, 150, 150))
            screen.blit(label, (20, y))
            
            # Test text
            try:
                text_surface = font.render(test_text, True, (255, 255, 255))
                screen.blit(text_surface, (150, y))
            except Exception as e:
                error_surface = label_font.render(f"Error: {str(e)}", True, (255, 0, 0))
                screen.blit(error_surface, (150, y))
            
            y += 40
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    print("✅ Visual test complete")


def main():
    """Run all diagnostic tests"""
    print("\n" + "🔬" + "="*58 + "🔬")
    print("  PYGAME TEXT RENDERING DIAGNOSTIC SUITE")
    print("  Identifying font encoding and Unicode issues")
    print("🔬" + "="*58 + "🔬")
    
    try:
        # Test 1: Font loading
        font, available_fonts = test_font_loading()
        
        # Test 2: Unicode rendering
        unicode_results = test_unicode_rendering(font)
        
        # Test 3: Alternative fonts
        alt_fonts = test_font_alternatives()
        
        # Test 4: Current lyrics analysis
        char_info = test_current_lyrics()
        
        # Test 5: Visual test
        test_visual_rendering()
        
        # Summary
        print("\n" + "="*60)
        print("DIAGNOSIS SUMMARY")
        print("="*60)
        
        # Check if Hindi rendered successfully
        hindi_works = unicode_results.get('Hindi/Devanagari', {}).get('success', False)
        
        if hindi_works:
            print("\n✅ Hindi/Devanagari WORKS with current font")
            print("   Issue might be elsewhere (check lyrics_window.py)")
        else:
            print("\n❌ Hindi/Devanagari DOES NOT WORK with current font")
            print("\n🔧 RECOMMENDED FIXES:")
            
            if alt_fonts:
                best_font = list(alt_fonts.keys())[0]
                print(f"\n   1. Use '{best_font}' font instead of Segoe UI")
                print(f"      Path: {alt_fonts[best_font]['path']}")
                print(f"\n   2. Update pygame_text_renderer.py:")
                print(f"      font_path = pygame.font.match_font('{best_font}')")
            else:
                print("\n   1. Install a Unicode font that supports Devanagari:")
                print("      - Noto Sans Devanagari (Google Fonts)")
                print("      - Mangal (comes with Windows Hindi language pack)")
                print("\n   2. Or use system default with fallback:")
                print("      font = pygame.font.SysFont('arial,segoeui,sans-serif', 18)")
        
        # Check for installed Hindi fonts
        hindi_fonts_available = [name for name in alt_fonts.keys()]
        if hindi_fonts_available:
            print(f"\n✅ Hindi-capable fonts available: {', '.join(hindi_fonts_available)}")
        else:
            print("\n⚠️ No Hindi-capable fonts found on system")
            print("   Install Windows Hindi Language Pack or Noto Sans Devanagari")
    
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("Test suite complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
