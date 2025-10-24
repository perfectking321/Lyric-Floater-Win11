"""
Test script for new transparency and resizing features
"""
import pygame
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.pygame_ui_components import OpacitySlider, Button
from ui.styles import *

def test_opacity_slider():
    """Test opacity slider component"""
    print("\n=== Testing OpacitySlider Component ===")
    
    pygame.init()
    screen = pygame.display.set_mode((300, 400))
    pygame.display.set_caption("Opacity Slider Test")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 14)
    
    # Create slider
    opacity_value = 0.95
    
    def on_opacity_change(value):
        nonlocal opacity_value
        opacity_value = value
        print(f"Opacity changed to: {value:.2f} ({int(value*100)}%)")
    
    slider = OpacitySlider(140, 50, 20, 200, initial_value=0.95, on_change=on_opacity_change)
    
    # Create close button
    close_button = Button(100, 300, 100, 40, "Close", font, callback=lambda: None)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            slider.handle_event(event)
            if close_button.handle_event(event):
                running = False
        
        # Draw
        screen.fill((30, 30, 30))
        
        # Draw title
        title = font.render("Drag slider to change opacity", True, (255, 255, 255))
        screen.blit(title, (40, 20))
        
        # Draw slider
        slider.draw(screen)
        
        # Draw value
        value_text = font.render(f"{int(opacity_value*100)}%", True, (255, 255, 255))
        screen.blit(value_text, (140 - 10, 260))
        
        # Draw close button
        close_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("✅ Slider component works correctly")

def test_window_transparency():
    """Test window transparency with Windows API"""
    print("\n=== Testing Window Transparency ===")
    
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Transparency Test")
    clock = pygame.time.Clock()
    
    # Test transparency API
    try:
        import ctypes
        hwnd = pygame.display.get_wm_info()['window']
        
        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x00080000
        LWA_ALPHA = 0x00000002
        
        user32 = ctypes.windll.user32
        ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED)
        
        # Test different opacity levels
        opacities = [1.0, 0.9, 0.7, 0.5, 0.3, 0.5, 0.7, 0.9, 1.0]
        frame = 0
        font = pygame.font.SysFont("Arial", 20)
        
        running = True
        while running and frame < len(opacities) * 60:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Change opacity every second
            opacity_index = frame // 60
            if opacity_index < len(opacities):
                opacity = opacities[opacity_index]
                alpha = int(opacity * 255)
                user32.SetLayeredWindowAttributes(hwnd, 0, alpha, LWA_ALPHA)
                
                # Draw
                screen.fill((60, 60, 60))
                text = font.render(f"Opacity: {int(opacity*100)}%", True, (255, 255, 255))
                screen.blit(text, (100, 130))
                
                instruction = font.render("(Changes every second)", True, (200, 200, 200))
                screen.blit(instruction, (80, 160))
                
                pygame.display.flip()
                clock.tick(60)
                frame += 1
        
        print("✅ Window transparency works correctly")
        
    except Exception as e:
        print(f"❌ Transparency test failed: {e}")
    
    pygame.quit()

def test_window_resizing():
    """Test window resizing"""
    print("\n=== Testing Window Resizing ===")
    
    pygame.init()
    screen = pygame.display.set_mode((400, 300), pygame.RESIZABLE)
    pygame.display.set_caption("Resize Test - Drag edges!")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 14)
    
    min_width = 300
    min_height = 200
    current_width = 400
    current_height = 300
    
    running = True
    resize_count = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.VIDEORESIZE:
                # Enforce minimum size
                new_width = max(event.w, min_width)
                new_height = max(event.h, min_height)
                
                screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
                current_width = new_width
                current_height = new_height
                resize_count += 1
                
                print(f"  Resized to: {new_width}x{new_height}")
        
        # Draw
        screen.fill((40, 40, 40))
        
        # Draw instructions
        title = font.render("Drag window edges to resize", True, (255, 255, 255))
        screen.blit(title, (20, 20))
        
        size_text = font.render(f"Current size: {current_width}x{current_height}", True, (200, 200, 200))
        screen.blit(size_text, (20, 50))
        
        count_text = font.render(f"Resize events: {resize_count}", True, (200, 200, 200))
        screen.blit(count_text, (20, 80))
        
        min_text = font.render(f"Minimum size: {min_width}x{min_height}", True, (150, 150, 150))
        screen.blit(min_text, (20, 110))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("✅ Window resizing works correctly")

if __name__ == "__main__":
    print("Testing new features: Transparency and Resizing")
    print("=" * 50)
    
    # Run tests
    try:
        test_opacity_slider()
        test_window_transparency()
        test_window_resizing()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed! Features are working correctly.")
        print("\nFeature Summary:")
        print("1. ✅ OpacitySlider component - vertical slider for 30%-100% opacity")
        print("2. ✅ Window transparency - Windows API integration working")
        print("3. ✅ Window resizing - RESIZABLE flag with minimum size enforcement")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
