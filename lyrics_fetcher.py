import requests
from bs4 import BeautifulSoup
import re
import time
import json
import os
from config import GENIUS_ACCESS_TOKEN
from lrclib_fetcher import LRClibFetcher

class GeniusLyricsFetcher:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.genius.com"
        self.headers = {"Authorization": f"Bearer {api_token}"}
        self.cache_dir = "lyrics_cache"
        
        # Initialize LRClib fetcher for synced lyrics
        self.lrclib_fetcher = LRClibFetcher()
        print("[LyricsFetcher] Initialized with LRClib + Genius fallback")
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def parse_lyrics_with_timing(self, lyrics_text):
        """Parse lyrics text and create estimated timings."""
        lines = lyrics_text.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        total_lines = len(non_empty_lines)
        
        # Create timing estimates (distribute evenly across estimated song duration)
        timings = []
        current_line = 0
        
        for line in lines:
            if line.strip():
                # Store line with timing information
                timing = {
                    'text': line.strip(),
                    'start_time': None,  # Will be set during playback
                    'duration': None,    # Will be set during playback
                    'line_number': current_line
                }
                timings.append(timing)
                current_line += 1
        
        return timings
    
    def fetch_lyrics(self, artist, title, album=None, duration=None):
        """
        Fetch lyrics with timing information.
        Priority: Cache → LRClib (synced) → Genius (fallback)
        
        Args:
            artist: Artist name
            title: Track title
            album: Album name (optional, improves LRClib accuracy)
            duration: Track duration in seconds (optional, improves LRClib accuracy)
        """
        print(f"\n{'='*70}")
        print(f"[LyricsFetcher] Fetching lyrics for: {artist} - {title}")
        if album:
            print(f"[LyricsFetcher] Album: {album}")
        if duration:
            print(f"[LyricsFetcher] Duration: {duration}s")
        print(f"{'='*70}")
        
        # Try to get from cache first
        cached_lyrics = self.get_lyrics_from_cache(artist, title)
        if cached_lyrics:
            print("[LyricsFetcher] ✅ Found in cache")
            return cached_lyrics
        
        # Try LRClib first (has synced lyrics!)
        print("[LyricsFetcher] 🎵 Trying LRClib API (synced lyrics)...")
        lrclib_result = self.lrclib_fetcher.fetch_synced_lyrics(
            artist, title, album, duration
        )
        
        if lrclib_result:
            # Check if we got synced lyrics
            if lrclib_result.get('synced_lyrics'):
                print("[LyricsFetcher] ✅ SUCCESS! Got synced lyrics from LRClib")
                synced_lyrics = lrclib_result['synced_lyrics']
                print(f"[LyricsFetcher] Lines: {len(synced_lyrics)}")
                print(f"[LyricsFetcher] First: {synced_lyrics[0][1]}ms - '{synced_lyrics[0][0][:40]}'")
                print(f"[LyricsFetcher] Last: {synced_lyrics[-1][1]}ms - '{synced_lyrics[-1][0][:40]}'")
                
                # Save to cache
                self.save_lyrics_to_cache(artist, title, synced_lyrics)
                return synced_lyrics
            
            # Check if we got plain lyrics
            elif lrclib_result.get('raw_plain'):
                print("[LyricsFetcher] ⚠️ Got plain lyrics from LRClib (no timestamps)")
                plain_text = lrclib_result['raw_plain']
                # Convert to our format and save
                lyrics_with_timing = self.parse_lyrics_with_timing(plain_text)
                if lyrics_with_timing:
                    self.save_lyrics_to_cache(artist, title, lyrics_with_timing)
                    return lyrics_with_timing
        
        # Fallback to Genius
        print("[LyricsFetcher] 🔄 Falling back to Genius API...")
        lyrics = self.fetch_lyrics_from_genius(artist, title)
        if lyrics:
            print("[LyricsFetcher] ✅ Got lyrics from Genius (estimated timing)")
            # Save to cache
            self.save_lyrics_to_cache(artist, title, lyrics)
        else:
            print("[LyricsFetcher] ❌ No lyrics found from any source")
        
        return lyrics
    
    def fetch_lyrics_from_genius(self, artist, title):
        """Fetch lyrics from Genius API with timing information."""
        try:
            print(f"\nFetching lyrics for: {artist} - {title}")
            
            # Clean up artist and title
            artist = re.sub(r'feat\.|ft\.|\(.*?\)|\[.*?\]', '', artist).strip()
            title = re.sub(r'\(.*?\)|\[.*?\]', '', title).strip()
            print(f"Cleaned up search terms: {artist} - {title}")
            
            # Search for the song
            search_url = f"{self.base_url}/search"
            params = {"q": f"{artist} {title}"}
            print(f"Searching Genius API: {search_url}")
            response = requests.get(search_url, headers=self.headers, params=params)
            response.raise_for_status()
            
            # Get the first hit
            data = response.json()
            hits = data["response"]["hits"]
            if not hits:
                print("No results found on Genius")
                return None
            
            # Get the lyrics URL
            result = hits[0]["result"]
            lyrics_url = result["url"]
            print(f"Found lyrics URL: {lyrics_url}")
            
            # Scrape the lyrics
            print("Fetching lyrics page...")
            page = requests.get(lyrics_url)
            soup = BeautifulSoup(page.content, 'html.parser')
            
            # Try different possible lyrics container classes
            lyrics_text = None
            
            # Try the old lyrics div first
            lyrics_div = soup.find("div", class_="lyrics")
            if lyrics_div:
                print("Found lyrics in old format")
                lyrics_text = lyrics_div.get_text()
            
            # Try the new Lyrics Container
            if not lyrics_text:
                lyrics_div = soup.find("div", class_="Lyrics__Container-sc-1ynbvzw-6")
                if lyrics_div:
                    print("Found lyrics in new format")
                    lyrics_text = lyrics_div.get_text()
            
            # Try the newest data-lyrics-container format
            if not lyrics_text:
                lyrics_divs = soup.find_all("div", attrs={"data-lyrics-container": "true"})
                if lyrics_divs:
                    print("Found lyrics in newest format")
                    lyrics_text = "\n".join(div.get_text() for div in lyrics_divs)
            
            if not lyrics_text:
                print("Could not find lyrics in the page")
                return None
            
            # Clean up lyrics text
            print("Cleaning up lyrics text...")
            lyrics_text = self._clean_genius_lyrics(lyrics_text)
            
            if not lyrics_text:
                print("No lyrics text after cleanup")
                return None
            
            # Parse lyrics with timing information
            print("Parsing lyrics with timing information...")
            lyrics_with_timing = self.parse_lyrics_with_timing(lyrics_text)
            
            if lyrics_with_timing:
                print(f"Successfully parsed {len(lyrics_with_timing)} lines")
                return lyrics_with_timing
            else:
                print("No lines parsed from lyrics text")
                return None
            
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching lyrics: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing Genius API response: {e}")
            return None
        except Exception as e:
            print(f"Error fetching lyrics from Genius: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _clean_genius_lyrics(self, lyrics_text):
        """Clean up lyrics text from Genius - remove metadata and extra content"""
        # Remove section markers like [Verse 1], [Chorus], etc.
        lyrics_text = re.sub(r'\[.*?\]', '', lyrics_text)
        
        # Split into lines for filtering
        lines = lyrics_text.split('\n')
        cleaned_lines = []
        
        # Patterns to skip
        skip_patterns = [
            r'^\d+$',  # Just numbers
            r'embed$',  # "Embed" links
            r'see.*live',  # "See X live"
            r'get tickets',
            r'^\d+\s*contributors?',  # "X Contributors"
            r'you might also like',
            r'genius.*annotation',
            r'^\s*$'  # Empty lines (we'll add back spacing)
        ]
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Skip if matches any skip pattern
            should_skip = False
            for pattern in skip_patterns:
                if re.search(pattern, line_lower):
                    should_skip = True
                    break
            
            if not should_skip and line.strip():
                cleaned_lines.append(line.strip())
        
        # Join lines back
        lyrics_text = '\n'.join(cleaned_lines)
        
        # Normalize line breaks
        lyrics_text = re.sub(r'\n{3,}', '\n\n', lyrics_text)
        lyrics_text = lyrics_text.strip()
        
        return lyrics_text
    
    def get_lyrics_from_cache(self, artist, title):
        """Get lyrics from cache with timing information."""
        cache_file = os.path.join(self.cache_dir, f"{artist}_{title}.json")
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert list format back to tuples for synced lyrics
                if isinstance(data, list) and len(data) > 0:
                    first_item = data[0]
                    
                    # Check if it's synced format (list of 3 items: text, start_ms, end_ms)
                    if isinstance(first_item, list) and len(first_item) == 3:
                        # Convert lists back to tuples
                        print(f"[Cache] ✅ Found synced lyrics in cache")
                        return [(item[0], item[1], item[2]) for item in data]
                    
                    # Old Genius format (dict with 'text' key) - IGNORE and refetch
                    elif isinstance(first_item, dict):
                        print("[Cache] ⚠️ Found OLD cache format (Genius), will refetch with LRClib")
                        return None
                
                return data
            return None
        except Exception as e:
            print(f"Error reading from cache: {e}")
            return None
    
    def save_lyrics_to_cache(self, artist, title, lyrics):
        """Save lyrics to cache with timing information."""
        cache_file = os.path.join(self.cache_dir, f"{artist}_{title}.json")
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(lyrics, f, ensure_ascii=False, indent=2)
            print(f"[Cache] ✅ Saved to cache: {artist}_{title}")
        except Exception as e:
            print(f"Error saving to cache: {e}")
