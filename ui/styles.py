# styles.py
BACKGROUND_COLOR = "#121212"
TEXT_COLOR = "#FFFFFF"
HIGHLIGHT_COLOR = "#1DB954"
SECONDARY_COLOR = "#282828"
BUTTON_HOVER_COLOR = "#404040"
PROGRESS_BAR_COLOR = "#1DB954"
DISABLED_COLOR = "#A0A0A0"

FONT_FAMILY = "Segoe UI"  # More modern font
FONT_SIZE = 12
TITLE_FONT_SIZE = 14
BUTTON_FONT_SIZE = 16  # Larger size for playback control symbols

# Style configurations for ttk widgets
PROGRESS_BAR_STYLE = {
    'troughcolor': SECONDARY_COLOR,
    'background': PROGRESS_BAR_COLOR,
    'thickness': 6
}

# Button styles
BUTTON_STYLE = {
    'background': SECONDARY_COLOR,
    'foreground': TEXT_COLOR,
    'activebackground': BUTTON_HOVER_COLOR,
    'activeforeground': TEXT_COLOR,
    'borderwidth': 0,
    'relief': 'flat',
    'padx': 10,
    'pady': 5
}
