import requests
import json
import time
import webbrowser
import os
import base64
import threading
import tkinter as tk
from tkinter import simpledialog
from urllib.parse import urlencode

class SpotifyClient:
    def __init__(self):
        # Load credentials from config
        from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
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
                # Start authentication in a separate thread to avoid blocking the GUI
                threading.Thread(target=self.get_auth_token, daemon=True).start()
    
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
    
    def get_auth_url():
        client_id = "912a26cedade4d53bd1b45694dc0a789"  # Replace with your actual client ID
        redirect_uri = "http%3A%2F%2F127.0.0.1%3A8888%2Fcallback"
        scope = "user-read-currently-playing+user-read-playback-state"
        
        auth_url = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"
        return auth_url

        
        # Parameters for the auth request
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": "user-read-currently-playing user-read-playback-state",
            "show_dialog": True  # Force login dialog
        }
        
        # Create the auth URL
        auth_url = f"{auth_url}?{urlencode(params)}"
        
        # Open the auth URL in the browser
        print(f"Please visit this URL to authorize the application: {auth_url}")
        webbrowser.open(auth_url)
        
        # Use a dialog to get the redirect URL instead of terminal input
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        redirect_url = simpledialog.askstring("Spotify Authentication", 
                                             "Please login in the browser window that opened.\n\n"
                                             "After authorizing, copy the FULL URL you were redirected to and paste it here:")
        
        if not redirect_url:
            print("Authentication cancelled by user")
            return
        
        # Extract the code from the URL
        try:
            if "?code=" in redirect_url:
                code = redirect_url.split("?code=")[1].split("&")[0]
            elif "code=" in redirect_url:
                code = redirect_url.split("code=")[1].split("&")[0]
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
            threading.Thread(target=self.get_auth_token, daemon=True).start()
    
    def get_current_track(self):
        """
        Get the currently playing track from Spotify.
        Returns a dictionary with track information or None if no track is playing.
        """
        try:
            # Check if token is expired
            if time.time() > self.token_expiry:
                self.refresh_access_token()
            
            # If we don't have a token yet, return None
            if not self.auth_token:
                print("No authentication token available")
                return None
            
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
                return None
            elif response.status_code != 200:
                print(f"Error getting current track: {response.status_code} {response.text}")
                return None
            
            # Parse the response
            data = response.json()
            
            # Check if a track is currently playing
            if not data or not data.get("is_playing", False) or not data.get("item"):
                return None
            
            # Extract the track information
            track = data["item"]
            
            # Return the track information
            return {
                "id": track["id"],
                "name": track["name"],
                "artists": track["artists"],
                "duration_ms": track.get("duration_ms", 0),
                "album": track.get("album", {}).get("name", ""),
                "progress_ms": data.get("progress_ms", 0)
            }
            
        except Exception as e:
            print(f"Error in get_current_track: {e}")
            return None
