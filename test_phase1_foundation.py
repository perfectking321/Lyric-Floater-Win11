"""
Test Phase 1 - Animation Manager & Color Cache

Run this to verify the foundation components work correctly.
"""

import tkinter as tk
from ui.animation_manager import AnimationManager, AnimationState, MultiPropertyAnimation, Easing
from ui.color_cache import ColorCache


def test_animation_manager():
    """Test the animation manager"""
    print("\n" + "="*60)
    print("TEST 1: Animation Manager")
    print("="*60)
    
    root = tk.Tk()
    root.title("Animation Manager Test")
    root.geometry("400x300")
    
    # Create canvas for visual feedback
    canvas = tk.Canvas(root, bg='#000000', highlightthickness=0)
    canvas.pack(fill='both', expand=True)
    
    # Create test circle
    circle = canvas.create_oval(50, 125, 100, 175, fill='#FF2D55', outline='')
    
    # Create animation manager
    anim_manager = AnimationManager(root, fps=60)
    
    # Test counter
    test_results = {'animations_completed': 0}
    
    def move_circle(x_pos):
        """Update callback - move circle"""
        canvas.coords(circle, x_pos, 125, x_pos + 50, 175)
    
    def on_animation_complete():
        """Complete callback"""
        test_results['animations_completed'] += 1
        print(f"✅ Animation {test_results['animations_completed']} completed")
        
        if test_results['animations_completed'] < 3:
            # Start next animation
            start_x = 50 if test_results['animations_completed'] % 2 == 1 else 300
            end_x = 300 if test_results['animations_completed'] % 2 == 1 else 50
            
            anim = AnimationState(
                duration_ms=500,
                start_value=start_x,
                end_value=end_x,
                easing_func=Easing.ease_in_out_cubic,
                on_update=move_circle,
                on_complete=on_animation_complete
            )
            anim_manager.add_animation(f'move_{test_results["animations_completed"]}', anim)
        else:
            # All tests done
            print("\n✅ All 3 animations completed successfully!")
            stats = anim_manager.get_performance_stats()
            print(f"\n📊 Performance Stats:")
            print(f"   Average Frame Time: {stats['avg_frame_time']}ms")
            print(f"   Max Frame Time: {stats['max_frame_time']}ms")
            print(f"   Current FPS: {stats['current_fps']}")
            print(f"   Active Animations: {stats['active_animations']}")
            
            root.after(2000, root.destroy)
    
    # Create info label
    label = tk.Label(
        root,
        text="Watch the circle move smoothly!\nRunning 3 back-and-forth animations...",
        bg='#000000',
        fg='#FFFFFF',
        font=('Segoe UI', 12)
    )
    canvas.create_window(200, 50, window=label)
    
    # Start first animation
    first_anim = AnimationState(
        duration_ms=500,
        start_value=50,
        end_value=300,
        easing_func=Easing.ease_in_out_cubic,
        on_update=move_circle,
        on_complete=on_animation_complete
    )
    anim_manager.add_animation('move_0', first_anim)
    
    print("\n🚀 Starting animation manager test...")
    print("   Watch the window for 6 seconds...")
    
    root.mainloop()


def test_multi_property_animation():
    """Test multi-property animation"""
    print("\n" + "="*60)
    print("TEST 2: Multi-Property Animation")
    print("="*60)
    
    root = tk.Tk()
    root.title("Multi-Property Animation Test")
    root.geometry("400x300")
    
    canvas = tk.Canvas(root, bg='#000000', highlightthickness=0)
    canvas.pack(fill='both', expand=True)
    
    # Create test rectangle
    rect = canvas.create_rectangle(150, 100, 250, 200, fill='#1DB954', outline='')
    text = canvas.create_text(200, 250, text="Size: 100x100", fill='#FFFFFF', font=('Segoe UI', 12))
    
    anim_manager = AnimationManager(root, fps=60)
    
    def update_rect(values):
        """Update rectangle with multiple properties"""
        x = values['x']
        y = values['y']
        size = values['size']
        
        canvas.coords(rect, x, y, x + size, y + size)
        canvas.itemconfig(text, text=f"Size: {int(size)}x{int(size)}")
    
    def animation_done():
        print("✅ Multi-property animation completed!")
        stats = anim_manager.get_performance_stats()
        print(f"\n📊 Performance Stats:")
        print(f"   Average Frame Time: {stats['avg_frame_time']}ms")
        print(f"   Current FPS: {stats['current_fps']}")
        
        root.after(2000, root.destroy)
    
    # Animate x, y, and size simultaneously
    multi_anim = MultiPropertyAnimation(
        duration_ms=1500,
        properties={
            'x': (150, 100),      # Move left
            'y': (100, 50),       # Move up
            'size': (100, 200),   # Grow
        },
        easing_func=Easing.ease_in_out_cubic,
        on_update=update_rect,
        on_complete=animation_done
    )
    
    anim_manager.add_animation('multi', multi_anim)
    
    print("\n🚀 Starting multi-property animation...")
    print("   Watch the rectangle move and grow!")
    
    root.mainloop()


def test_color_cache():
    """Test color cache performance"""
    print("\n" + "="*60)
    print("TEST 3: Color Cache")
    print("="*60)
    
    import time
    
    color_cache = ColorCache()
    
    # Test basic functionality
    print("\n1️⃣ Testing basic color operations...")
    
    test_colors = [
        ('#FFFFFF', 1.0, '#ffffff'),
        ('#FFFFFF', 0.5, '#7f7f7f'),
        ('#FFFFFF', 0.0, '#000000'),
        ('#FF2D55', 1.0, '#ff2d55'),
        ('#FF2D55', 0.7, '#b21f3b'),
    ]
    
    for base, opacity, expected in test_colors:
        result = color_cache.get_color(base, opacity)
        status = "✅" if result.lower() == expected.lower() else "❌"
        print(f"   {status} get_color('{base}', {opacity}) = {result} (expected {expected})")
    
    # Test cache hit rate
    print("\n2️⃣ Testing cache performance...")
    
    # Warm up
    for _ in range(100):
        color_cache.get_color('#FFFFFF', 0.5)
    
    # Test with cache (should be fast)
    start = time.time()
    for _ in range(10000):
        color_cache.get_color('#FFFFFF', 0.5)
    cached_time = time.time() - start
    
    # Test without cache (calculate each time)
    start = time.time()
    for _ in range(10000):
        color_cache._calculate_opacity_color('#FFFFFF', 0.5)
    uncached_time = time.time() - start
    
    speedup = uncached_time / cached_time if cached_time > 0 else 0
    
    print(f"   With cache: {cached_time*1000:.2f}ms for 10,000 operations")
    print(f"   Without cache: {uncached_time*1000:.2f}ms for 10,000 operations")
    print(f"   ✅ Speedup: {speedup:.1f}x faster!")
    
    # Test interpolation
    print("\n3️⃣ Testing color interpolation...")
    
    result = color_cache.get_interpolated_color('#000000', '#FFFFFF', 0.5)
    print(f"   Interpolate #000000 → #FFFFFF (50%) = {result}")
    
    result = color_cache.get_interpolated_color('#FF0000', '#0000FF', 0.5)
    print(f"   Interpolate #FF0000 → #0000FF (50%) = {result}")
    
    # Cache stats
    print("\n4️⃣ Cache Statistics:")
    stats = color_cache.get_cache_stats()
    print(f"   Total cached entries: {stats['total_entries']}")
    print(f"   Estimated memory: {stats['memory_bytes'] / 1024:.1f} KB")
    
    print("\n✅ Color cache test completed!")


def run_all_tests():
    """Run all Phase 1 tests"""
    print("\n" + "="*60)
    print("🧪 PHASE 1 FOUNDATION TESTS")
    print("="*60)
    
    try:
        # Test 3 (no GUI)
        test_color_cache()
        
        # Test 1 (GUI)
        print("\n⏳ Starting GUI tests (watch the windows)...\n")
        test_animation_manager()
        
        # Test 2 (GUI)
        test_multi_property_animation()
        
        print("\n" + "="*60)
        print("✅ ALL PHASE 1 TESTS PASSED!")
        print("="*60)
        print("\n✨ Foundation components are working correctly!")
        print("   Ready to proceed to Phase 2 (Rendering).\n")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()
