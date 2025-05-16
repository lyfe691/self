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

# Initialize colorama
init()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="WinFetch - System info tool for Windows")
    parser.add_argument("--config", help="Path to custom config file")
    parser.add_argument("--ascii", help="Path to custom ASCII template")
    parser.add_argument("--theme", help="Color theme (default, powershell, windows, red, green, magenta, etc.)")
    parser.add_argument("--list-themes", action="store_true", help="List available color themes")
    parser.add_argument("--list-ascii", action="store_true", help="List available ASCII art templates")
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
            "ascii_art": "windows",
            "color": "blue",
            "info_display": ["os", "hostname", "kernel", "uptime", "packages", "shell", "resolution", "cpu", "memory", "disk"]
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

def display_winfetch(ascii_art, system_info, config):
    """Display the fetched information with ASCII art."""
    # Import our color theme module
    import color_themes
    
    # Get theme
    theme_name = config.get("theme", "default")
    theme = color_themes.get_theme(theme_name)
    
    # Add username@hostname as title
    import os
    import platform
    username = os.environ.get("USERNAME", "user")
    hostname = platform.node()
    title = f"{username}@{hostname}"
    
    # Print ASCII art and system info side by side
    art_lines = ascii_art.split('\n')
    
    # Apply color to info text
    info_list = []
    for key in config["info_display"]:
        if key in system_info:
            info_text = system_info[key]
            info_list.append(color_themes.apply_label_color(info_text, theme["label"]))
    
    # Combine art and info
    max_art_lines = len(art_lines)
    max_info_lines = len(info_list)
    max_lines = max(max_art_lines, max_info_lines)
    
    # Add padding
    print()
    
    # Print user@hostname
    padding = " " * 12  # Adjust based on your preference
    print(f"{padding}{theme['title']}{title}{Style.RESET_ALL}")
    print(f"{padding}{theme['title']}{'-' * len(title)}{Style.RESET_ALL}")
    print()
    
    # Print ASCII art and info
    for i in range(max_lines):
        art_line = art_lines[i] if i < max_art_lines else ""
        info_line = info_list[i] if i < max_info_lines else ""
        
        # Add spacing between art and info
        spacing = "    "
        
        print(f"{theme['ascii']}{art_line}{Style.RESET_ALL}{spacing}{info_line}")
    
    # Add color blocks at the bottom
    print()
    color_blocks = ""
    for color in [Fore.BLACK, Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]:
        color_blocks += f"{color}███{Style.RESET_ALL}"
    print(f"{padding}{color_blocks}")
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
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line args
    if args.ascii:
        config["ascii_art"] = args.ascii
    if args.theme:
        config["theme"] = args.theme
    
    # Load ASCII art and system info
    ascii_art = load_ascii_art(config["ascii_art"])
    system_info = get_system_info()
    
    # Display WinFetch
    display_winfetch(ascii_art, system_info, config)

if __name__ == "__main__":
    main() 