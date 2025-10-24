"""
Test Case Suite: Lyrics Display and Controls Bug Diagnosis
Tests for:
1. Lyrics showing in one line (layout issue)
2. Play/Pause button not working
3. Previous/Next buttons not working
"""
import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.pygame_sprite_manager import LyricSpriteManager
from ui.pygame_text_renderer import TextRenderer
from ui.styles import *


def test_sprite_layout():
    """Test 1: Check sprite positioning and layout"""
    print("\n" + "="*60)
    print("TEST 1: Sprite Layout and Positioning")
    print("="*60)
    
    pygame.init()
    
    renderer = TextRenderer()
    sprite_manager = LyricSpriteManager(renderer, 500, 700)
    
    # Load test lyrics
    test_lyrics = [
        "Line 1: You got the feeling",
        "Line 2: You got the feeling",
        "Line 3: You got the feeling",
        "Line 4: You got the feeling",
        "Line 5: You got the feeling"
    ]
    
    print(f"\n📝 Loading {len(test_lyrics)} test lyrics...")
    sprite_manager.load_lyrics(test_lyrics)
    
    print(f"\n🔍 Inspecting sprite positions:")
    print(f"   Line height: {sprite_manager.line_height}px")
    print(f"   Lyrics area Y: {sprite_manager.lyrics_area_y}px")
    print(f"   Lyrics area height: {sprite_manager.lyrics_area_height}px")
    
    for i, sprite in enumerate(sprite_manager.lyric_sprites):
        print(f"\n   Sprite {i+1}:")
        print(f"      Text: {sprite.text[:40]}")
        print(f"      Y position: {sprite.y}")
        print(f"      Target Y: {sprite.target_y}")
        print(f"      Rect: {sprite.rect}")
        print(f"      Width: {sprite.width}")
    
    # Check if they're overlapping
    print(f"\n⚠️ Checking for overlaps:")
    for i in range(len(sprite_manager.lyric_sprites) - 1):
        sprite1 = sprite_manager.lyric_sprites[i]
        sprite2 = sprite_manager.lyric_sprites[i + 1]
        
        gap = sprite2.y - (sprite1.y + sprite1.rect.height)
        if gap < 0:
            print(f"   ❌ OVERLAP: Sprite {i+1} and {i+2} overlap by {abs(gap)}px!")
        elif gap < 5:
            print(f"   ⚠️ TOO CLOSE: Sprite {i+1} and {i+2} only {gap}px apart")
        else:
            print(f"   ✅ OK: Sprite {i+1} and {i+2} gap: {gap}px")
    
    pygame.quit()
    return sprite_manager


def test_line_spacing_calculation():
    """Test 2: Check line spacing calculation"""
    print("\n" + "="*60)
    print("TEST 2: Line Spacing Calculation")
    print("="*60)
    
    print(f"\n📊 Style constants:")
    print(f"   FONT_SIZE: {FONT_SIZE}")
    print(f"   FONT_SIZE_CURRENT: {FONT_SIZE_CURRENT}")
    print(f"   LINE_SPACING: {LINE_SPACING}")
    print(f"   HEADER_HEIGHT: {HEADER_HEIGHT}")
    print(f"   CONTROL_HEIGHT: {CONTROL_HEIGHT}")
    print(f"   LYRICS_PADDING: {LYRICS_PADDING}")
    
    # Calculate expected line height
    expected_line_height = int(FONT_SIZE_CURRENT * LINE_SPACING)
    print(f"\n🔢 Expected line height: {FONT_SIZE_CURRENT} * {LINE_SPACING} = {expected_line_height}px")
    
    # Check if this is reasonable
    if expected_line_height < 20:
        print(f"   ❌ TOO SMALL! Lines will overlap")
        print(f"   ✅ Should be at least 30px for 18pt font")
    elif expected_line_height < 30:
        print(f"   ⚠️ TIGHT: May cause issues")
    else:
        print(f"   ✅ LOOKS GOOD")
    
    return expected_line_height


def test_button_callbacks():
    """Test 3: Check if button callbacks are wired correctly"""
    print("\n" + "="*60)
    print("TEST 3: Button Callback Testing")
    print("="*60)
    
    pygame.init()
    
    # Mock callbacks
    callbacks_called = {
        'play_pause': False,
        'prev': False,
        'next': False
    }
    
    def mock_play_pause():
        callbacks_called['play_pause'] = True
        print("   ✅ Play/Pause callback fired!")
    
    def mock_prev():
        callbacks_called['prev'] = True
        print("   ✅ Previous callback fired!")
    
    def mock_next():
        callbacks_called['next'] = True
        print("   ✅ Next callback fired!")
    
    # Import button component
    from ui.pygame_ui_components import Button
    
    # Create test buttons
    font = pygame.font.Font(None, 18)
    
    play_button = Button(200, 100, 60, 40, "▶", font, callback=mock_play_pause)
    prev_button = Button(100, 100, 50, 40, "⏮", font, callback=mock_prev)
    next_button = Button(300, 100, 50, 40, "⏭", font, callback=mock_next)
    
    print(f"\n🎮 Created test buttons:")
    print(f"   Play button rect: {play_button.rect}")
    print(f"   Prev button rect: {prev_button.rect}")
    print(f"   Next button rect: {next_button.rect}")
    
    # Simulate clicks
    print(f"\n🖱️ Simulating button clicks:")
    
    # Play button click
    print(f"\n   Testing Play/Pause button...")
    mouse_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (230, 120)})
    mouse_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': (230, 120)})
    mouse_motion = pygame.event.Event(pygame.MOUSEMOTION, {'pos': (230, 120)})
    
    play_button.handle_event(mouse_motion)
    play_button.handle_event(mouse_down)
    play_button.handle_event(mouse_up)
    
    if not callbacks_called['play_pause']:
        print(f"      ❌ FAILED: Callback not called!")
    
    # Prev button click
    print(f"\n   Testing Previous button...")
    mouse_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (125, 120)})
    mouse_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': (125, 120)})
    mouse_motion = pygame.event.Event(pygame.MOUSEMOTION, {'pos': (125, 120)})
    
    prev_button.handle_event(mouse_motion)
    prev_button.handle_event(mouse_down)
    prev_button.handle_event(mouse_up)
    
    if not callbacks_called['prev']:
        print(f"      ❌ FAILED: Callback not called!")
    
    # Next button click
    print(f"\n   Testing Next button...")
    mouse_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (325, 120)})
    mouse_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': 1, 'pos': (325, 120)})
    mouse_motion = pygame.event.Event(pygame.MOUSEMOTION, {'pos': (325, 120)})
    
    next_button.handle_event(mouse_motion)
    next_button.handle_event(mouse_down)
    next_button.handle_event(mouse_up)
    
    if not callbacks_called['next']:
        print(f"      ❌ FAILED: Callback not called!")
    
    pygame.quit()
    
    print(f"\n📊 Results:")
    print(f"   Play/Pause: {'✅ WORKS' if callbacks_called['play_pause'] else '❌ BROKEN'}")
    print(f"   Previous: {'✅ WORKS' if callbacks_called['prev'] else '❌ BROKEN'}")
    print(f"   Next: {'✅ WORKS' if callbacks_called['next'] else '❌ BROKEN'}")
    
    return callbacks_called


def test_spotify_controller_methods():
    """Test 4: Check if Spotify controller methods exist"""
    print("\n" + "="*60)
    print("TEST 4: Spotify Controller Method Availability")
    print("="*60)
    
    try:
        from controllers.spotify_controller import SpotifyController
        
        print(f"\n🔍 Checking SpotifyController methods:")
        
        required_methods = ['play', 'pause', 'next', 'previous', 'seek_to_position']
        
        for method in required_methods:
            if hasattr(SpotifyController, method):
                print(f"   ✅ {method:20s} - EXISTS")
            else:
                print(f"   ❌ {method:20s} - MISSING!")
        
    except Exception as e:
        print(f"   ❌ Error importing SpotifyController: {e}")


def main():
    """Run all tests"""
    print("\n🔬" + "="*58 + "🔬")
    print("  LYRICS DISPLAY & CONTROLS BUG DIAGNOSTIC SUITE")
    print("🔬" + "="*58 + "🔬")
    
    # Test 1: Layout
    sprite_manager = test_sprite_layout()
    
    # Test 2: Line spacing
    expected_height = test_line_spacing_calculation()
    
    # Test 3: Button callbacks
    callbacks = test_button_callbacks()
    
    # Test 4: Spotify methods
    test_spotify_controller_methods()
    
    # Summary
    print("\n" + "="*60)
    print("DIAGNOSIS SUMMARY")
    print("="*60)
    
    # Issue 1: Single line lyrics
    if sprite_manager:
        if sprite_manager.line_height < 30:
            print(f"\n❌ ISSUE 1: Line Height Too Small")
            print(f"   Current: {sprite_manager.line_height}px")
            print(f"   Should be: 30-40px")
            print(f"\n   🔧 FIX: Update styles.py")
            print(f"      LINE_SPACING = 2.0  (currently {LINE_SPACING})")
        else:
            print(f"\n✅ Line height looks OK: {sprite_manager.line_height}px")
    
    # Issue 2: Button callbacks
    all_buttons_work = all(callbacks.values())
    if not all_buttons_work:
        print(f"\n❌ ISSUE 2: Button Callbacks")
        if not callbacks['play_pause']:
            print(f"   Play/Pause button broken")
        if not callbacks['prev']:
            print(f"   Previous button broken")
        if not callbacks['next']:
            print(f"   Next button broken")
    else:
        print(f"\n✅ Button callbacks work in isolation")
        print(f"   Issue might be in pygame_lyrics_window.py event handling")
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
