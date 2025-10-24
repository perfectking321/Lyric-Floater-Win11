"""
LRClib API Integration for Synchronized Lyrics
Free, open-source lyrics database with timestamp support
"""

import requests
import re
from typing import Optional, List, Tuple, Dict


class LRClibFetcher:
    """Fetches synchronized lyrics from LRClib.net API"""
    
    def __init__(self):
        self.base_url = "https://lrclib.net/api"
        self.timeout = 10  # seconds
    
    def fetch_synced_lyrics(
        self, 
        artist: str, 
        title: str, 
        album: Optional[str] = None,
        duration: Optional[float] = None
    ) -> Optional[Dict]:
        """
        Fetch lyrics from LRClib API
        
        Args:
            artist: Artist name
            title: Track title
            album: Album name (optional, improves accuracy)
            duration: Track duration in seconds (optional, improves accuracy)
        
        Returns:
            Dict with 'synced_lyrics' (list of tuples) and 'plain_lyrics' (string)
            or None if not found
        """
        try:
            print(f"\n[LRClib] Searching for: {artist} - {title}")
            
            # Build request parameters
            params = {
                'artist_name': artist.strip(),
                'track_name': title.strip()
            }
            
            if album:
                params['album_name'] = album.strip()
            
            if duration:
                params['duration'] = str(int(duration))
            
            # Make API request
            url = f"{self.base_url}/get"
            print(f"[LRClib] Request: {url}")
            print(f"[LRClib] Params: {params}")
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            # Handle not found
            if response.status_code == 404:
                print(f"[LRClib] ❌ Not found in database")
                return None
            
            # Handle other errors
            if response.status_code != 200:
                print(f"[LRClib] ⚠️ API error: {response.status_code}")
                return None
            
            data = response.json()
            
            # Check what we got
            has_synced = data.get('syncedLyrics')
            has_plain = data.get('plainLyrics')
            
            print(f"[LRClib] Response received:")
            print(f"  - Synced lyrics: {'✅ Yes' if has_synced else '❌ No'}")
            print(f"  - Plain lyrics: {'✅ Yes' if has_plain else '❌ No'}")
            
            if not has_synced and not has_plain:
                print(f"[LRClib] ❌ No lyrics in response")
                return None
            
            result = {
                'source': 'lrclib',
                'plain_lyrics': has_plain,
                'synced_lyrics': None,
                'raw_synced': data.get('syncedLyrics'),
                'raw_plain': data.get('plainLyrics')
            }
            
            # Parse synced lyrics if available
            if has_synced:
                print(f"[LRClib] Parsing synced lyrics...")
                synced = self.parse_lrc_format(data['syncedLyrics'])
                if synced:
                    result['synced_lyrics'] = synced
                    print(f"[LRClib] ✅ Successfully parsed {len(synced)} synced lines")
                    print(f"[LRClib] First line: {synced[0][1]}ms - '{synced[0][0][:40]}...'")
                    print(f"[LRClib] Last line: {synced[-1][1]}ms - '{synced[-1][0][:40]}...'")
                else:
                    print(f"[LRClib] ⚠️ Failed to parse synced lyrics")
            
            return result
            
        except requests.exceptions.Timeout:
            print(f"[LRClib] ⚠️ Request timeout after {self.timeout}s")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[LRClib] ⚠️ Network error: {e}")
            return None
        except Exception as e:
            print(f"[LRClib] ⚠️ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def parse_lrc_format(self, lrc_text: str) -> Optional[List[Tuple[str, int, int]]]:
        """
        Parse LRC format lyrics into timed lines
        
        LRC Format: [MM:SS.xx]Lyric line
        Example: [00:12.50]Where are you now?
        
        Args:
            lrc_text: Raw LRC format text
        
        Returns:
            List of tuples: [(line_text, start_ms, end_ms), ...]
            or None if parsing fails
        """
        if not lrc_text:
            return None
        
        try:
            lines = []
            
            # Split by newlines
            raw_lines = lrc_text.strip().split('\n')
            
            for line in raw_lines:
                line = line.strip()
                if not line:
                    continue
                
                # Parse LRC timestamp: [MM:SS.xx] or [MM:SS.xxx]
                match = re.match(r'\[(\d+):(\d+)\.(\d+)\](.*)', line)
                
                if match:
                    minutes = int(match.group(1))
                    seconds = int(match.group(2))
                    centiseconds = match.group(3)
                    text = match.group(4).strip()
                    
                    # Handle different centisecond formats (xx or xxx)
                    if len(centiseconds) == 2:
                        milliseconds = int(centiseconds) * 10  # Convert centiseconds to ms
                    elif len(centiseconds) == 3:
                        milliseconds = int(centiseconds)
                    else:
                        milliseconds = 0
                    
                    # Calculate total milliseconds
                    total_ms = (minutes * 60 * 1000) + (seconds * 1000) + milliseconds
                    
                    # Only add lines with text
                    if text:
                        lines.append((text, total_ms))
            
            if not lines:
                return None
            
            # Calculate end times based on next line's start time
            timed_lines = []
            for i, (text, start_ms) in enumerate(lines):
                if i < len(lines) - 1:
                    # End time is start of next line
                    end_ms = lines[i + 1][1]
                else:
                    # Last line: estimate 5 seconds duration
                    end_ms = start_ms + 5000
                
                timed_lines.append((text, start_ms, end_ms))
            
            return timed_lines
            
        except Exception as e:
            print(f"[LRClib] Error parsing LRC format: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def test_connection(self) -> bool:
        """Test if LRClib API is accessible"""
        try:
            # Try to fetch a popular song
            result = self.fetch_synced_lyrics("Alan Walker", "Faded")
            return result is not None
        except Exception as e:
            print(f"[LRClib] Connection test failed: {e}")
            return False


# Test the fetcher
if __name__ == "__main__":
    fetcher = LRClibFetcher()
    
    print("="*70)
    print("TESTING LRClib FETCHER")
    print("="*70)
    
    # Test 1: Popular song with synced lyrics
    print("\n\nTest 1: Popular Song (should have synced lyrics)")
    print("-" * 70)
    result = fetcher.fetch_synced_lyrics("Alan Walker", "Faded", duration=212)
    
    if result and result['synced_lyrics']:
        print("\n✅ SUCCESS! Got synced lyrics:")
        synced = result['synced_lyrics']
        print(f"Total lines: {len(synced)}")
        print("\nFirst 3 lines:")
        for i in range(min(3, len(synced))):
            text, start, end = synced[i]
            print(f"  [{start/1000:.2f}s - {end/1000:.2f}s] {text}")
    else:
        print("\n❌ FAILED - No synced lyrics found")
    
    # Test 2: Connection test
    print("\n\nTest 2: Connection Test")
    print("-" * 70)
    if fetcher.test_connection():
        print("✅ LRClib API is accessible")
    else:
        print("❌ LRClib API is not accessible")
    
    print("\n" + "="*70)
    input("Press Enter to exit...")
