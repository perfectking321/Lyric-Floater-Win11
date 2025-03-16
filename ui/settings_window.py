import tkinter as tk
from tkinter import ttk, colorchooser
import json
import os
import sys

# Add parent directory to path to find modules in main directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.styles import BACKGROUND_COLOR, TEXT_COLOR, HIGHLIGHT_COLOR, FONT_FAMILY, FONT_SIZE

class SettingsWindow:
    def __init__(self, parent, apply_callback):
        self.parent = parent
        self.apply_callback = apply_callback
        
        # Create settings window
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("400x500")
        self.window.configure(bg=BACKGROUND_COLOR)
        self.window.transient(parent)  # Make this window related to the parent
        self.window.grab_set()  # Make this window modal
        
        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create appearance tab
        self.appearance_frame = tk.Frame(self.notebook, bg=BACKGROUND_COLOR)
        self.notebook.add(self.appearance_frame, text="Appearance")
        
        # Background color
        tk.Label(self.appearance_frame, text="Background Color:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor='w', pady=(10, 0))
        self.bg_color_frame = tk.Frame(self.appearance_frame, bg=BACKGROUND_COLOR)
        self.bg_color_frame.pack(fill='x', pady=5)
        
        self.bg_color_preview = tk.Label(self.bg_color_frame, text="   ", bg=BACKGROUND_COLOR, width=3, height=1, borderwidth=1, relief="solid")
        self.bg_color_preview.pack(side='left', padx=5)
        
        self.bg_color_button = tk.Button(self.bg_color_frame, text="Change", command=self.choose_bg_color)
        self.bg_color_button.pack(side='left', padx=5)
        
        # Text color
        tk.Label(self.appearance_frame, text="Text Color:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor='w', pady=(10, 0))
        self.text_color_frame = tk.Frame(self.appearance_frame, bg=BACKGROUND_COLOR)
        self.text_color_frame.pack(fill='x', pady=5)
        
        self.text_color_preview = tk.Label(self.text_color_frame, text="   ", bg=TEXT_COLOR, width=3, height=1, borderwidth=1, relief="solid")
        self.text_color_preview.pack(side='left', padx=5)
        
        self.text_color_button = tk.Button(self.text_color_frame, text="Change", command=self.choose_text_color)
        self.text_color_button.pack(side='left', padx=5)
        
        # Font settings
        tk.Label(self.appearance_frame, text="Font:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor='w', pady=(10, 0))
        self.font_frame = tk.Frame(self.appearance_frame, bg=BACKGROUND_COLOR)
        self.font_frame.pack(fill='x', pady=5)
        
        self.font_var = tk.StringVar(value=FONT_FAMILY)
        self.font_options = ["Arial", "Helvetica", "Times New Roman", "Courier New", "Verdana"]
        self.font_dropdown = ttk.Combobox(self.font_frame, textvariable=self.font_var, values=self.font_options)
        self.font_dropdown.pack(side='left', padx=5, fill='x', expand=True)
        
        # Font size
        tk.Label(self.appearance_frame, text="Font Size:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor='w', pady=(10, 0))
        self.font_size_frame = tk.Frame(self.appearance_frame, bg=BACKGROUND_COLOR)
        self.font_size_frame.pack(fill='x', pady=5)
        
        self.font_size_var = tk.IntVar(value=FONT_SIZE)
        self.font_size_scale = tk.Scale(self.font_size_frame, from_=8, to=20, orient='horizontal', 
                                      variable=self.font_size_var, bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                                      highlightbackground=BACKGROUND_COLOR)
        self.font_size_scale.pack(fill='x', padx=5)
        
        # Opacity
        tk.Label(self.appearance_frame, text="Window Opacity:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor='w', pady=(10, 0))
        self.opacity_frame = tk.Frame(self.appearance_frame, bg=BACKGROUND_COLOR)
        self.opacity_frame.pack(fill='x', pady=5)
        
        self.opacity_var = tk.DoubleVar(value=0.85)
        self.opacity_scale = tk.Scale(self.opacity_frame, from_=0.3, to=1.0, resolution=0.05, orient='horizontal', 
                                    variable=self.opacity_var, bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                                    highlightbackground=BACKGROUND_COLOR)
        self.opacity_scale.pack(fill='x', padx=5)
        
        # Create API settings tab
        self.api_frame = tk.Frame(self.notebook, bg=BACKGROUND_COLOR)
        self.notebook.add(self.api_frame, text="API Settings")
        
        # Genius API Token
        tk.Label(self.api_frame, text="Genius API Token:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor='w', pady=(10, 0))
        self.genius_token_var = tk.StringVar()
        self.genius_token_entry = tk.Entry(self.api_frame, textvariable=self.genius_token_var, show="*", 
                                         bg="#333333", fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.genius_token_entry.pack(fill='x', padx=5, pady=5)
        
        # Spotify Client ID
        tk.Label(self.api_frame, text="Spotify Client ID:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor='w', pady=(10, 0))
        self.spotify_id_var = tk.StringVar()
        self.spotify_id_entry = tk.Entry(self.api_frame, textvariable=self.spotify_id_var, 
                                       bg="#333333", fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.spotify_id_entry.pack(fill='x', padx=5, pady=5)
        
        # Spotify Client Secret
        tk.Label(self.api_frame, text="Spotify Client Secret:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(anchor='w', pady=(10, 0))
        self.spotify_secret_var = tk.StringVar()
        self.spotify_secret_entry = tk.Entry(self.api_frame, textvariable=self.spotify_secret_var, show="*", 
                                           bg="#333333", fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.spotify_secret_entry.pack(fill='x', padx=5, pady=5)
        
        # Load existing settings
        self.load_settings()
        
        # Create buttons frame
        self.buttons_frame = tk.Frame(self.window, bg=BACKGROUND_COLOR)
        self.buttons_frame.pack(fill='x', padx=10, pady=10)
        
        # Add Save and Cancel buttons
        self.save_button = tk.Button(self.buttons_frame, text="Save", command=self.save_settings)
        self.save_button.pack(side='right', padx=5)
        
        self.cancel_button = tk.Button(self.buttons_frame, text="Cancel", command=self.window.destroy)
        self.cancel_button.pack(side='right', padx=5)
    
    def choose_bg_color(self):
        color = colorchooser.askcolor(initialcolor=BACKGROUND_COLOR)[1]
        if color:
            self.bg_color_preview.config(bg=color)
    
    def choose_text_color(self):
        color = colorchooser.askcolor(initialcolor=TEXT_COLOR)[1]
        if color:
            self.text_color_preview.config(bg=color)
    
    def load_settings(self):
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    settings = json.load(f)
                    
                    # Load appearance settings
                    self.bg_color_preview.config(bg=settings.get("background_color", BACKGROUND_COLOR))
                    self.text_color_preview.config(bg=settings.get("text_color", TEXT_COLOR))
                    self.font_var.set(settings.get("font_family", FONT_FAMILY))
                    self.font_size_var.set(settings.get("font_size", FONT_SIZE))
                    self.opacity_var.set(settings.get("opacity", 0.85))
                    
                    # Load API settings
                    self.genius_token_var.set(settings.get("genius_token", ""))
                    self.spotify_id_var.set(settings.get("spotify_client_id", ""))
                    self.spotify_secret_var.set(settings.get("spotify_client_secret", ""))
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        try:
            settings = {
                # Appearance settings
                "background_color": self.bg_color_preview.cget("bg"),
                "text_color": self.text_color_preview.cget("bg"),
                "font_family": self.font_var.get(),
                "font_size": self.font_size_var.get(),
                "opacity": self.opacity_var.get(),
                
                # API settings
                "genius_token": self.genius_token_var.get(),
                "spotify_client_id": self.spotify_id_var.get(),
                "spotify_client_secret": self.spotify_secret_var.get()
            }
            
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=2)
            
            # Update config.py with API settings
            with open("config.py", "w") as f:
                f.write(f'GENIUS_ACCESS_TOKEN = "{self.genius_token_var.get()}"\n')
                f.write(f'SPOTIFY_CLIENT_ID = "{self.spotify_id_var.get()}"\n')
                f.write(f'SPOTIFY_CLIENT_SECRET = "{self.spotify_secret_var.get()}"\n')
            
            # Call the callback to apply changes
            self.apply_callback(settings)
            
            # Close the window
            self.window.destroy()
        except Exception as e:
            print(f"Error saving settings: {e}")
