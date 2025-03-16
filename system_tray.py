import os
import sys
import tkinter as tk
from infi.systray import SysTrayIcon

class SystemTray:
    def __init__(self, root, show_callback, exit_callback):
        self.root = root
        self.show_callback = show_callback
        self.exit_callback = exit_callback
        
        # Use the assets folder for the icon
        self.icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.ico")
        if not os.path.exists(self.icon_path):
            self.create_default_icon()
        
        # Setup the tray icon
        self.setup_tray()
        
        # Add protocol handler for window closing
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        
        # Create a temporary icon if none exists
        self.icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons8-music-48.png")
        if not os.path.exists(self.icon_path):
            self.create_default_icon()
        
        # Setup the tray icon
        self.setup_tray()
        
        # Add protocol handler for window closing
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
    
    def create_default_icon(self):
        # Create the assets directory if it doesn't exist
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir)
    
        # Create a simple icon image
        from PIL import Image
        img = Image.new('RGB', (16, 16), color=(29, 185, 84))  # Spotify green, smaller size
        img.save(self.icon_path)

    
    def setup_tray(self):
        try:
            # First, check if we already have an icon and shut it down
            if hasattr(self, 'systray'):
                try:
                    self.systray.shutdown()
                except:
                    pass
                
            # Create the menu using the proper constructor
            menu_options = (
                ("Show Lyrics", None, self.show_window),
            )
            
            # Create the tray icon
            self.systray = SysTrayIcon(
                self.icon_path,
                "Spotify Lyrics",
                menu_options,
                on_quit=self.exit_app
            )
            
            # Start the tray icon
            self.systray.start()
            print("System tray icon initialized successfully")
        except Exception as e:
            print(f"Error in system tray: {e}")

    
    def show_window(self, systray=None):
        # Call the show callback or directly show the window
        if self.show_callback:
            self.show_callback()
        else:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
    
    def hide_window(self):
        # Hide the window
        self.root.withdraw()
    
    def exit_app(self, systray=None):
        # Stop the systray if it's running
        if hasattr(self, 'systray'):
            try:
                self.systray.shutdown()
            except RuntimeError as e:
                # Ignore thread joining errors
                print(f"Ignoring thread error during shutdown: {e}")
        
        # Call the exit callback or directly exit using after() to avoid thread issues
        if self.exit_callback:
            self.root.after(0, self.exit_callback)
        else:
            self.root.after(0, self.root.destroy)

        
        # Call the exit callback or directly exit
        if self.exit_callback:
            self.exit_callback()
        else:
            self.root.destroy()
