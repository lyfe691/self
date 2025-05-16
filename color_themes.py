"""
Color themes for WinFetch
"""

from colorama import Fore, Back, Style

# Basic color mapping
COLOR_MAP = {
    "black": Fore.BLACK,
    "blue": Fore.BLUE,
    "cyan": Fore.CYAN,
    "green": Fore.GREEN,
    "magenta": Fore.MAGENTA,
    "red": Fore.RED,
    "white": Fore.WHITE,
    "yellow": Fore.YELLOW,
    "lightblack": Fore.LIGHTBLACK_EX,
    "lightblue": Fore.LIGHTBLUE_EX,
    "lightcyan": Fore.LIGHTCYAN_EX,
    "lightgreen": Fore.LIGHTGREEN_EX,
    "lightmagenta": Fore.LIGHTMAGENTA_EX,
    "lightred": Fore.LIGHTRED_EX,
    "lightwhite": Fore.LIGHTWHITE_EX,
    "lightyellow": Fore.LIGHTYELLOW_EX
}

# Predefined themes
THEMES = {
    "default": {
        "title": Fore.BLUE,
        "ascii": Fore.BLUE,
        "text": Fore.RESET,
        "label": Fore.CYAN
    },
    "powershell": {
        "title": Fore.YELLOW,
        "ascii": Fore.BLUE,
        "text": Fore.RESET,
        "label": Fore.BLUE
    },
    "windows": {
        "title": Fore.CYAN,
        "ascii": Fore.CYAN,
        "text": Fore.RESET,
        "label": Fore.LIGHTCYAN_EX
    },
    "red": {
        "title": Fore.RED,
        "ascii": Fore.RED,
        "text": Fore.RESET,
        "label": Fore.LIGHTRED_EX
    },
    "green": {
        "title": Fore.GREEN,
        "ascii": Fore.GREEN,
        "text": Fore.RESET,
        "label": Fore.LIGHTGREEN_EX
    },
    "magenta": {
        "title": Fore.MAGENTA,
        "ascii": Fore.MAGENTA,
        "text": Fore.RESET,
        "label": Fore.LIGHTMAGENTA_EX
    }
}

def get_theme(theme_name="default"):
    """Get a color theme by name."""
    if theme_name in THEMES:
        return THEMES[theme_name]
    
    # If theme name is a color name, create a theme based on that color
    if theme_name.lower() in COLOR_MAP:
        color = COLOR_MAP[theme_name.lower()]
        return {
            "title": color,
            "ascii": color,
            "text": Fore.RESET,
            "label": color
        }
    
    # Default to the default theme
    return THEMES["default"]

def colorize(text, color_code):
    """Apply color to text."""
    return f"{color_code}{text}{Style.RESET_ALL}"

def apply_label_color(info_text, label_color):
    """Apply color to the label part of the info text (before the colon)."""
    if ': ' in info_text:
        label, value = info_text.split(': ', 1)
        return f"{label_color}{label}{Style.RESET_ALL}: {value}"
    return info_text 