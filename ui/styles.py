# styles.py - Apple Music Inspired Color Scheme

# Background Colors
BACKGROUND_COLOR = "#000000"
BACKGROUND_OPACITY = 0.80  # 80% opacity for frosted glass effect
OVERLAY_COLOR = "#000000"
OVERLAY_OPACITY = 0.50

# Text Colors
TEXT_COLOR = "#FFFFFF"  # Main text (legacy compatibility)
TEXT_MUTED = "#6B7280"  # Past/upcoming lyrics
TEXT_ACTIVE = "#FFFFFF"  # Current line
TEXT_UPCOMING = "#9CA3AF"  # Next few lines
TEXT_PAST = "#4B5563"  # Past lines
TEXT_INFO = "#D1D5DB"  # Song info
TEXT_SECONDARY = "#9CA3AF"  # Artist, album

# Accent Colors
HIGHLIGHT_COLOR = "#FF2D55"  # Apple Music pink
ACCENT_COLOR = "#FF2D55"  # Apple Music pink
ACCENT_SECONDARY = "#1DB954"  # Spotify green (for fallbacks)
SECONDARY_COLOR = "#1A1A1A"
BUTTON_HOVER_COLOR = "#2A2A2A"
PROGRESS_BAR_COLOR = "#FFFFFF"
PROGRESS_COLOR = "#FFFFFF"
PROGRESS_BG = "#374151"
DISABLED_COLOR = "#4B5563"

# Font Settings
FONT_FAMILY = "Segoe UI"
FONT_SIZE = 14  # Base lyrics size
FONT_SIZE_CURRENT = 18  # Current line size
FONT_SIZE_TITLE = 18  # Song title
FONT_SIZE_INFO = 14  # Artist name
FONT_SIZE_SMALL = 12  # Album, timestamps
TITLE_FONT_SIZE = 18
BUTTON_FONT_SIZE = 16

# Opacity Levels
OPACITY_CURRENT = 1.0  # Current line
OPACITY_NEXT_1 = 0.7  # Next line
OPACITY_NEXT_2 = 0.5  # Line after next
OPACITY_NEXT_3 = 0.3  # Further lines
OPACITY_PAST = 0.4  # Past lines
OPACITY_FAR = 0.2  # Far away lines

# Animation Timings (in milliseconds)
ANIMATION_FAST = 150  # Button hover
ANIMATION_NORMAL = 300  # Line transitions
ANIMATION_SMOOTH = 500  # Auto-scroll

# Lyrics Timing Configuration
LYRICS_OFFSET_MS = -1000  # Delay by 1000ms (1 second) after singing
# Positive value = highlight AFTER lyrics are sung
# Negative value = highlight BEFORE lyrics are sung (read-ahead)
# Zero = exact timing from LRClib
ANIMATION_FADE = 400  # Fade in/out

# Performance Settings (Phase 2 Optimizations)
VIRTUAL_SCROLLING_ENABLED = True  # Use virtual scrolling (only render visible lines)
VISIBLE_LINES_BUFFER = 3  # Extra lines to render above/below viewport
ANIMATION_FPS = 60  # Target FPS for animations
BATCH_CANVAS_UPDATES = True  # Batch canvas updates for better performance
ANIMATE_FONT_SIZE = False  # Disable font size animation for smoother performance

# Layout Dimensions
ALBUM_ART_SIZE = 80  # Circular album art
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 700
LYRICS_PADDING = 40
LINE_SPACING = 1.8
CONTROL_HEIGHT = 120
HEADER_HEIGHT = 120

# Button Styling
BUTTON_STYLE = {
    'background': SECONDARY_COLOR,
    'foreground': TEXT_COLOR,
    'activebackground': BUTTON_HOVER_COLOR,
    'activeforeground': TEXT_COLOR,
    'borderwidth': 0,
    'relief': 'flat',
    'padx': 10,
    'pady': 5,
    'cursor': 'hand2'
}

# Progress Bar Styling
PROGRESS_BAR_STYLE = {
    'troughcolor': PROGRESS_BG,
    'background': PROGRESS_COLOR,
    'thickness': 4,
    'borderwidth': 0,
    'relief': 'flat'
}

# Control Button Sizes
BUTTON_SIZE_SMALL = 40  # Previous/Next
BUTTON_SIZE_LARGE = 50  # Play/Pause

# Border Radius (for rounded elements)
BORDER_RADIUS = 12

# Shadow/Glow Effects
SHADOW_OPACITY = 0.3
GLOW_INTENSITY = 0.15

