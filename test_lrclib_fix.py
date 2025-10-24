"""
Test the LRClib fix - verify synced lyrics work after duration fix
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lyrics_fetcher import GeniusLyricsFetcher

def test_fixed_duration():
    """Test that duration is now correctly converted to seconds"""
    print("\n" + "="*70)
    print("TESTING LRCLIB FIX - Duration Conversion")
    print("="*70)
    
    fetcher = GeniusLyricsFetcher(api_token="dummy")  # We won't need Genius
    
    # Test songs that were failing
    test_cases = [
        {
            "name": "Darkside",
            "artist": "Alan Walker",
            "title": "Darkside",
            "album": "Different World",
            "duration_ms": 207426,  # Spotify gives milliseconds
            "duration_sec": 207  # Should be converted to seconds
        },
        {
            "name": "Alone",
            "artist": "Alan Walker",
            "title": "Alone",
            "album": "Different World",
            "duration_ms": 160426,
            "duration_sec": 160
        },
        {
            "name": "Faded",
            "artist": "Alan Walker",
            "title": "Faded",
            "album": "Faded",
            "duration_ms": 212000,
            "duration_sec": 212
        }
    ]
    
    print("\n📋 Test Cases:")
    for i, song in enumerate(test_cases, 1):
        print(f"\n{i}. {song['name']}")
        print(f"   Spotify duration: {song['duration_ms']}ms")
        print(f"   Expected LRClib: {song['duration_sec']}s")
        print(f"   Conversion: {song['duration_ms']} // 1000 = {song['duration_ms'] // 1000}s")
    
    print("\n" + "="*70)
    print("FETCHING LYRICS (with fixed duration)")
    print("="*70)
    
    results = []
    
    for song in test_cases:
        print(f"\n{'='*70}")
        print(f"Testing: {song['name']}")
        print(f"{'='*70}")
        
        # Fetch with converted duration (seconds)
        lyrics = fetcher.fetch_lyrics(
            artist=song['artist'],
            title=song['title'],
            album=song['album'],
            duration=song['duration_sec']  # ✅ Now in seconds!
        )
        
        # Analyze result
        if lyrics:
            is_synced = False
            line_count = 0
            
            if isinstance(lyrics, list) and len(lyrics) > 0:
                first_item = lyrics[0]
                
                if isinstance(first_item, (tuple, list)) and len(first_item) == 3:
                    # Synced lyrics (text, start_ms, end_ms)
                    is_synced = True
                    line_count = len(lyrics)
                    print(f"\n✅ SUCCESS: Got SYNCED lyrics!")
                    print(f"   Lines: {line_count}")
                    print(f"   Format: (text, start_ms, end_ms)")
                    print(f"   First line: {lyrics[0][0][:50]}...")
                    print(f"   Timing: {lyrics[0][1]}ms - {lyrics[0][2]}ms")
                elif isinstance(first_item, dict):
                    # Plain text
                    print(f"\n⚠️ WARNING: Got plain text (no sync)")
                    print(f"   This means LRClib failed or no synced lyrics available")
            
            results.append({
                'song': song['name'],
                'synced': is_synced,
                'lines': line_count
            })
        else:
            print(f"\n❌ FAILED: No lyrics returned")
            results.append({
                'song': song['name'],
                'synced': False,
                'lines': 0
            })
    
    # Summary
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    
    all_synced = all(r['synced'] for r in results)
    
    for r in results:
        status = "✅ SYNCED" if r['synced'] else "❌ FAILED"
        print(f"{status}: {r['song']:15s} - {r['lines']:2d} lines")
    
    print("\n" + "="*70)
    
    if all_synced:
        print("🎉 SUCCESS! All songs now have synced lyrics!")
        print("The duration conversion fix is working correctly.")
    else:
        print("⚠️ PARTIAL SUCCESS - Some songs still failing")
        print("This could be due to:")
        print("  - Songs not in LRClib database")
        print("  - Network issues")
        print("  - API rate limiting")
    
    print("="*70)
    
    return all_synced

if __name__ == "__main__":
    try:
        success = test_fixed_duration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
