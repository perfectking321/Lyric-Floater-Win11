"""
Test Always on Top behavior during window resize
Diagnose if topmost status is lost when window is resized
"""
import pygame
import ctypes
from ctypes import wintypes
import time

def check_topmost_status(hwnd):
    """Check if window has TOPMOST flag"""
    user32 = ctypes.windll.user32
    GWL_EXSTYLE = -20
    WS_EX_TOPMOST = 0x00000008
    
    ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    is_topmost = bool(ex_style & WS_EX_TOPMOST)
    return is_topmost, ex_style

def set_always_on_top(hwnd):
    """Set window to always on top"""
    user32 = ctypes.windll.user32
    
    # Proper type casting
    hwnd = ctypes.c_void_p(hwnd)
    HWND_TOPMOST = ctypes.c_void_p(-1)
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_SHOWWINDOW = 0x0040
    
    # Define function signature
    user32.SetWindowPos.argtypes = [
        wintypes.HWND, wintypes.HWND,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        wintypes.UINT
    ]
    user32.SetWindowPos.restype = wintypes.BOOL
    
    result = user32.SetWindowPos(
        hwnd, HWND_TOPMOST,
        0, 0, 0, 0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
    )
    
    return bool(result)

def test_resize_topmost_behavior():
    """Test if topmost is lost during resize"""
    print("\n" + "="*70)
    print("TEST: Always on Top During Window Resize")
    print("="*70)
    
    pygame.init()
    
    # Create resizable window
    screen = pygame.display.set_mode((600, 400), pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption("Resize Test - Always on Top")
    pygame.display.flip()
    pygame.event.pump()
    time.sleep(0.1)
    
    # Get window handle
    hwnd = pygame.display.get_wm_info()['window']
    print(f"\n📌 Window handle: {hwnd} (0x{hwnd:X})")
    
    # Check initial topmost status
    print("\n📍 Step 1: Initial Status")
    is_topmost, ex_style = check_topmost_status(hwnd)
    print(f"  Is Topmost: {is_topmost}")
    print(f"  Extended Style: 0x{ex_style:X}")
    
    # Set always on top
    print("\n📍 Step 2: Setting Always on Top")
    result = set_always_on_top(hwnd)
    print(f"  SetWindowPos result: {result}")
    
    time.sleep(0.1)
    is_topmost, ex_style = check_topmost_status(hwnd)
    print(f"  Is Topmost now: {is_topmost}")
    print(f"  Extended Style: 0x{ex_style:X}")
    
    if not is_topmost:
        print("  ⚠️ WARNING: Topmost flag not set!")
        return
    
    print("  ✅ Always on Top enabled")
    
    # Test manual resize via set_mode
    print("\n📍 Step 3: Testing Resize via set_mode()")
    sizes = [
        (500, 350, "Smaller"),
        (700, 500, "Larger"),
        (600, 400, "Original")
    ]
    
    for width, height, desc in sizes:
        print(f"\n  Resizing to {width}x{height} ({desc})...")
        screen = pygame.display.set_mode((width, height), pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.flip()
        pygame.event.pump()
        time.sleep(0.2)
        
        # Check if handle changed
        new_hwnd = pygame.display.get_wm_info()['window']
        print(f"    Window handle: {new_hwnd} (0x{new_hwnd:X})")
        print(f"    Handle changed: {new_hwnd != hwnd}")
        
        # Check topmost status
        is_topmost, ex_style = check_topmost_status(new_hwnd)
        print(f"    Is Topmost: {is_topmost}")
        print(f"    Extended Style: 0x{ex_style:X}")
        
        if not is_topmost:
            print(f"    ❌ Lost topmost status after resize!")
        else:
            print(f"    ✅ Still topmost")
    
    # Interactive test
    print("\n" + "="*70)
    print("📍 Step 4: Interactive Resize Test")
    print("="*70)
    print("\nInstructions:")
    print("  1. Try resizing the window by dragging edges")
    print("  2. Watch the console for status updates")
    print("  3. Press ESC to exit")
    print("\nStarting in 2 seconds...")
    time.sleep(2)
    
    clock = pygame.time.Clock()
    running = True
    last_size = (screen.get_width(), screen.get_height())
    resize_count = 0
    
    # Set always on top again before interactive test
    hwnd = pygame.display.get_wm_info()['window']
    set_always_on_top(hwnd)
    
    print("\n🎯 Monitoring window resizes...")
    print("   Current topmost status will be checked on each resize event\n")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.VIDEORESIZE:
                resize_count += 1
                new_size = (event.w, event.h)
                
                print(f"\n🔄 Resize #{resize_count}: {last_size} → {new_size}")
                
                # Update screen size
                screen = pygame.display.set_mode(new_size, pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF)
                
                # Check topmost status AFTER resize
                hwnd = pygame.display.get_wm_info()['window']
                is_topmost, ex_style = check_topmost_status(hwnd)
                
                print(f"   Window handle: {hwnd} (0x{hwnd:X})")
                print(f"   Is Topmost: {is_topmost}")
                print(f"   Extended Style: 0x{ex_style:X}")
                
                if not is_topmost:
                    print(f"   ❌ TOPMOST LOST! Attempting to restore...")
                    result = set_always_on_top(hwnd)
                    if result:
                        print(f"   ✅ Topmost restored")
                    else:
                        print(f"   ❌ Failed to restore topmost")
                else:
                    print(f"   ✅ Topmost preserved")
                
                last_size = new_size
        
        # Fill screen with color
        screen.fill((30, 30, 60))
        
        # Draw text
        font = pygame.font.SysFont("Arial", 16)
        texts = [
            f"Resize Count: {resize_count}",
            f"Current Size: {screen.get_width()}x{screen.get_height()}",
            "Try resizing by dragging edges",
            "Press ESC to exit"
        ]
        
        y = 50
        for text in texts:
            surf = font.render(text, True, (255, 255, 255))
            screen.blit(surf, (20, y))
            y += 30
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    
    print("\n" + "="*70)
    print(f"Test complete! Total resizes: {resize_count}")
    print("="*70)

def test_videoresize_event():
    """Test VIDEORESIZE event handling"""
    print("\n" + "="*70)
    print("TEST: VIDEORESIZE Event Analysis")
    print("="*70)
    
    pygame.init()
    screen = pygame.display.set_mode((600, 400), pygame.RESIZABLE)
    pygame.display.set_caption("VIDEORESIZE Event Test")
    
    hwnd = pygame.display.get_wm_info()['window']
    set_always_on_top(hwnd)
    
    print("\n✅ Window created with Always on Top")
    print("📖 Resize the window and observe the event sequence\n")
    
    clock = pygame.time.Clock()
    running = True
    event_count = 0
    
    while running:
        for event in pygame.event.get():
            event_count += 1
            
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.VIDEORESIZE:
                print(f"\n🔄 Event #{event_count}: VIDEORESIZE")
                print(f"   New size: {event.w}x{event.h}")
                print(f"   Event dict: {event.dict}")
                
                # Check topmost BEFORE set_mode
                hwnd_before = pygame.display.get_wm_info()['window']
                topmost_before, style_before = check_topmost_status(hwnd_before)
                print(f"   BEFORE set_mode:")
                print(f"     Handle: {hwnd_before} (0x{hwnd_before:X})")
                print(f"     Topmost: {topmost_before}")
                
                # Resize screen
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                
                # Check topmost AFTER set_mode
                hwnd_after = pygame.display.get_wm_info()['window']
                topmost_after, style_after = check_topmost_status(hwnd_after)
                print(f"   AFTER set_mode:")
                print(f"     Handle: {hwnd_after} (0x{hwnd_after:X})")
                print(f"     Handle changed: {hwnd_before != hwnd_after}")
                print(f"     Topmost: {topmost_after}")
                
                if not topmost_after:
                    print(f"   ❌ Topmost lost during set_mode!")
                    print(f"   🔧 Restoring topmost...")
                    set_always_on_top(hwnd_after)
        
        screen.fill((40, 40, 80))
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    try:
        print("="*70)
        print("DIAGNOSING ALWAYS ON TOP DURING RESIZE")
        print("="*70)
        
        # Run first test
        test_resize_topmost_behavior()
        
        # Ask for second test
        # response = input("\n\nRun VIDEORESIZE event analysis? (y/n): ")
        # if response.lower() == 'y':
        #     test_videoresize_event()
        
        print("\n✅ All tests complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
