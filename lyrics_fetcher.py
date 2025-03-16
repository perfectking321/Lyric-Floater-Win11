import requests
from bs4 import BeautifulSoup
import re
import time
import json
import os
from config import GENIUS_ACCESS_TOKEN

class GeniusLyricsFetcher:
    def __init__(self, api_token):
        self.genius_access_token = api_token
        self.headers = {
            'Authorization': f'Bearer {self.genius_access_token}'
        }
        self.base_url = 'https://api.genius.com'
        self.search_url = f'{self.base_url}/search'
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        
    def fetch_lyrics_from_genius(self, artist, title):
        """
        Fetch lyrics from Genius for a given artist and title.
        """
        try:
            # Clean up artist and title
            artist = re.sub(r'feat\.|ft\.|\(.*?\)|\[.*?\]', '', artist).strip()
            title = re.sub(r'\(.*?\)|\[.*?\]', '', title).strip()
            
            # Search for the song
            search_term = f"{artist} {title}"
            params = {'q': search_term}
            response = self.session.get(self.search_url, params=params)
            
            if response.status_code != 200:
                print(f"Error searching for lyrics: {response.status_code}")
                return None
            
            data = response.json()
            
            # Check if we got any hits
            if 'response' not in data or 'hits' not in data['response'] or not data['response']['hits']:
                print(f"No results found for {search_term}")
                return None
            
            # Find the best match
            best_match = None
            for hit in data['response']['hits']:
                if hit['type'] == 'song':
                    result = hit['result']
                    result_artist = result['primary_artist']['name'].lower()
                    result_title = result['title'].lower()
                    
                    # Check if this is a good match
                    if (artist.lower() in result_artist or result_artist in artist.lower()) and \
                       (title.lower() in result_title or result_title in title.lower()):
                        best_match = result
                        break
            
            if not best_match and data['response']['hits']:
                # Just take the first result if no good match
                best_match = data['response']['hits'][0]['result']
            
            if not best_match:
                print(f"No matching song found for {search_term}")
                return None
            
            # Get the lyrics URL
            lyrics_url = best_match['url']
            
            # Scrape the lyrics from the URL
            lyrics = self._scrape_lyrics_from_url(lyrics_url)
            
            if not lyrics:
                print(f"Could not scrape lyrics from {lyrics_url}")
                return None
            
            return lyrics
            
        except Exception as e:
            print(f"Error fetching lyrics from Genius: {e}")
            return None
    
    def _scrape_lyrics_from_url(self, url):
        """
        Scrape lyrics from a Genius URL.
        """
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all divs with the data-lyrics-container attribute
            lyrics_containers = soup.find_all('div', attrs={'data-lyrics-container': 'true'})
            
            if not lyrics_containers:
                return None
            
            # Extract and process the lyrics
            lyrics = []
            for container in lyrics_containers:
                # Get the HTML content
                content = str(container)
                
                # Replace <br> tags with newlines
                content = content.replace('<br/>', '\n')
                
                # Create a new soup object with the modified content
                container_soup = BeautifulSoup(content, 'html.parser')
                
                # Get the text and preserve newlines
                container_text = container_soup.get_text('\n')
                lyrics.append(container_text)
            
            # Join all lyrics sections
            full_lyrics = '\n'.join(lyrics)
            
            # Clean up the lyrics
            full_lyrics = re.sub(r'\[.*?\]', '', full_lyrics)  # Remove [Verse], [Chorus], etc.
            full_lyrics = re.sub(r'\n{3,}', '\n\n', full_lyrics)  # Replace multiple newlines with double newlines
            full_lyrics = full_lyrics.strip()
            
            return full_lyrics
            
        except Exception as e:
            print(f"Error scraping lyrics: {e}")
            return None
    
    def save_lyrics_to_cache(self, artist, title, lyrics):
        """
        Save lyrics to a cache file.
        """
        try:
            # Create a cache directory if it doesn't exist
            os.makedirs('lyrics_cache', exist_ok=True)
            
            # Create a cache key
            cache_key = f"{artist}_{title}".lower()
            cache_key = re.sub(r'[^\w]', '_', cache_key)
            cache_file = os.path.join('lyrics_cache', f"{cache_key}.json")
            
            # Save to cache
            cache_data = {
                'artist': artist,
                'title': title,
                'lyrics': lyrics,
                'timestamp': time.time()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Error saving lyrics to cache: {e}")
            return False
    
    def get_lyrics_from_cache(self, artist, title):
        """
        Get lyrics from the cache if available.
        """
        try:
            # Create a cache key
            cache_key = f"{artist}_{title}".lower()
            cache_key = re.sub(r'[^\w]', '_', cache_key)
            cache_file = os.path.join('lyrics_cache', f"{cache_key}.json")
            
            # Check if cache file exists
            if not os.path.exists(cache_file):
                return None
            
            # Load from cache
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache is too old (1 week)
            if time.time() - cache_data.get('timestamp', 0) > 7 * 24 * 60 * 60:
                return None
            
            return cache_data.get('lyrics')
            
        except Exception as e:
            print(f"Error getting lyrics from cache: {e}")
            return None
