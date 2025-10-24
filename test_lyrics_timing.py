"""
Test Cases for Live Lyrics Detection & Highlighting System

This file contains diagnostic tests to identify issues with real-time 
lyrics synchronization and highlighting.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class MockSpotifyController:
    """Mock Spotify Controller for testing timing algorithms"""
    
    def calculate_line_timing(self, lyrics_lines, duration_ms):
        """Same algorithm as real SpotifyController"""
        if not lyrics_lines or duration_ms <= 0:
            return []
        
        timed_lines = []
        num_lines = len(lyrics_lines)
        time_per_line = duration_ms / num_lines
        
        for i, line in enumerate(lyrics_lines):
            start_ms = int(i * time_per_line)
            end_ms = int((i + 1) * time_per_line)
            timed_lines.append((line, start_ms, end_ms))
        
        return timed_lines
    
    def get_current_line_index(self, progress_ms, timed_lines):
        """Same algorithm as real SpotifyController"""
        for i, (line, start_ms, end_ms) in enumerate(timed_lines):
            if start_ms <= progress_ms < end_ms:
                return i
        
        if progress_ms >= timed_lines[-1][2] if timed_lines else 0:
            return len(timed_lines) - 1
        
        return 0


class LyricsTimingTester:
    """Test suite for lyrics timing algorithm"""
    
    def __init__(self):
        self.test_results = []
        
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'details': details
        })
    
    def test_timing_calculation_algorithm(self):
        """
        TEST 1: Verify the timing calculation algorithm
        
        ALGORITHM USED:
        - Simple even distribution (time_per_line = total_duration / num_lines)
        - Each line gets equal time slice
        - No consideration for actual line length or natural pauses
        
        PROBLEM: This is the ROOT CAUSE of poor synchronization!
        Songs don't have evenly distributed lyrics. Some lines are sung
        quickly, others slowly, with varying pauses between them.
        """
        print("\n" + "="*70)
        print("TEST 1: TIMING CALCULATION ALGORITHM")
        print("="*70)
        
        # Simulate a 3-minute song (180,000 ms) with 50 lines
        duration_ms = 180000  # 3 minutes
        num_lines = 50
        
        controller = MockSpotifyController()
        lyrics_lines = [f"Line {i+1}" for i in range(num_lines)]
        
        timed_lines = controller.calculate_line_timing(lyrics_lines, duration_ms)
        
        # Verify calculations
        time_per_line = duration_ms / num_lines
        expected_time_per_line = 3600  # ms per line
        
        print(f"Total Duration: {duration_ms}ms ({duration_ms/1000}s)")
        print(f"Number of Lines: {num_lines}")
        print(f"Time per Line: {time_per_line}ms ({time_per_line/1000:.2f}s)")
        print(f"\nFirst 5 lines timing:")
        for i in range(min(5, len(timed_lines))):
            line, start, end = timed_lines[i]
            print(f"  Line {i}: {start}ms - {end}ms (duration: {end-start}ms)")
        
        # Check if timing is correct
        all_correct = True
        for i, (line, start, end) in enumerate(timed_lines):
            expected_start = int(i * time_per_line)
            expected_end = int((i + 1) * time_per_line)
            if start != expected_start or end != expected_end:
                all_correct = False
                break
        
        self.log_test(
            "Timing Calculation",
            all_correct,
            f"Each line gets {time_per_line:.0f}ms evenly"
        )
        
        # Identify the problem
        print("\n⚠️  IDENTIFIED PROBLEM:")
        print("   The algorithm assumes ALL lines take the same time to sing!")
        print("   Reality: Lyrics have varying speeds, pauses, and repetitions.")
        print("   Example: 'Where are you now?' might take 2s")
        print("            'Atlantis, under the sea, under the sea' might take 4s")
        print("   But our algorithm gives them both the same time slice.")
        
        return timed_lines
    
    def test_line_index_detection(self):
        """
        TEST 2: Verify current line detection at different timestamps
        """
        print("\n" + "="*70)
        print("TEST 2: CURRENT LINE INDEX DETECTION")
        print("="*70)
        
        controller = MockSpotifyController()
        
        # Create sample timed lyrics (20-second song, 10 lines)
        duration_ms = 20000
        lyrics_lines = [
            "Line 1: Where are you now?",
            "Line 2: Where are you now?",
            "Line 3: Under the bright but faded lights",
            "Line 4: You set my heart on fire",
            "Line 5: Where are you now?",
            "Line 6: Where are you now?",
            "Line 7: Where are you now?",
            "Line 8: Atlantis, under the sea",
            "Line 9: Where are you now?",
            "Line 10: Another dream"
        ]
        
        timed_lines = controller.calculate_line_timing(lyrics_lines, duration_ms)
        
        # Test at various timestamps
        test_timestamps = [0, 1000, 2000, 5000, 10000, 15000, 19000, 20000, 25000]
        
        print(f"Song Duration: {duration_ms}ms")
        print(f"Lines: {len(lyrics_lines)}")
        print(f"\nTesting line detection at various timestamps:\n")
        
        all_correct = True
        for timestamp in test_timestamps:
            detected_index = controller.get_current_line_index(timestamp, timed_lines)
            
            # Calculate expected index
            time_per_line = duration_ms / len(lyrics_lines)
            expected_index = min(int(timestamp / time_per_line), len(lyrics_lines) - 1)
            
            is_correct = detected_index == expected_index
            if not is_correct:
                all_correct = False
            
            status = "✓" if is_correct else "✗"
            if detected_index < len(lyrics_lines):
                line_text = lyrics_lines[detected_index][:30]
            else:
                line_text = "OUT OF RANGE"
            
            print(f"  {status} At {timestamp:5d}ms → Line {detected_index} (expected {expected_index})")
            print(f"      '{line_text}...'")
            
            if detected_index < len(timed_lines):
                line, start, end = timed_lines[detected_index]
                print(f"      Timing: {start}ms - {end}ms")
            print()
        
        self.log_test(
            "Line Index Detection",
            all_correct,
            f"Tested {len(test_timestamps)} different timestamps"
        )
        
        return all_correct
    
    def test_edge_cases(self):
        """
        TEST 3: Test edge cases that might cause bugs
        """
        print("\n" + "="*70)
        print("TEST 3: EDGE CASES")
        print("="*70)
        
        controller = MockSpotifyController()
        
        test_cases = [
            {
                'name': 'Empty lyrics list',
                'lines': [],
                'duration': 180000,
                'should_return_empty': True
            },
            {
                'name': 'Zero duration',
                'lines': ['Line 1', 'Line 2'],
                'duration': 0,
                'should_return_empty': True
            },
            {
                'name': 'Negative duration',
                'lines': ['Line 1', 'Line 2'],
                'duration': -1000,
                'should_return_empty': True
            },
            {
                'name': 'Single line',
                'lines': ['Only one line'],
                'duration': 60000,
                'should_return_empty': False
            },
            {
                'name': 'Very short song (5 seconds)',
                'lines': ['Line 1', 'Line 2', 'Line 3'],
                'duration': 5000,
                'should_return_empty': False
            },
            {
                'name': 'Many lines (100)',
                'lines': [f'Line {i}' for i in range(100)],
                'duration': 180000,
                'should_return_empty': False
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            result = controller.calculate_line_timing(
                test_case['lines'],
                test_case['duration']
            )
            
            is_empty = len(result) == 0
            expected_empty = test_case['should_return_empty']
            passed = is_empty == expected_empty
            
            if not passed:
                all_passed = False
            
            status = "✓" if passed else "✗"
            print(f"  {status} {test_case['name']}")
            print(f"      Expected empty: {expected_empty}, Got empty: {is_empty}")
            if result and not expected_empty:
                print(f"      Returned {len(result)} timed lines")
                if len(result) > 0:
                    time_per_line = (result[0][2] - result[0][1])
                    print(f"      Time per line: {time_per_line}ms")
            print()
        
        self.log_test("Edge Cases", all_passed, f"Tested {len(test_cases)} edge cases")
        
        return all_passed
    
    def test_real_world_scenario(self):
        """
        TEST 4: Simulate real-world scenario with "Faded" by Alan Walker
        """
        print("\n" + "="*70)
        print("TEST 4: REAL-WORLD SCENARIO - 'Faded' by Alan Walker")
        print("="*70)
        
        # Real song data
        duration_ms = 212000  # 3:32 (from your screenshot: 3:32)
        
        # Actual lyrics from your screenshot
        lyrics = [
            "Where are you now?",
            "Where are you now?",
            "Under the bright but faded lights",
            "You set my heart on fire",
            "Where are you now?",
            "Where are you now?",
            "Where are you now?",
            "Atlantis, under the sea, under the sea",
            "Where are you now? Another dream",
            "The monster's running wild inside of me",
            "I'm faded, I'm faded",
            "So lost, I'm faded, I'm faded",
            "So lost, I'm faded"
        ]
        
        controller = MockSpotifyController()
        timed_lines = controller.calculate_line_timing(lyrics, duration_ms)
        
        print(f"Song: Faded by Alan Walker")
        print(f"Duration: {duration_ms}ms ({duration_ms/1000:.0f}s)")
        print(f"Lyrics Lines: {len(lyrics)}")
        print(f"Time per line: {duration_ms/len(lyrics):.0f}ms ({duration_ms/len(lyrics)/1000:.1f}s)")
        
        # Your screenshot shows 0:20 progress (20 seconds = 20000ms)
        progress_at_screenshot = 20000
        
        current_index = controller.get_current_line_index(progress_at_screenshot, timed_lines)
        
        print(f"\n📸 Screenshot Analysis:")
        print(f"   Timestamp: {progress_at_screenshot}ms (0:20)")
        print(f"   Detected Line Index: {current_index}")
        print(f"   Detected Line Text: '{lyrics[current_index]}'")
        
        # Show what SHOULD be playing at 20 seconds
        # Based on the actual song, at 0:20, the singer is likely around line 4-6
        print(f"\n   Line Timing at 0:20:")
        for i in range(max(0, current_index-2), min(len(timed_lines), current_index+3)):
            line, start, end = timed_lines[i]
            marker = " ← CURRENT" if i == current_index else ""
            print(f"      Line {i}: {start/1000:.1f}s - {end/1000:.1f}s: '{line[:40]}'{marker}")
        
        print(f"\n⚠️  PROBLEM ANALYSIS:")
        print(f"   At 20 seconds into the song:")
        print(f"   - Algorithm thinks: Line {current_index} should be playing")
        print(f"   - But in reality: The actual lyrics timing depends on the song's rhythm")
        print(f"   - The even distribution doesn't match actual singing pace!")
        
        # Calculate percentage error
        actual_progress_percent = (progress_at_screenshot / duration_ms) * 100
        detected_line_percent = (current_index / len(lyrics)) * 100
        
        print(f"\n   Progress: {actual_progress_percent:.1f}% through song")
        print(f"   Line: {detected_line_percent:.1f}% through lyrics")
        print(f"   Difference: {abs(actual_progress_percent - detected_line_percent):.1f}%")
        
        # The test "passes" if calculation is consistent, but we note the limitation
        self.log_test(
            "Real-world Scenario",
            True,
            f"Algorithm is mathematically correct but doesn't match actual singing"
        )
        
        return timed_lines
    
    def test_update_frequency(self):
        """
        TEST 5: Analyze update frequency issues
        """
        print("\n" + "="*70)
        print("TEST 5: UPDATE FREQUENCY ANALYSIS")
        print("="*70)
        
        print("Spotify API Progress Update Frequency:")
        print("  - Updates every 1000ms (1 second) via update_progress()")
        print("  - This is set in: self.root.after(1000, self.update_progress)")
        print("\nPotential Issues:")
        print("  ❌ 1-second granularity is too coarse for smooth line transitions")
        print("  ❌ A line that lasts only 2-3 seconds will only get 2-3 updates")
        print("  ❌ User sees 'jumpy' highlighting instead of smooth transitions")
        print("\nRecommendation:")
        print("  ✅ Increase update frequency to 250ms or 500ms")
        print("  ✅ This will give 4-2 updates per second for smoother transitions")
        
        self.log_test(
            "Update Frequency",
            False,
            "1-second updates are too slow for smooth highlighting"
        )
    
    def run_all_tests(self):
        """Run all diagnostic tests"""
        print("\n" + "="*70)
        print("LYRICS TIMING DIAGNOSTIC TEST SUITE")
        print("="*70)
        
        self.test_timing_calculation_algorithm()
        self.test_line_index_detection()
        self.test_edge_cases()
        self.test_real_world_scenario()
        self.test_update_frequency()
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for r in self.test_results if r['passed'])
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print("\nFailed Tests:")
        for result in self.test_results:
            if not result['passed']:
                print(f"  ❌ {result['test']}: {result['details']}")
        
        print("\n" + "="*70)
        print("ROOT CAUSE ANALYSIS")
        print("="*70)
        print("""
🔴 CRITICAL ISSUES FOUND:

1. EVEN DISTRIBUTION ALGORITHM IS FUNDAMENTALLY FLAWED
   - Assumes all lyrics lines take equal time
   - Real songs have variable pacing, pauses, repetitions
   - No way to know actual timing without LRC/synchronized lyrics

2. SLOW UPDATE FREQUENCY (1 second)
   - Progress updates every 1000ms
   - Makes highlighting feel jumpy and unresponsive
   - Short lines (2-3s) barely get highlighted before moving on

3. NO ACTUAL SYNCHRONIZED LYRICS DATA
   - Genius API doesn't provide timestamps
   - We're guessing the timing by dividing evenly
   - This NEVER matches the actual song

SOLUTIONS:

✅ IMMEDIATE FIX (keeps current system):
   1. Increase update frequency: 1000ms → 250ms
   2. Add smooth interpolation between detected changes
   3. Add slight delay/lookahead for better perception

✅ PROPER FIX (better accuracy):
   1. Use LRC format lyrics (with actual timestamps)
   2. Integrate with Spotify's Lyrics API (if available)
   3. Use Musixmatch API for synced lyrics
   4. Implement machine learning to predict timing patterns

✅ HYBRID APPROACH:
   1. Try to fetch synced lyrics (LRC/Musixmatch)
   2. Fall back to improved estimation if not available
   3. Learn from user feedback to improve estimates
        """)


if __name__ == "__main__":
    tester = LyricsTimingTester()
    tester.run_all_tests()
    
    input("\nPress Enter to exit...")
