"""
Diagnostic Test Cases for Lyrics Fetching Issue

Problem: LRClib returns 42 lines, but app only displays 1 line
Hypothesis: Cache or data processing issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lyrics_fetcher import GeniusLyricsFetcher
from config import GENIUS_ACCESS_TOKEN
from lrclib_fetcher import LRClibFetcher
import json


def test_case_1_cache_inspection():
    """TEST 1: Inspect what's actually in the cache"""
    print("\n" + "="*70)
    print("TEST 1: CACHE INSPECTION")
    print("="*70)
    
    cache_dir = "lyrics_cache"
    if not os.path.exists(cache_dir):
        print("❌ Cache directory doesn't exist")
        return
    
    cache_files = os.listdir(cache_dir)
    print(f"Found {len(cache_files)} cache files:")
    
    for filename in cache_files:
        filepath = os.path.join(cache_dir, filename)
        print(f"\n📁 {filename}:")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"   Type: {type(data)}")
            print(f"   Length: {len(data) if isinstance(data, (list, dict, str)) else 'N/A'}")
            
            if isinstance(data, list):
                print(f"   Items: {len(data)}")
                if len(data) > 0:
                    print(f"   First item type: {type(data[0])}")
                    print(f"   First item: {str(data[0])[:100]}")
            elif isinstance(data, dict):
                print(f"   Keys: {list(data.keys())}")
            elif isinstance(data, str):
                print(f"   Preview: {data[:200]}")
                
        except Exception as e:
            print(f"   ❌ Error reading: {e}")


def test_case_2_lrclib_direct():
    """TEST 2: Direct LRClib fetch"""
    print("\n" + "="*70)
    print("TEST 2: DIRECT LRClib FETCH")
    print("="*70)
    
    fetcher = LRClibFetcher()
    result = fetcher.fetch_synced_lyrics("Alan Walker", "Faded", duration=212)
    
    if result:
        print(f"✅ LRClib returned data")
        print(f"   Has synced: {result.get('synced_lyrics') is not None}")
        print(f"   Has plain: {result.get('raw_plain') is not None}")
        
        if result.get('synced_lyrics'):
            synced = result['synced_lyrics']
            print(f"   Synced lines: {len(synced)}")
            print(f"   Format: {type(synced[0]) if synced else 'empty'}")
            print(f"\n   First 3 synced lines:")
            for i, line in enumerate(synced[:3]):
                print(f"   {i}. {line}")
    else:
        print("❌ LRClib returned None")


def test_case_3_fetcher_integration():
    """TEST 3: Full lyrics_fetcher integration (NO CACHE)"""
    print("\n" + "="*70)
    print("TEST 3: LYRICS_FETCHER INTEGRATION (Cache Cleared)")
    print("="*70)
    
    # Clear cache for this test
    cache_dir = "lyrics_cache"
    cache_file = os.path.join(cache_dir, "alan_walker_faded.json")
    if os.path.exists(cache_file):
        os.remove(cache_file)
        print("🗑️  Cleared cache for 'Faded'")
    
    fetcher = GeniusLyricsFetcher(GENIUS_ACCESS_TOKEN)
    result = fetcher.fetch_lyrics("Alan Walker", "Faded", album="Different World", duration=212)
    
    print(f"\n📊 Result Analysis:")
    print(f"   Type: {type(result)}")
    print(f"   Length: {len(result) if result else 0}")
    
    if isinstance(result, list) and len(result) > 0:
        first = result[0]
        print(f"   First item type: {type(first)}")
        print(f"   First item: {str(first)[:150]}")
        
        if isinstance(first, tuple):
            print(f"\n   ✅ CORRECT FORMAT: List of tuples (synced lyrics)")
            print(f"   Sample lines:")
            for i in range(min(3, len(result))):
                text, start, end = result[i]
                print(f"   {i}. [{start}ms-{end}ms] {text[:50]}")
        elif isinstance(first, dict):
            print(f"\n   ⚠️  DICT FORMAT: Genius fallback")
            print(f"   Keys: {first.keys() if isinstance(first, dict) else 'N/A'}")


def test_case_4_cache_save_load():
    """TEST 4: Test cache save and load cycle"""
    print("\n" + "="*70)
    print("TEST 4: CACHE SAVE/LOAD CYCLE")
    print("="*70)
    
    # Create test data (synced format)
    test_lyrics = [
        ("Test line 1", 1000, 2000),
        ("Test line 2", 2000, 3000),
        ("Test line 3", 3000, 4000)
    ]
    
    fetcher = GeniusLyricsFetcher(GENIUS_ACCESS_TOKEN)
    
    # Save to cache
    print("💾 Saving test lyrics to cache...")
    fetcher.save_lyrics_to_cache("Test Artist", "Test Song", test_lyrics)
    
    # Load from cache
    print("📂 Loading from cache...")
    loaded = fetcher.get_lyrics_from_cache("Test Artist", "Test Song")
    
    print(f"\n📊 Comparison:")
    print(f"   Original: {len(test_lyrics)} items, type={type(test_lyrics[0])}")
    print(f"   Loaded: {len(loaded) if loaded else 0} items, type={type(loaded[0]) if loaded else 'None'}")
    
    if loaded and len(loaded) == len(test_lyrics):
        print(f"   ✅ Length matches!")
        if loaded[0] == test_lyrics[0]:
            print(f"   ✅ Data matches!")
        else:
            print(f"   ❌ Data MISMATCH!")
            print(f"      Original: {test_lyrics[0]}")
            print(f"      Loaded: {loaded[0]}")
    else:
        print(f"   ❌ Length MISMATCH or None!")


def test_case_5_clean_lyrics_function():
    """TEST 5: Test the _clean_lyrics_text function"""
    print("\n" + "="*70)
    print("TEST 5: LYRICS CLEANING FUNCTION")
    print("="*70)
    
    # Simulate what might come from LRClib
    test_input = """Line 1 of lyrics
Line 2 of lyrics
Line 3 of lyrics
Line 4 of lyrics
Line 5 of lyrics"""
    
    print(f"📥 Input:")
    print(f"   Lines: {len(test_input.split(chr(10)))}")
    print(f"   Preview: {test_input[:100]}")
    
    # Simulate the cleaning that happens in UI
    from ui.lyrics_window_v2 import ModernLyricsWindow
    
    # Create a minimal mock object
    class MockRoot:
        def after(self, *args): pass
        def update_idletasks(self): pass
        def winfo_screenwidth(self): return 1920
        def winfo_screenheight(self): return 1080
        def geometry(self, *args): pass
        def attributes(self, *args): pass
        def configure(self, *args): pass
        def iconphoto(self, *args): pass
        def bind(self, *args): pass
    
    try:
        window = ModernLyricsWindow(MockRoot())
        cleaned = window._clean_lyrics_text(test_input)
        
        print(f"\n📤 Output:")
        print(f"   Lines: {len(cleaned.split(chr(10)))}")
        print(f"   Preview: {cleaned[:100]}")
        
        if len(cleaned.split('\n')) < len(test_input.split('\n')):
            print(f"   ⚠️  LINES WERE REMOVED by cleaning!")
        else:
            print(f"   ✅ All lines preserved")
    except Exception as e:
        print(f"   ❌ Error testing clean function: {e}")


def run_all_tests():
    """Run all diagnostic tests"""
    print("\n" + "="*70)
    print("🔬 LYRICS FETCHING DIAGNOSTIC SUITE")
    print("="*70)
    
    test_case_1_cache_inspection()
    test_case_2_lrclib_direct()
    test_case_3_fetcher_integration()
    test_case_4_cache_save_load()
    test_case_5_clean_lyrics_function()
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETE")
    print("="*70)
    print("\nPlease review the output above to identify the issue.")


if __name__ == "__main__":
    run_all_tests()
    input("\nPress Enter to exit...")
