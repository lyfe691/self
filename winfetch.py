#!/usr/bin/env python3
"""
WinFetch - A customizable system information tool for Windows
"""

import os
import sys
import json
import platform
import argparse
from colorama import init, Fore, Style
import shutil

# Initialize colorama
init()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="WinFetch - System info tool for Windows")
    parser.add_argument("--config", help="Path to custom config file")
    parser.add_argument("--ascii", help="Path to custom ASCII template")
    parser.add_argument("--image", help="Path to image or name of image in the images directory")
    parser.add_argument("--theme", help="Color theme (default, powershell, windows, red, green, magenta, etc.)")
    parser.add_argument("--list-themes", action="store_true", help="List available color themes")
    parser.add_argument("--list-ascii", action="store_true", help="List available ASCII art templates")
    parser.add_argument("--list-images", action="store_true", help="List available images")
    parser.add_argument("--height", type=int, default=20, help="Height of the displayed image (default: 20 lines)")
    return parser.parse_args()

def load_config(config_path=None):
    """Load configuration from file."""
    default_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "config.json")
    config_path = config_path or default_config
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        print("Using default configuration.")
        return {
            "display_type": "image",  # "image" or "ascii"
            "image": "windows_logo.png",  # Default image
            "ascii_art": "windows",  # Default ASCII art
            "theme": "blue",  # Default theme
            "info_display": [
                "os", "hostname", "kernel", "uptime", "packages", 
                "shell", "resolution", "wm", "theme", "cpu", "memory", "disk"
            ]
        }

def load_ascii_art(art_name):
    """Load ASCII art template."""
    art_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ascii", f"{art_name}.txt")
    try:
        with open(art_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to a simple ASCII art
        return """
        ################
        ##            ##
        ##  Windows   ##
        ##            ##
        ################
        """

def get_system_info():
    """Collect system information."""
    # Use our specialized module for better Windows-specific info
    import win_sysinfo
    return win_sysinfo.get_all_info()

def create_color_blocks(theme):
    """Create terminal color blocks for display."""
    # Define colors to use
    colors = [
        (0, 0, 0),         # Black
        (170, 0, 0),       # Red
        (0, 170, 0),       # Green
        (170, 85, 0),      # Yellow
        (0, 0, 170),       # Blue
        (170, 0, 170),     # Magenta
        (0, 170, 170),     # Cyan
        (170, 170, 170),   # White
        (85, 85, 85),      # Bright Black
        (255, 85, 85),     # Bright Red
        (85, 255, 85),     # Bright Green
        (255, 255, 85),    # Bright Yellow
        (85, 85, 255),     # Bright Blue
        (255, 85, 255),    # Bright Magenta
        (85, 255, 255),    # Bright Cyan
        (255, 255, 255)    # Bright White
    ]
    
    # Import RGB to ANSI function
    from image_handler import rgb_to_ansi
    
    # Create color blocks
    blocks = ""
    for r, g, b in colors:
        blocks += f"{rgb_to_ansi(r, g, b, bg=True)}   {Style.RESET_ALL}"
    
    return blocks

def get_terminal_width():
    """Get the width of the terminal."""
    try:
        columns, _ = shutil.get_terminal_size()
        return columns
    except:
        return 80  # Default width

def display_winfetch(display_type, art_source, system_info, config, image_height=20):
    """Display the fetched information with ASCII art or image."""
    # Import modules
    import color_themes
    from image_handler import image_to_ansi, get_image_path
    
    # Get theme
    theme_name = config.get("theme", "default")
    theme = color_themes.get_theme(theme_name)
    
    # Get terminal width
    terminal_width = get_terminal_width()
    
    # Add username@hostname as title
    import os
    import platform
    username = os.environ.get("USERNAME", "user")
    hostname = platform.node()
    title = f"{username}@{hostname}"
    
    # Prepare left side content (ASCII art or image)
    left_content = []
    if display_type == "image":
        image_path = get_image_path(art_source)
        if image_path:
            left_content = image_to_ansi(image_path, height=image_height)
        else:
            # Fallback to ASCII if image not found
            left_content = load_ascii_art("windows").split('\n')
    else:
        # ASCII art
        left_content = art_source.split('\n')
    
    # Apply color to info text
    info_list = []
    for key in config["info_display"]:
        if key in system_info:
            info_text = system_info[key]
            info_list.append(color_themes.apply_label_color(info_text, theme["label"]))
    
    # Determine dimensions
    left_width = max(len(line) for line in left_content) if left_content else 0
    left_height = len(left_content)
    info_height = len(info_list)
    
    # Spacing between sections
    spacing = 4
    
    # Clear screen and reset cursor
    print("\033[H\033[J", end="")
    
    # Print the title at the top
    title_padding = " " * 2
    print()
    print(f"{title_padding}{theme['title']}{title}{Style.RESET_ALL}")
    print(f"{title_padding}{theme['title']}{'-' * len(title)}{Style.RESET_ALL}")
    print()
    
    # Calculate how many lines of content to display to ensure proper alignment
    max_content_lines = max(left_height, info_height)
    
    # Display content side by side
    for i in range(max_content_lines):
        left_line = left_content[i] if i < left_height else ""
        info_line = info_list[i] if i < info_height else ""
        
        print(f"{left_line}{' ' * spacing}{info_line}")
    
    # Add color blocks at the bottom
    print()
    color_blocks = create_color_blocks(theme)
    print(f"{title_padding}{color_blocks}")
    print()

def list_ascii_templates():
    """List available ASCII art templates."""
    import os
    ascii_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ascii")
    if os.path.exists(ascii_dir):
        templates = [f.replace(".txt", "") for f in os.listdir(ascii_dir) if f.endswith(".txt")]
        print("Available ASCII templates:")
        for template in templates:
            print(f"  - {template}")
    else:
        print("ASCII template directory not found.")

def list_color_themes():
    """List available color themes."""
    import color_themes
    print("Available color themes:")
    for theme in color_themes.THEMES:
        print(f"  - {theme}")
    print("\nAdditionally, you can use any of these basic colors:")
    for color in sorted(color_themes.COLOR_MAP.keys()):
        print(f"  - {color}")

def list_images():
    """List available images."""
    from image_handler import list_available_images
    images = list_available_images()
    
    if not images:
        print("No images found in the images directory.")
        print(f"Place image files in the '{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')}' directory.")
        return
    
    print("Available images:")
    for image in images:
        print(f"  - {image}")

def main():
    """Main function."""
    args = parse_args()
    
    # Handle special commands
    if args.list_themes:
        list_color_themes()
        return
    
    if args.list_ascii:
        list_ascii_templates()
        return
    
    if args.list_images:
        list_images()
        return
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line args
    if args.ascii:
        config["display_type"] = "ascii"
        config["ascii_art"] = args.ascii
    
    if args.image:
        config["display_type"] = "image"
        config["image"] = args.image
    
    if args.theme:
        config["theme"] = args.theme
    
    # Load display content (ASCII art or image path)
    display_type = config.get("display_type", "ascii")
    
    if display_type == "ascii":
        art_source = load_ascii_art(config["ascii_art"])
    else:
        art_source = config.get("image", "")
    
    # Get system info
    system_info = get_system_info()
    
    # Display WinFetch
    display_winfetch(
        display_type=display_type,
        art_source=art_source,
        system_info=system_info,
        config=config,
        image_height=args.height
    )

if __name__ == "__main__":
    main() 