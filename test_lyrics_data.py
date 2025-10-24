"""
Test Case 4: Lyrics Fetching and Data Format
Check what data is actually coming from LRClib/Genius
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lyrics_fetcher import GeniusLyricsFetcher
import json

def load_config():
    """Load config"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def test_lyrics_data():
    """Test what lyrics are actually being fetched"""
    print("\n" + "="*60)
    print("LYRICS DATA INSPECTION")
    print("="*60)
    
    config = load_config()
    fetcher = GeniusLyricsFetcher(api_token=config['genius_access_token'])
    
    # The song from your screenshot
    artist = "Pritam"
    title = "Janam Janam"
    album = "Dilwale (Original Motion Picture Soundtrack)"
    duration = 217893  # approximate
    
    print(f"\n🎵 Fetching lyrics for:")
    print(f"   Artist: {artist}")
    print(f"   Title: {title}")
    print(f"   Album: {album}")
    print(f"   Duration: {duration}ms")
    
    print(f"\n⏳ Fetching...")
    lyrics = fetcher.fetch_lyrics(artist, title, album, duration)
    
    print(f"\n📊 Lyrics data type: {type(lyrics)}")
    print(f"   Length: {len(lyrics) if lyrics else 0}")
    
    if lyrics:
        first_item = lyrics[0]
        print(f"\n🔍 First item type: {type(first_item)}")
        print(f"   First item: {first_item}")
        
        if isinstance(first_item, (tuple, list)) and len(first_item) == 3:
            print(f"\n✅ SYNCED LYRICS (LRClib format)")
            print(f"\n   First 10 lines:")
            for i, item in enumerate(lyrics[:10]):
                text, start_ms, end_ms = item
                print(f"   {i+1}. [{start_ms/1000:.2f}s] {text[:60]}")
                
                # Check for box characters
                if '□' in text or '\ufffd' in text:
                    print(f"      ⚠️ CONTAINS BOX CHARACTERS!")
                
                # Check encoding
                try:
                    text.encode('utf-8')
                except:
                    print(f"      ❌ UTF-8 encoding failed!")
        
        elif isinstance(first_item, dict):
            print(f"\n⚠️ PLAIN TEXT LYRICS (Genius format)")
            text = first_item.get('text', '')
            lines = text.split('\n')
            print(f"   Total lines: {len(lines)}")
            print(f"\n   First 10 lines:")
            for i, line in enumerate(lines[:10]):
                if line.strip():
                    print(f"   {i+1}. {line[:60]}")
                    
                    if '□' in line or '\ufffd' in line:
                        print(f"      ⚠️ CONTAINS BOX CHARACTERS!")
    
    print(f"\n" + "="*60)
    print("CACHE INSPECTION")
    print("="*60)
    
    # Check cache file
    cache_file = f"lyrics_cache/{artist}_{title}.json"
    if os.path.exists(cache_file):
        print(f"\n📁 Cache file exists: {cache_file}")
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            cached_data = json.load(f)
        
        print(f"   Type: {type(cached_data)}")
        print(f"   Length: {len(cached_data)}")
        
        if cached_data:
            first = cached_data[0]
            print(f"   First item: {first}")
            
            if isinstance(first, list) and len(first) == 3:
                text = first[0]
                print(f"\n   First line text: {text}")
                
                # Hex dump first 20 characters
                print(f"\n   Hex dump of first 20 chars:")
                for i, char in enumerate(text[:20]):
                    print(f"      {i+1:2d}. '{char}' -> U+{ord(char):04X}")
                    
                if '□' in text:
                    print(f"\n   ❌ FOUND BOX CHARACTER!")
                    box_index = text.index('□')
                    print(f"      Position: {box_index}")
                    print(f"      Unicode: U+{ord('□'):04X}")
    else:
        print(f"\n📭 No cache file found")
    
    print(f"\n" + "="*60)
    print("DIAGNOSIS")
    print("="*60)
    
    if lyrics and isinstance(lyrics[0], (tuple, list)):
        # Check if lyrics contain boxes
        has_boxes = any('□' in item[0] for item in lyrics if isinstance(item, (tuple, list)))
        
        if has_boxes:
            print(f"\n❌ PROBLEM: Lyrics DATA contains box characters!")
            print(f"   This means:")
            print(f"   1. LRClib/Genius returned corrupted data, OR")
            print(f"   2. Data was corrupted during fetch/save")
            print(f"\n   🔧 FIX: Clear cache and refetch")
            print(f"      del {cache_file}")
        else:
            print(f"\n✅ Lyrics data looks clean (no boxes)")
            print(f"   Issue must be in rendering pipeline")


if __name__ == "__main__":
    test_lyrics_data()
