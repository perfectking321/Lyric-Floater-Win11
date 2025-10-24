"""
Test LRClib API to diagnose 400 errors
"""
import requests
import json

def test_lrclib_api():
    """Test LRClib API with different song formats"""
    print("\n" + "="*70)
    print("LRCLIB API DIAGNOSTIC TEST")
    print("="*70)
    
    # Test cases - working vs failing songs
    test_songs = [
        {
            "name": "Faded (WORKING)",
            "artist": "Alan Walker",
            "track": "Faded",
            "album": "Faded",
            "duration": 212  # seconds, not milliseconds!
        },
        {
            "name": "Janam Janam (WORKING)",
            "artist": "Pritam",
            "track": "Janam Janam",
            "album": "Dilwale (Original Motion Picture Soundtrack)",
            "duration": 237  # seconds
        },
        {
            "name": "Darkside (FAILING)",
            "artist": "Alan Walker",
            "track": "Darkside",
            "album": "Different World",
            "duration": 207  # Current: 207426ms / 1000
        },
        {
            "name": "Alone (FAILING)",
            "artist": "Alan Walker",
            "track": "Alone",
            "album": "Different World",
            "duration": 160  # Current: 160426ms / 1000
        }
    ]
    
    print("\n🔍 Testing LRClib API responses:\n")
    
    for song in test_songs:
        print(f"\n{'='*70}")
        print(f"Testing: {song['name']}")
        print(f"  Artist: {song['artist']}")
        print(f"  Track: {song['track']}")
        print(f"  Album: {song['album']}")
        print(f"  Duration: {song['duration']}s")
        print(f"{'='*70}")
        
        # Test with current approach (milliseconds as string)
        print("\n📍 Test 1: Current approach (duration in milliseconds):")
        params_ms = {
            'artist_name': song['artist'],
            'track_name': song['track'],
            'album_name': song['album'],
            'duration': str(song['duration'] * 1000)  # Convert to ms
        }
        
        try:
            response = requests.get('https://lrclib.net/api/get', params=params_ms, timeout=5)
            print(f"  Status: {response.status_code}")
            print(f"  Params: {params_ms}")
            
            if response.status_code == 200:
                data = response.json()
                has_synced = bool(data.get('syncedLyrics'))
                print(f"  ✅ SUCCESS! Synced lyrics: {has_synced}")
                if has_synced:
                    lines = data['syncedLyrics'].split('\n')
                    print(f"  Lines: {len(lines)}")
            else:
                print(f"  ❌ FAILED: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
        
        # Test with seconds (integer)
        print("\n📍 Test 2: Duration in seconds (integer):")
        params_sec = {
            'artist_name': song['artist'],
            'track_name': song['track'],
            'album_name': song['album'],
            'duration': song['duration']  # Seconds as integer
        }
        
        try:
            response = requests.get('https://lrclib.net/api/get', params=params_sec, timeout=5)
            print(f"  Status: {response.status_code}")
            print(f"  Params: {params_sec}")
            
            if response.status_code == 200:
                data = response.json()
                has_synced = bool(data.get('syncedLyrics'))
                print(f"  ✅ SUCCESS! Synced lyrics: {has_synced}")
                if has_synced:
                    lines = data['syncedLyrics'].split('\n')
                    print(f"  Lines: {len(lines)}")
            else:
                print(f"  ❌ FAILED: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
        
        # Test without duration
        print("\n📍 Test 3: Without duration parameter:")
        params_no_dur = {
            'artist_name': song['artist'],
            'track_name': song['track'],
            'album_name': song['album']
        }
        
        try:
            response = requests.get('https://lrclib.net/api/get', params=params_no_dur, timeout=5)
            print(f"  Status: {response.status_code}")
            print(f"  Params: {params_no_dur}")
            
            if response.status_code == 200:
                data = response.json()
                has_synced = bool(data.get('syncedLyrics'))
                print(f"  ✅ SUCCESS! Synced lyrics: {has_synced}")
                if has_synced:
                    lines = data['syncedLyrics'].split('\n')
                    print(f"  Lines: {len(lines)}")
            else:
                print(f"  ❌ FAILED: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
        except Exception as e:
            print(f"  ❌ ERROR: {e}")

def check_lyricstify_code():
    """Check what the actual code is doing"""
    print("\n" + "="*70)
    print("CHECKING LYRICSTIFY_FETCHER CODE")
    print("="*70)
    
    with open('lyricstify_fetcher.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the LRClib API call
    import re
    lrclib_section = re.search(r'def _fetch_from_lrclib.*?(?=\n    def |\nclass |\Z)', content, re.DOTALL)
    
    if lrclib_section:
        print("\n_fetch_from_lrclib method:")
        print("-" * 70)
        lines = lrclib_section.group(0).split('\n')[:40]  # First 40 lines
        for i, line in enumerate(lines, 1):
            print(f"{i:3d}: {line}")
    
    print("\n🔍 Looking for duration parameter handling...")
    if 'duration_ms' in content:
        print("  ✅ Found: duration_ms variable")
    if "params = {" in content:
        print("  ✅ Found: params dictionary")
    if "'duration':" in content:
        print("  ✅ Found: duration parameter being set")

if __name__ == "__main__":
    try:
        # First check the code
        check_lyricstify_code()
        
        # Then test the API
        test_lrclib_api()
        
        print("\n" + "="*70)
        print("DIAGNOSTIC COMPLETE")
        print("="*70)
        print("\n💡 Analysis:")
        print("  - If Test 1 (milliseconds) fails with 400")
        print("  - But Test 2 (seconds) succeeds")
        print("  - Then the bug is: duration should be in SECONDS, not milliseconds!")
        print("\n  LRClib expects: duration=207 (seconds)")
        print("  Current code sends: duration=207426 (milliseconds)")
        print("  This causes 400 Bad Request!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
