import requests
from bs4 import BeautifulSoup
import re
import time
import json
import os
from config import GENIUS_ACCESS_TOKEN

class GeniusLyricsFetcher:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.genius.com"
        self.headers = {"Authorization": f"Bearer {api_token}"}
        self.cache_dir = "lyrics_cache"
        
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
    
    def fetch_lyrics(self, artist, title):
        """Fetch lyrics with timing information."""
        # Try to get from cache first
        cached_lyrics = self.get_lyrics_from_cache(artist, title)
        if cached_lyrics:
            return cached_lyrics
        
        # If not in cache, fetch from Genius
        lyrics = self.fetch_lyrics_from_genius(artist, title)
        if lyrics:
            # Save to cache
            self.save_lyrics_to_cache(artist, title, lyrics)
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
            lyrics_text = re.sub(r'\[.*?\]', '', lyrics_text)  # Remove [Verse], [Chorus], etc.
            lyrics_text = re.sub(r'\n{3,}', '\n\n', lyrics_text)  # Normalize line breaks
            lyrics_text = lyrics_text.strip()
            
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
    
    def get_lyrics_from_cache(self, artist, title):
        """Get lyrics from cache with timing information."""
        cache_file = os.path.join(self.cache_dir, f"{artist}_{title}.json")
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
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
        except Exception as e:
            print(f"Error saving to cache: {e}")
