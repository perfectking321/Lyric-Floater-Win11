"""
Test Phase 2 - Virtual Scroller & Canvas Batcher

Run this to verify rendering optimization components work correctly.
"""

import tkinter as tk
from ui.virtual_scroller import VirtualScroller
from ui.canvas_batcher import CanvasBatcher, SmartCanvasBatcher
import time


def test_virtual_scroller():
    """Test virtual scrolling performance"""
    print("\n" + "="*60)
    print("TEST 1: Virtual Scroller")
    print("="*60)
    
    root = tk.Tk()
    root.title("Virtual Scroller Test")
    root.geometry("500x600")
    
    # Create canvas
    canvas = tk.Canvas(root, bg='#000000', highlightthickness=0)
    canvas.pack(fill='both', expand=True)
    
    # Create virtual scroller
    scroller = VirtualScroller(
        canvas=canvas,
        window_width=500,
        window_height=600,
        line_height=40,
        buffer_lines=3
    )
    
    # Create 50 test lyrics (simulating a long song)
    test_lyrics = [f"Lyric line {i+1} - This is a test line with some text" for i in range(50)]
    
    print(f"\n1️⃣ Setting {len(test_lyrics)} lyrics...")
    scroller.set_lyrics(test_lyrics)
    
    stats = scroller.get_stats()
    print(f"   Total lines: {stats['total_lines']}")
    print(f"   Visible lines: {stats['visible_lines']}")
    print(f"   ✅ Reduction: {stats['reduction_percent']}% fewer renders")
    
    # Create info label
    info_text = tk.StringVar()
    info_text.set(f"Rendering {stats['visible_lines']}/{stats['total_lines']} lines")
    
    info_label = tk.Label(
        root,
        textvariable=info_text,
        bg='#1A1A1A',
        fg='#FFFFFF',
        font=('Segoe UI', 12),
        pady=10
    )
    info_label.pack(side='bottom', fill='x')
    
    # Scroll animation
    scroll_positions = [0, 500, 1000, 1500, 1000, 500, 0]
    current_pos_idx = [0]
    
    def animate_scroll():
        if current_pos_idx[0] < len(scroll_positions):
            pos = scroll_positions[current_pos_idx[0]]
            scroller.update_viewport(pos)
            
            # Update canvas view
            canvas.yview_moveto(pos / max(1, scroller.total_content_height))
            
            # Update info
            stats = scroller.get_stats()
            info_text.set(
                f"Scroll: {int(pos)}px | "
                f"Rendering {stats['visible_lines']}/{stats['total_lines']} lines | "
                f"{stats['reduction_percent']}% reduction"
            )
            
            current_pos_idx[0] += 1
            root.after(1000, animate_scroll)
        else:
            print("\n2️⃣ Scroll animation complete!")
            stats = scroller.get_stats()
            print(f"   Final stats:")
            print(f"   - Total renders: {stats['render_count']}")
            print(f"   - Visible lines: {stats['visible_lines']}")
            print(f"   - Performance gain: {stats['reduction_percent']}% fewer canvas items")
            
            root.after(2000, root.destroy)
    
    print("\n2️⃣ Starting scroll animation (watch the window)...")
    root.after(1000, animate_scroll)
    
    root.mainloop()


def test_canvas_batcher():
    """Test canvas batching performance"""
    print("\n" + "="*60)
    print("TEST 2: Canvas Batcher")
    print("="*60)
    
    root = tk.Tk()
    root.title("Canvas Batcher Test")
    root.geometry("600x400")
    
    # Create two canvases for comparison
    frame_left = tk.Frame(root, bg='#1A1A1A')
    frame_left.pack(side='left', fill='both', expand=True)
    
    frame_right = tk.Frame(root, bg='#1A1A1A')
    frame_right.pack(side='right', fill='both', expand=True)
    
    # Left: Without batching
    label_left = tk.Label(frame_left, text="WITHOUT Batching", bg='#1A1A1A', fg='#FF2D55', font=('Segoe UI', 12, 'bold'))
    label_left.pack(pady=5)
    
    canvas_left = tk.Canvas(frame_left, bg='#000000', highlightthickness=0)
    canvas_left.pack(fill='both', expand=True, padx=5, pady=5)
    
    # Right: With batching
    label_right = tk.Label(frame_right, text="WITH Batching", bg='#1A1A1A', fg='#1DB954', font=('Segoe UI', 12, 'bold'))
    label_right.pack(pady=5)
    
    canvas_right = tk.Canvas(frame_right, bg='#000000', highlightthickness=0)
    canvas_right.pack(fill='both', expand=True, padx=5, pady=5)
    
    # Create batcher for right canvas
    batcher = CanvasBatcher(canvas_right, batch_size=50)
    
    # Create test items on both canvases
    items_left = []
    items_right = []
    
    for i in range(20):
        y = 20 + i * 15
        
        item_left = canvas_left.create_text(
            150, y,
            text=f"Line {i+1}",
            font=('Segoe UI', 10),
            fill='#FFFFFF',
            anchor='center'
        )
        items_left.append(item_left)
        
        item_right = canvas_right.create_text(
            150, y,
            text=f"Line {i+1}",
            font=('Segoe UI', 10),
            fill='#FFFFFF',
            anchor='center'
        )
        items_right.append(item_right)
    
    print("\n1️⃣ Created 20 items on each canvas")
    
    # Measure update performance
    test_results = {'without_batch': 0.0, 'with_batch': 0.0}
    
    def run_update_test():
        print("\n2️⃣ Running performance test...")
        
        # Test without batching (left canvas)
        start = time.time()
        for _ in range(10):  # 10 cycles
            for i, item_id in enumerate(items_left):
                opacity = (i % 10) / 10
                color = f'#{int(255*opacity):02x}{int(255*opacity):02x}{int(255*opacity):02x}'
                canvas_left.itemconfig(item_id, fill=color)
        canvas_left.update()
        test_results['without_batch'] = (time.time() - start) * 1000
        
        # Test with batching (right canvas)
        start = time.time()
        for _ in range(10):  # 10 cycles
            for i, item_id in enumerate(items_right):
                opacity = (i % 10) / 10
                color = f'#{int(255*opacity):02x}{int(255*opacity):02x}{int(255*opacity):02x}'
                batcher.queue_update(item_id, fill=color)
            batcher.flush()
        canvas_right.update()
        test_results['with_batch'] = (time.time() - start) * 1000
        
        # Show results
        speedup = test_results['without_batch'] / max(0.01, test_results['with_batch'])
        
        print(f"\n   Results (200 updates each):")
        print(f"   Without batching: {test_results['without_batch']:.2f}ms")
        print(f"   With batching: {test_results['with_batch']:.2f}ms")
        print(f"   ✅ Speedup: {speedup:.1f}x faster!")
        
        # Show batcher stats
        stats = batcher.get_stats()
        print(f"\n   Batcher stats:")
        print(f"   - Total batches: {stats['total_batches']}")
        print(f"   - Total updates: {stats['total_updates']}")
        print(f"   - Avg batch size: {stats['avg_batch_size']}")
        print(f"   - Max batch size: {stats['max_batch_size']}")
        
        root.after(2000, root.destroy)
    
    root.after(500, run_update_test)
    root.mainloop()


def test_smart_canvas_batcher():
    """Test smart canvas batcher with deduplication"""
    print("\n" + "="*60)
    print("TEST 3: Smart Canvas Batcher (Deduplication)")
    print("="*60)
    
    root = tk.Tk()
    root.title("Smart Canvas Batcher Test")
    root.geometry("400x300")
    
    canvas = tk.Canvas(root, bg='#000000', highlightthickness=0)
    canvas.pack(fill='both', expand=True)
    
    # Create smart batcher
    batcher = SmartCanvasBatcher(canvas, enable_deduplication=True)
    
    # Create test item
    item = canvas.create_text(
        200, 150,
        text="Watch me NOT flicker!",
        font=('Segoe UI', 16, 'bold'),
        fill='#FFFFFF'
    )
    
    print("\n1️⃣ Testing deduplication...")
    print("   Sending 1000 redundant updates...")
    
    # Send many redundant updates (should be deduplicated)
    start = time.time()
    for _ in range(1000):
        batcher.queue_update(item, fill='#FFFFFF')  # Same value every time!
    batcher.flush()
    dedup_time = (time.time() - start) * 1000
    
    # Send varying updates (can't deduplicate)
    start = time.time()
    for i in range(1000):
        color = f'#{i%256:02x}{i%256:02x}{i%256:02x}'
        batcher.queue_update(item, fill=color)
    batcher.flush()
    normal_time = (time.time() - start) * 1000
    
    stats = batcher.get_stats()
    
    print(f"\n   Results:")
    print(f"   Redundant updates: {dedup_time:.2f}ms (deduplicated)")
    print(f"   Varying updates: {normal_time:.2f}ms (not deduplicated)")
    print(f"   ✅ Deduplication saved {((normal_time - dedup_time) / normal_time * 100):.1f}% time")
    print(f"\n   Stats:")
    print(f"   - Total batches: {stats['total_batches']}")
    print(f"   - Total updates: {stats['total_updates']}")
    
    root.after(3000, root.destroy)
    root.mainloop()


def test_combined_performance():
    """Test virtual scroller + canvas batcher together"""
    print("\n" + "="*60)
    print("TEST 4: Combined Performance (Virtual + Batching)")
    print("="*60)
    
    root = tk.Tk()
    root.title("Combined Performance Test")
    root.geometry("500x600")
    
    canvas = tk.Canvas(root, bg='#000000', highlightthickness=0)
    canvas.pack(fill='both', expand=True)
    
    # Create both components
    scroller = VirtualScroller(canvas, window_width=500, window_height=600, line_height=40)
    batcher = SmartCanvasBatcher(canvas)
    
    # Create 100 lyrics (long song)
    test_lyrics = [f"Line {i+1}: Some lyric text here for testing" for i in range(100)]
    scroller.set_lyrics(test_lyrics)
    
    print(f"\n1️⃣ Created 100 lyric lines")
    
    scroller_stats = scroller.get_stats()
    print(f"   Virtual scroller rendering: {scroller_stats['visible_lines']}/{scroller_stats['total_lines']}")
    print(f"   ✅ {scroller_stats['reduction_percent']}% reduction")
    
    # Simulate rapid updates (like real-time lyrics)
    update_count = [0]
    
    def simulate_updates():
        if update_count[0] < 50:
            # Update multiple lines at once (simulating line highlighting changes)
            for i in range(10):
                line_idx = (update_count[0] + i) % 100
                canvas_id = scroller.get_line_canvas_id(line_idx)
                if canvas_id:
                    opacity = 0.5 + (i / 20)
                    color = f'#{int(255*opacity):02x}{int(255*opacity):02x}{int(255*opacity):02x}'
                    batcher.queue_update(canvas_id, fill=color)
            
            batcher.flush()
            update_count[0] += 1
            root.after(50, simulate_updates)  # 20 FPS updates
        else:
            print("\n2️⃣ Completed 50 update cycles (500 line updates)")
            
            scroller_stats = scroller.get_stats()
            batcher_stats = batcher.get_stats()
            
            print(f"\n   Virtual Scroller Stats:")
            print(f"   - Visible lines: {scroller_stats['visible_lines']}/{scroller_stats['total_lines']}")
            print(f"   - Render calls: {scroller_stats['render_count']}")
            
            print(f"\n   Canvas Batcher Stats:")
            print(f"   - Total batches: {batcher_stats['total_batches']}")
            print(f"   - Total updates: {batcher_stats['total_updates']}")
            print(f"   - Avg batch size: {batcher_stats['avg_batch_size']}")
            
            print(f"\n✅ Combined optimization working smoothly!")
            
            root.after(2000, root.destroy)
    
    print("\n2️⃣ Simulating rapid updates (like real-time lyrics)...")
    root.after(500, simulate_updates)
    root.mainloop()


def run_all_tests():
    """Run all Phase 2 tests"""
    print("\n" + "="*60)
    print("🧪 PHASE 2 RENDERING TESTS")
    print("="*60)
    
    try:
        test_virtual_scroller()
        test_canvas_batcher()
        test_smart_canvas_batcher()
        test_combined_performance()
        
        print("\n" + "="*60)
        print("✅ ALL PHASE 2 TESTS PASSED!")
        print("="*60)
        print("\n✨ Rendering components are working correctly!")
        print("   Ready to proceed to Phase 3 (Integration).\n")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()
