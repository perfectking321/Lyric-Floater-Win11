import subprocess
import re

class LyricstifyFetcher:
    def __init__(self, lyricstify_path):
        self.lyricstify_path = lyricstify_path
    
    def get_current_lyrics(self):
        try:
            # Use the full path to cli.js with node
            process = subprocess.Popen(
                ["node", f"{self.lyricstify_path}/dist/cli.js", "pipe"],
                stdout=subprocess.PIPE,
                text=True,
                cwd=self.lyricstify_path  # Set working directory
            )
            
            lyrics = []
            
            for line in process.stdout:
                clean_line = line.strip()
                if clean_line:  # Skip empty lines
                    # Simple heuristic to detect current line (first character is *)
                    if clean_line.startswith('*'):
                        current_line = clean_line.replace('*', '', 1).strip()
                        lyrics.append({"text": current_line, "current": True})
                    else:
                        lyrics.append({"text": clean_line, "current": False})
            
            return lyrics
            
        except Exception as e:
            print(f"Error getting lyrics from Lyricstify: {e}")
            import traceback
            traceback.print_exc()
            return []
