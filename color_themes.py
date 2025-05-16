"""
color themes for self
"""

from colorama import Fore, Back, Style

# cache for color formatted strings
_color_cache = {}

# basic color mapping
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

# predefined themes
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

# precompute theme lookups
_theme_cache = {}

def get_theme(theme_name="default"):
    global _theme_cache
    
    # check if theme is already cached
    if theme_name in _theme_cache:
        return _theme_cache[theme_name]
    
    if theme_name in THEMES:
        result = THEMES[theme_name]
    elif theme_name.lower() in COLOR_MAP:
        color = COLOR_MAP[theme_name.lower()]
        result = {
            "title": color,
            "ascii": color,
            "text": Fore.RESET,
            "label": color
        }
    else:
        result = THEMES["default"]
    
    # cache the result
    _theme_cache[theme_name] = result
    return result

def colorize(text, color_code):
    # check if this text/color combo is cached
    cache_key = f"{text}::{color_code}"
    if cache_key in _color_cache:
        return _color_cache[cache_key]
    
    result = f"{color_code}{text}{Style.RESET_ALL}"
    _color_cache[cache_key] = result
    return result

def apply_label_color(info_text, label_color):
    # check if this text / color is cached
    cache_key = f"{info_text}::{label_color}"
    if cache_key in _color_cache:
        return _color_cache[cache_key]
    
    if ': ' in info_text:
        label, value = info_text.split(': ', 1)
        result = f"{label_color}{label}{Style.RESET_ALL}: {value}"
    else:
        result = info_text
    
    _color_cache[cache_key] = result
    return result 