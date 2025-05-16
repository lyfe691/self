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
    parser.add_argument("--setup", action="store_true", help="Run interactive setup to create config file")
    parser.add_argument("--height", type=int, help="Override height of the displayed image")
    parser.add_argument("--version", action="store_true", help="Show version information")
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
            "image_height": 20,  # Default image height
            "info_display": [
                "os", "hostname", "kernel", "uptime", "packages", 
                "shell", "resolution", "wm", "theme", "terminal", 
                "font", "cpu", "gpu", "memory", "disk"
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

def display_winfetch(display_type, art_source, system_info, config):
    """Display the fetched information with ASCII art or image."""
    # Import modules
    import color_themes
    from image_handler import image_to_ansi, get_image_path, sharpen_image
    
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
    user_host = f"{username}@{hostname}"
    
    # Prepare left side content (ASCII art or image)
    left_content = []
    image_height = config.get("image_height", 20)
    
    if display_type == "image":
        image_path = get_image_path(art_source)
        if image_path:
            # Apply sharpening filter for better quality
            enhanced_path = sharpen_image(image_path)
            left_content = image_to_ansi(enhanced_path, height=image_height)
        else:
            # Fallback to ASCII if image not found
            left_content = load_ascii_art("windows").split('\n')
    else:
        # ASCII art
        left_content = art_source.split('\n')
    
    # Apply color to info text
    info_list = []
    
    # Add username@hostname at the top of the info section
    info_list.append(f"{theme['title']}{user_host}{Style.RESET_ALL}")
    info_list.append(f"{theme['title']}{'-' * len(user_host)}{Style.RESET_ALL}")
    info_list.append("")  # Empty line after the title
    
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
    
    # Clear screen
    print("\033[H\033[J", end="")
    
    # Calculate how many lines of content to display to ensure proper alignment
    max_content_lines = max(left_height, info_height)
    
    # Add some padding
    print()
    
    # Display content side by side
    for i in range(max_content_lines):
        left_line = left_content[i] if i < left_height else ""
        info_line = info_list[i] if i < info_height else ""
        
        print(f"{left_line}{' ' * spacing}{info_line}")
    
    # Add color blocks at the bottom
    print()
    color_blocks = create_color_blocks(theme)
    print(f"{' ' * 2}{color_blocks}")
    print()

def setup_wizard():
    """Interactive setup wizard to create/modify the config file."""
    from colorama import Fore, Style
    import image_handler
    import os
    
    print(f"{Fore.CYAN}WinFetch Setup Wizard{Style.RESET_ALL}")
    print("-----------------")
    print("This wizard will help you create a custom configuration for WinFetch.\n")
    
    # Default config
    config = load_config()
    
    # Display type
    print(f"{Fore.YELLOW}Display Type:{Style.RESET_ALL}")
    print("1. Image (recommended)")
    print("2. ASCII Art")
    choice = input("Choose [1/2] (default: 1): ").strip() or "1"
    config["display_type"] = "image" if choice == "1" else "ascii"
    print()
    
    # Image selection
    if config["display_type"] == "image":
        # List available images
        images = image_handler.list_available_images()
        if images:
            print(f"{Fore.YELLOW}Available Images:{Style.RESET_ALL}")
            for i, img in enumerate(images, 1):
                print(f"{i}. {img}")
            
            img_choice = input("Choose image number (or type a path/filename): ").strip()
            try:
                idx = int(img_choice) - 1
                if 0 <= idx < len(images):
                    config["image"] = images[idx]
                else:
                    config["image"] = img_choice
            except ValueError:
                config["image"] = img_choice
        else:
            print("No images found in images directory.")
            print("Please place images in the 'images' directory and run setup again.")
            config["image"] = "windows_logo.png"  # Default fallback
    else:
        # ASCII art selection
        ascii_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ascii")
        if os.path.exists(ascii_dir):
            ascii_files = [f.replace(".txt", "") for f in os.listdir(ascii_dir) if f.endswith(".txt")]
            
            print(f"{Fore.YELLOW}Available ASCII Art:{Style.RESET_ALL}")
            for i, art in enumerate(ascii_files, 1):
                print(f"{i}. {art}")
                
            art_choice = input("Choose ASCII art number (default: windows): ").strip()
            try:
                idx = int(art_choice) - 1
                if 0 <= idx < len(ascii_files):
                    config["ascii_art"] = ascii_files[idx]
            except ValueError:
                if art_choice:
                    config["ascii_art"] = art_choice
    print()
    
    # Theme selection
    import color_themes
    print(f"{Fore.YELLOW}Available Color Themes:{Style.RESET_ALL}")
    for i, theme in enumerate(color_themes.THEMES.keys(), 1):
        print(f"{i}. {theme}")
    
    theme_choice = input("Choose theme number (default: default): ").strip()
    theme_list = list(color_themes.THEMES.keys())
    try:
        idx = int(theme_choice) - 1
        if 0 <= idx < len(theme_list):
            config["theme"] = theme_list[idx]
    except ValueError:
        if theme_choice in color_themes.THEMES:
            config["theme"] = theme_choice
    print()
    
    # Image height
    if config["display_type"] == "image":
        print(f"{Fore.YELLOW}Image Height:{Style.RESET_ALL}")
        print("Recommended: 18-25 for best results")
        height_choice = input("Enter image height (default: 20): ").strip()
        try:
            config["image_height"] = int(height_choice)
        except:
            config["image_height"] = 20
    print()
    
    # Save configuration
    config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    config_path = os.path.join(config_dir, "config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    
    print(f"{Fore.GREEN}Configuration saved to {config_path}{Style.RESET_ALL}")
    print(f"Run WinFetch with 'python winfetch.py' to see your changes.\n")

def main():
    """Main function."""
    args = parse_args()
    
    # Handle version flag
    if args.version:
        print("WinFetch v1.0.0")
        return
    
    # Handle setup wizard
    if args.setup:
        setup_wizard()
        return
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line args if provided
    if args.height:
        config["image_height"] = args.height
    
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
        config=config
    )

if __name__ == "__main__":
    main() 