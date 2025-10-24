"""
Test Always on Top functionality for Pygame window
Error code 1400 = ERROR_INVALID_WINDOW_HANDLE
"""
import pygame
import ctypes
import time
import sys

def test_window_handle_retrieval():
    """Test if we can get valid window handle from Pygame"""
    print("\n" + "="*70)
    print("TEST 1: Window Handle Retrieval")
    print("="*70)
    
    pygame.init()
    pygame.display.set_caption("Test - Always on Top")
    
    # Create window
    screen = pygame.display.set_mode((400, 300), pygame.HWSURFACE | pygame.DOUBLEBUF)
    print("✅ Pygame window created")
    
    # Try to get window info immediately
    print("\n📍 Attempt 1: Get window handle immediately after creation")
    wm_info = pygame.display.get_wm_info()
    print(f"  WM Info keys: {wm_info.keys()}")
    
    if 'window' in wm_info:
        hwnd = wm_info['window']
        print(f"  ✅ Window handle found: {hwnd} (0x{hwnd:X})")
        print(f"  Handle type: {type(hwnd)}")
        print(f"  Is valid (non-zero): {hwnd != 0}")
    else:
        print("  ❌ No 'window' key in wm_info")
        return False
    
    # Force pygame to process events
    print("\n📍 Attempt 2: After flip() and event pump")
    pygame.display.flip()
    pygame.event.pump()
    time.sleep(0.1)
    
    wm_info2 = pygame.display.get_wm_info()
    hwnd2 = wm_info2.get('window', None)
    if hwnd2:
        print(f"  Window handle: {hwnd2} (0x{hwnd2:X})")
        print(f"  Same as before: {hwnd == hwnd2}")
    else:
        print("  ❌ No window handle after flip")
    
    pygame.quit()
    return hwnd != 0

def test_set_window_pos_variations():
    """Test different SetWindowPos approaches"""
    print("\n" + "="*70)
    print("TEST 2: SetWindowPos API Variations")
    print("="*70)
    
    pygame.init()
    screen = pygame.display.set_mode((400, 300), pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.flip()
    pygame.event.pump()
    time.sleep(0.1)
    
    hwnd = pygame.display.get_wm_info()['window']
    print(f"Window handle: {hwnd} (0x{hwnd:X})")
    
    # Windows API constants
    HWND_TOPMOST = -1
    HWND_NOTOPMOST = -2
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_SHOWWINDOW = 0x0040
    SWP_NOACTIVATE = 0x0010
    
    user32 = ctypes.windll.user32
    
    # Test 1: Basic approach
    print("\n📍 Test 1: Basic SetWindowPos (NOMOVE | NOSIZE | SHOWWINDOW)")
    result = user32.SetWindowPos(
        hwnd,
        HWND_TOPMOST,
        0, 0, 0, 0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
    )
    error = ctypes.windll.kernel32.GetLastError()
    print(f"  Result: {result}")
    print(f"  Error code: {error}")
    if error != 0:
        print(f"  Error meaning: {get_error_message(error)}")
    
    # Test 2: With NOACTIVATE
    print("\n📍 Test 2: SetWindowPos with NOACTIVATE flag")
    result = user32.SetWindowPos(
        hwnd,
        HWND_TOPMOST,
        0, 0, 0, 0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
    )
    error = ctypes.windll.kernel32.GetLastError()
    print(f"  Result: {result}")
    print(f"  Error code: {error}")
    if error != 0:
        print(f"  Error meaning: {get_error_message(error)}")
    
    # Test 3: Using actual coordinates
    print("\n📍 Test 3: SetWindowPos with actual coordinates")
    result = user32.SetWindowPos(
        hwnd,
        HWND_TOPMOST,
        100, 100, 400, 300,  # Actual position and size
        SWP_SHOWWINDOW
    )
    error = ctypes.windll.kernel32.GetLastError()
    print(f"  Result: {result}")
    print(f"  Error code: {error}")
    if error != 0:
        print(f"  Error meaning: {get_error_message(error)}")
    
    # Test 4: Check if window is actually topmost
    print("\n📍 Test 4: Verify window extended style")
    GWL_EXSTYLE = -20
    WS_EX_TOPMOST = 0x00000008
    
    ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    print(f"  Extended style: 0x{ex_style:X}")
    print(f"  Has TOPMOST flag: {bool(ex_style & WS_EX_TOPMOST)}")
    
    pygame.quit()

def test_alternative_method():
    """Test alternative method using SetWindowLong"""
    print("\n" + "="*70)
    print("TEST 3: Alternative Method (SetWindowLong)")
    print("="*70)
    
    pygame.init()
    screen = pygame.display.set_mode((400, 300), pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.flip()
    pygame.event.pump()
    time.sleep(0.1)
    
    hwnd = pygame.display.get_wm_info()['window']
    print(f"Window handle: {hwnd} (0x{hwnd:X})")
    
    user32 = ctypes.windll.user32
    
    # Get current extended style
    GWL_EXSTYLE = -20
    WS_EX_TOPMOST = 0x00000008
    
    print("\n📍 Step 1: Get current extended style")
    ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    print(f"  Current ex_style: 0x{ex_style:X}")
    
    print("\n📍 Step 2: Add TOPMOST flag")
    new_style = ex_style | WS_EX_TOPMOST
    result = user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
    print(f"  SetWindowLong result: {result}")
    print(f"  Previous style: 0x{result:X}")
    
    print("\n📍 Step 3: Verify new style")
    verify_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    print(f"  New ex_style: 0x{verify_style:X}")
    print(f"  Has TOPMOST: {bool(verify_style & WS_EX_TOPMOST)}")
    
    # Need to update window for changes to take effect
    print("\n📍 Step 4: Update window position to apply changes")
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_NOZORDER = 0x0004
    SWP_FRAMECHANGED = 0x0020
    
    result = user32.SetWindowPos(
        hwnd, 0, 0, 0, 0, 0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED
    )
    error = ctypes.windll.kernel32.GetLastError()
    print(f"  SetWindowPos result: {result}")
    print(f"  Error code: {error}")
    
    pygame.quit()

def test_timing_issue():
    """Test if timing affects success"""
    print("\n" + "="*70)
    print("TEST 4: Timing Test (Delays)")
    print("="*70)
    
    pygame.init()
    screen = pygame.display.set_mode((400, 300), pygame.HWSURFACE | pygame.DOUBLEBUF)
    
    delays = [0, 0.05, 0.1, 0.2, 0.5]
    
    for delay in delays:
        print(f"\n📍 Testing with {delay}s delay:")
        
        if delay > 0:
            pygame.display.flip()
            pygame.event.pump()
            time.sleep(delay)
        
        hwnd = pygame.display.get_wm_info()['window']
        
        user32 = ctypes.windll.user32
        HWND_TOPMOST = -1
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_SHOWWINDOW = 0x0040
        
        result = user32.SetWindowPos(
            hwnd, HWND_TOPMOST,
            0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
        )
        error = ctypes.windll.kernel32.GetLastError()
        
        print(f"  Result: {result}, Error: {error}")
        if result != 0:
            print(f"  ✅ SUCCESS at {delay}s delay!")
            break
    
    pygame.quit()

def get_error_message(error_code):
    """Get Windows error message for error code"""
    error_messages = {
        0: "No error",
        1400: "ERROR_INVALID_WINDOW_HANDLE - Invalid window handle",
        1401: "ERROR_INVALID_MENU_HANDLE",
        1402: "ERROR_INVALID_CURSOR_HANDLE",
        5: "ERROR_ACCESS_DENIED",
        6: "ERROR_INVALID_HANDLE",
    }
    return error_messages.get(error_code, f"Unknown error {error_code}")

def test_manual_topmost():
    """Manual visual test - keep window open to test topmost"""
    print("\n" + "="*70)
    print("TEST 5: Manual Visual Test")
    print("="*70)
    print("\nInstructions:")
    print("  1. Window will stay open for 10 seconds")
    print("  2. Try clicking on other windows")
    print("  3. Check if this window stays on top")
    print("  4. Close manually or wait 10 seconds")
    print("\nStarting in 2 seconds...")
    time.sleep(2)
    
    pygame.init()
    screen = pygame.display.set_mode((500, 300), pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption("🎵 Always on Top Test - Try clicking other windows!")
    
    # Fill with visible color
    screen.fill((50, 50, 100))
    font = pygame.font.SysFont("Arial", 24)
    text = font.render("Always on Top Test Window", True, (255, 255, 255))
    text_rect = text.get_rect(center=(250, 150))
    screen.blit(text, text_rect)
    
    pygame.display.flip()
    pygame.event.pump()
    time.sleep(0.2)
    
    # Apply always on top
    hwnd = pygame.display.get_wm_info()['window']
    print(f"\nWindow handle: {hwnd} (0x{hwnd:X})")
    
    user32 = ctypes.windll.user32
    HWND_TOPMOST = -1
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_SHOWWINDOW = 0x0040
    
    result = user32.SetWindowPos(
        hwnd, HWND_TOPMOST,
        0, 0, 0, 0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
    )
    
    error = ctypes.windll.kernel32.GetLastError()
    print(f"SetWindowPos result: {result}")
    print(f"Error code: {error}")
    
    if result != 0:
        print("✅ Always on Top applied successfully!")
        print("Try opening other windows - this should stay on top")
    else:
        print(f"❌ Failed: {get_error_message(error)}")
    
    # Keep window open
    clock = pygame.time.Clock()
    running = True
    start_time = time.time()
    
    while running and (time.time() - start_time < 10):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        clock.tick(60)
    
    pygame.quit()
    print("\n✅ Test complete!")

if __name__ == "__main__":
    try:
        print("="*70)
        print("DIAGNOSING ALWAYS ON TOP ISSUE")
        print("="*70)
        
        # Run tests
        test_window_handle_retrieval()
        test_set_window_pos_variations()
        test_alternative_method()
        test_timing_issue()
        
        # Manual test
        response = input("\n\nRun manual visual test? (y/n): ")
        if response.lower() == 'y':
            test_manual_topmost()
        
        print("\n" + "="*70)
        print("ALL TESTS COMPLETE")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
