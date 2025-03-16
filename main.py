import sys
import os
import tkinter as tk

# Add the current directory to the path to ensure modules can be found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the LyricsWindow class from the ui module
from ui.lyrics_window import LyricsWindow
from system_tray import SystemTray

def show_window():
    root.deiconify()
    root.lift()
    root.focus_force()

def exit_app():
    root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = LyricsWindow(root)
    
    # Initialize system tray with callbacks
    tray = SystemTray(root, show_window, exit_app)
    
    root.mainloop()
    
def cleanup():
    # Clean up any existing system tray icons
    if hasattr(app, 'system_tray') and app.system_tray is not None:
        try:
            app.system_tray.systray.shutdown()
        except:
            pass
    root.destroy()

# Register the cleanup function
root.protocol("WM_DELETE_WINDOW", cleanup)
