from PIL import Image, ImageDraw

def create_icon():
    """Creates a simple icon image."""
    # Create a new image with a dark background
    size = (32, 32)
    icon = Image.new('RGBA', size, (18, 18, 18, 255))
    draw = ImageDraw.Draw(icon)
    
    # Draw a simple music note symbol
    color = (29, 185, 84)  # Spotify green
    draw.rectangle([8, 8, 12, 20], fill=color)  # Vertical line
    draw.ellipse([6, 16, 14, 24], fill=color)   # Note head
    draw.rectangle([12, 8, 24, 12], fill=color)  # Horizontal line
    
    return icon

def get_icon():
    """Returns an Image object containing the app icon."""
    return create_icon()

def save_icon(path="app.ico"):
    """Saves the icon as an ICO file."""
    icon = create_icon()
    icon.save(path, format="ICO") 
