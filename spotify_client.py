import requests
import json
import time
import webbrowser
import os
import base64
from urllib.parse import urlencode, parse_qs, urlparse
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

class SpotifyClient:
    def __init__(self):
        self.client_id = SPOTIFY_CLIENT_ID
        self.client_secret = SPOTIFY_CLIENT_SECRET
        self.redirect_uri = "http://127.0.0.1:8888/callback"
        self.auth_token = None
        self.refresh_token = None
        self.token_expiry = 0
        
        # Load tokens if they exist
        self.load_tokens()
        
        # Get new tokens if needed
        if not self.auth_token or time.time() > self.token_expiry:
            if self.refresh_token:
                self.refresh_access_token()
            else:
                self.get_auth_token()
    
    def load_tokens(self):
        try:
            if os.path.exists("spotify_tokens.json"):
                with open("spotify_tokens.json", "r") as f:
                    tokens = json.load(f)
                    self.auth_token = tokens.get("auth_token")
                    self.refresh_token = tokens.get("refresh_token")
                    self.token_expiry = tokens.get("token_expiry", 0)
        except Exception as e:
            print(f"Error loading tokens: {e}")
    
    def save_tokens(self):
        try:
            tokens = {
                "auth_token": self.auth_token,
                "refresh_token": self.refresh_token,
                "token_expiry": self.token_expiry
            }
            with open("spotify_tokens.json", "w") as f:
                json.dump(tokens, f)
        except Exception as e:
            print(f"Error saving tokens: {e}")
    
    def get_auth_token(self):
        # Spotify authorization URL
        auth_url = "https://accounts.spotify.com/authorize"
        
        # Parameters for the auth request
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": "user-read-currently-playing user-read-playback-state user-modify-playback-state",
            "show_dialog": True  # Force login dialog
        }
        
        # Create the auth URL
        auth_url = f"{auth_url}?{urlencode(params)}"
        
        # Open the auth URL in the browser
        print(f"Please visit this URL to authorize the application: {auth_url}")
        webbrowser.open(auth_url)
        
        # Get the auth code from the redirect URL
        redirect_url = input("Enter the full redirect URL you were sent to: ")
        
        # Extract the code from the URL - Fixed to handle different URL formats
        try:
            # Try to parse the URL and extract the code parameter
            if "?" in redirect_url:
                code = redirect_url.split("?code=")[1].split("&")[0]
            else:
                print("Invalid redirect URL. Please make sure you copy the entire URL.")
                return
        except IndexError:
            print("Error extracting code from redirect URL")
            print("Please make sure you copy the entire URL including the code parameter")
            return
        
        # Exchange the code for an access token
        token_url = "https://accounts.spotify.com/api/token"
        
        # Prepare the authorization header
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        
        # Prepare the request data
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        
        # Make the request
        response = requests.post(
            token_url,
            headers={
                "Authorization": f"Basic {auth_header}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data=data
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response
            token_data = response.json()
            
            # Save the tokens
            self.auth_token = token_data["access_token"]
            self.refresh_token = token_data["refresh_token"]
            self.token_expiry = time.time() + token_data["expires_in"]
            
            # Save the tokens to a file
            self.save_tokens()
            print("Authentication successful!")
        else:
            print(f"Error getting auth token: {response.status_code} {response.text}")
    
    def refresh_access_token(self):
        # Spotify token URL
        token_url = "https://accounts.spotify.com/api/token"
        
        # Prepare the authorization header
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        
        # Prepare the request data
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        
        # Make the request
        response = requests.post(
            token_url,
            headers={
                "Authorization": f"Basic {auth_header}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data=data
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response
            token_data = response.json()
            
            # Save the tokens
            self.auth_token = token_data["access_token"]
            if "refresh_token" in token_data:
                self.refresh_token = token_data["refresh_token"]
            self.token_expiry = time.time() + token_data["expires_in"]
            
            # Save the tokens to a file
            self.save_tokens()
        else:
            print(f"Error refreshing token: {response.status_code} {response.text}")
            # If refresh fails, get a new auth token
            self.get_auth_token()
    
    def get_current_track(self):
        """
        Get the currently playing track from Spotify.
        Returns a dictionary with track information or None if no track is playing.
        """
        try:
            # Check if token is expired
            if time.time() > self.token_expiry:
                self.refresh_access_token()
            
            # Make the request to Spotify API
            response = requests.get(
                "https://api.spotify.com/v1/me/player/currently-playing",
                headers={
                    "Authorization": f"Bearer {self.auth_token}"
                }
            )
            
            # Handle different response codes
            if response.status_code == 204:
                # No content - no track playing
                print("No track currently playing")
                return None
            elif response.status_code != 200:
                print(f"Error getting current track: {response.status_code} {response.text}")
                return None
            
            # Parse the response
            data = response.json()
            
            # Check if a track is currently playing
            if not data or not data.get("is_playing", False) or not data.get("item"):
                print("No track currently playing or track data missing")
                return None
            
            # Extract the track information
            track = data["item"]
            
            # Return the track information
            return {
                "id": track["id"],
                "name": track["name"],
                "artists": track["artists"],
                "duration_ms": track.get("duration_ms", 0),
                "album": track.get("album", {}),
                "progress_ms": data.get("progress_ms", 0)
            }
            
        except Exception as e:
            print(f"Error in get_current_track: {e}")
            return None
    
    def get_playback_state(self):
        """
        Get the current playback state from Spotify.
        Returns a dictionary with playback information or None if no track is playing.
        """
        try:
            # Check if token is expired
            if time.time() > self.token_expiry:
                self.refresh_access_token()
            
            # Make the request to Spotify API
            response = requests.get(
                "https://api.spotify.com/v1/me/player",
                headers={
                    "Authorization": f"Bearer {self.auth_token}"
                }
            )
            
            # Handle different response codes
            if response.status_code == 204:
                # No content - no track playing
                return None
            elif response.status_code != 200:
                print(f"Error getting playback state: {response.status_code} {response.text}")
                return None
            
            # Parse and return the response
            return response.json()
            
        except Exception as e:
            print(f"Error in get_playback_state: {e}")
            return None
    
    def start_playback(self):
        """Start or resume playback."""
        try:
            # Check if token is expired
            if time.time() > self.token_expiry:
                self.refresh_access_token()
            
            # Make the request to Spotify API
            response = requests.put(
                "https://api.spotify.com/v1/me/player/play",
                headers={
                    "Authorization": f"Bearer {self.auth_token}"
                }
            )
            
            if response.status_code not in [204, 202]:
                print(f"Error starting playback: {response.status_code} {response.text}")
                
        except Exception as e:
            print(f"Error in start_playback: {e}")
    
    def pause_playback(self):
        """Pause playback."""
        try:
            # Check if token is expired
            if time.time() > self.token_expiry:
                self.refresh_access_token()
            
            # Make the request to Spotify API
            response = requests.put(
                "https://api.spotify.com/v1/me/player/pause",
                headers={
                    "Authorization": f"Bearer {self.auth_token}"
                }
            )
            
            if response.status_code not in [204, 202]:
                print(f"Error pausing playback: {response.status_code} {response.text}")
                
        except Exception as e:
            print(f"Error in pause_playback: {e}")
    
    def next_track(self):
        """Skip to next track."""
        try:
            # Check if token is expired
            if time.time() > self.token_expiry:
                self.refresh_access_token()
            
            # Make the request to Spotify API
            response = requests.post(
                "https://api.spotify.com/v1/me/player/next",
                headers={
                    "Authorization": f"Bearer {self.auth_token}"
                }
            )
            
            if response.status_code not in [204, 202]:
                print(f"Error skipping to next track: {response.status_code} {response.text}")
                
        except Exception as e:
            print(f"Error in next_track: {e}")
    
    def previous_track(self):
        """Skip to previous track."""
        try:
            # Check if token is expired
            if time.time() > self.token_expiry:
                self.refresh_access_token()
            
            # Make the request to Spotify API
            response = requests.post(
                "https://api.spotify.com/v1/me/player/previous",
                headers={
                    "Authorization": f"Bearer {self.auth_token}"
                }
            )
            
            if response.status_code not in [204, 202]:
                print(f"Error skipping to previous track: {response.status_code} {response.text}")
                
        except Exception as e:
            print(f"Error in previous_track: {e}")
