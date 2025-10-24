"""
Image processing utilities for UI enhancements
"""
from PIL import Image, ImageDraw, ImageFilter, ImageTk
import requests
from io import BytesIO


def create_circular_image(image: Image.Image, size: tuple = (80, 80)) -> ImageTk.PhotoImage:
    """
    Crop and mask image to circular shape
    
    Args:
        image: PIL Image object
        size: Tuple of (width, height) for output size
        
    Returns:
        PhotoImage ready for tkinter display
    """
    # Resize image to target size
    image = image.resize(size, Image.Resampling.LANCZOS)
    
    # Create circular mask
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    
    # Create output image with transparency
    output = Image.new('RGBA', size, (0, 0, 0, 0))
    output.paste(image, (0, 0))
    output.putalpha(mask)
    
    # Add subtle shadow/border (optional)
    # output = add_circular_shadow(output, size)
    
    return ImageTk.PhotoImage(output)


def add_circular_shadow(image: Image.Image, size: tuple, 
                        shadow_offset: int = 2, blur_radius: int = 4) -> Image.Image:
    """
    Add a subtle drop shadow to circular image
    
    Args:
        image: PIL Image with transparency
        size: Image size tuple
        shadow_offset: Offset for shadow in pixels
        blur_radius: Blur amount for shadow
        
    Returns:
        Image with shadow effect
    """
    # Create a larger canvas for shadow
    shadow_size = (size[0] + blur_radius * 2, size[1] + blur_radius * 2)
    shadow_canvas = Image.new('RGBA', shadow_size, (0, 0, 0, 0))
    
    # Create shadow layer
    shadow = Image.new('RGBA', size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.ellipse((0, 0) + size, fill=(0, 0, 0, 100))
    
    # Blur shadow
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))
    
    # Paste shadow onto canvas
    shadow_canvas.paste(shadow, (blur_radius + shadow_offset, blur_radius + shadow_offset))
    
    # Paste original image on top
    shadow_canvas.paste(image, (blur_radius, blur_radius), image)
    
    return shadow_canvas


def download_image(url: str, fallback_color: str = "#1DB954") -> Image.Image:
    """
    Download image from URL with error handling
    
    Args:
        url: Image URL
        fallback_color: Color to use if download fails
        
    Returns:
        PIL Image object
    """
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        return image.convert('RGBA')
    except Exception as e:
        print(f"Error downloading image: {e}")
        # Return colored placeholder
        return create_placeholder_image(fallback_color)


def create_placeholder_image(color: str = "#1DB954", size: tuple = (300, 300)) -> Image.Image:
    """
    Create a colored placeholder image
    
    Args:
        color: Hex color string
        size: Image size tuple
        
    Returns:
        PIL Image object
    """
    image = Image.new('RGB', size, color)
    return image


def apply_blur(image: Image.Image, radius: int = 10) -> Image.Image:
    """
    Apply Gaussian blur to image
    
    Args:
        image: PIL Image
        radius: Blur radius
        
    Returns:
        Blurred image
    """
    return image.filter(ImageFilter.GaussianBlur(radius))


def adjust_opacity(image: Image.Image, opacity: float) -> Image.Image:
    """
    Adjust image opacity
    
    Args:
        image: PIL Image with RGBA mode
        opacity: Opacity value from 0.0 to 1.0
        
    Returns:
        Image with adjusted opacity
    """
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Get alpha channel
    alpha = image.split()[3]
    
    # Adjust alpha values
    alpha = alpha.point(lambda p: int(p * opacity))
    
    # Put alpha back
    image.putalpha(alpha)
    
    return image


def create_gradient_overlay(size: tuple, 
                           start_color: tuple = (0, 0, 0, 200),
                           end_color: tuple = (0, 0, 0, 0),
                           direction: str = "vertical") -> Image.Image:
    """
    Create a gradient overlay image
    
    Args:
        size: Image size (width, height)
        start_color: RGBA tuple for gradient start
        end_color: RGBA tuple for gradient end
        direction: "vertical" or "horizontal"
        
    Returns:
        PIL Image with gradient
    """
    gradient = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(gradient)
    
    if direction == "vertical":
        for i in range(size[1]):
            progress = i / size[1]
            r = int(start_color[0] + (end_color[0] - start_color[0]) * progress)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * progress)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * progress)
            a = int(start_color[3] + (end_color[3] - start_color[3]) * progress)
            draw.line([(0, i), (size[0], i)], fill=(r, g, b, a))
    else:  # horizontal
        for i in range(size[0]):
            progress = i / size[0]
            r = int(start_color[0] + (end_color[0] - start_color[0]) * progress)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * progress)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * progress)
            a = int(start_color[3] + (end_color[3] - start_color[3]) * progress)
            draw.line([(i, 0), (i, size[1])], fill=(r, g, b, a))
    
    return gradient
