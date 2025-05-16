#!/usr/bin/env python3
"""
winfetch - customizable system information tool for windows
"""

import os
import sys
import json
import platform
import argparse
import time
from colorama import init, Fore, Style
import shutil
import textwrap

# Initialize colorama
init()

# cache system information with a timeout
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache", "sysinfo.json")
CACHE_TIMEOUT = 300  # 5 minutes

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="WinFetch - System info tool for Windows")
    parser.add_argument("--config", help="Path to custom config file")
    parser.add_argument("--setup", action="store_true", help="Run interactive setup to create config file")
    parser.add_argument("--height", type=int, help="Override height of the displayed image")
    parser.add_argument("--width", type=int, help="Override width of the displayed image")
    parser.add_argument("--version", action="store_true", help="Show version information")
    parser.add_argument("--no-cache", action="store_true", help="Bypass cache and gather fresh system info")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode with simplified output")
    parser.add_argument("--image", help="Use an image (specify name in images folder or path)")
    parser.add_argument("--ascii", help="Use ASCII art (specify name of ASCII art file)")
    return parser.parse_args()

def load_config(config_path=None):
    """Load configuration from file."""
    default_config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "config.json")
    config_path = config_path or default_config
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"config file not found: {config_path}")
        print("using default configuration.")
        return {
            "display_type": "image",  # "image" or "ascii"
            "image": "rei.jpg",  # Default image
            "ascii_art": "windows",  # Default ASCII art
            "theme": "blue",  # Default theme
            "image_height": 20,  # Default image height
            "image_width": None,  # Default image width (None = auto-calculate based on aspect ratio)
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
        with open(art_path, 'r', encoding='utf-8') as f:
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
    except UnicodeDecodeError:
        # Fallback if we have encoding issues
        print(f"warning: encoding issue with ascii art file: {art_path}")
        return """
        ################
        ##            ##
        ##  Windows   ##
        ##            ##
        ################
        """

def get_system_info(use_cache=True):
    """Collect system information."""
    # check if cache exists and is fresh
    if use_cache and os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
                # check if cache is still valid
                if time.time() - cache_data['timestamp'] < CACHE_TIMEOUT:
                    return cache_data['info']
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            pass  # if any error, just regenerate
    
    # get fresh information
    import win_sysinfo
    info = win_sysinfo.get_all_info()
    
    # save to cache
    if use_cache:
        cache_dir = os.path.dirname(CACHE_FILE)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        with open(CACHE_FILE, 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'info': info
            }, f)
    
    return info

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

def display_winfetch(display_type, art_source, system_info, config, execution_time=None):
    """Display the fetched information with ASCII art or image."""
    # Import modules
    import color_themes
    from image_handler import image_to_ansi, get_image_path
    
    # Get theme
    theme_name = config.get("theme", "default")
    theme = color_themes.get_theme(theme_name)
    
    # Get terminal width for proper wrapping
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
    image_width = config.get("image_width", None)
    
    if display_type == "image":
        image_path = get_image_path(art_source)
        if image_path:
            # Render image directly without sharpening
            left_content = image_to_ansi(image_path, height=image_height, width=image_width)
        else:
            # Fallback to ASCII if image not found
            left_content = load_ascii_art("windows").split('\n')
    else:
        # ASCII art
        left_content = art_source.split('\n')
    
    # Determine dimensions
    left_width = max(len(strip_ansi(line)) for line in left_content) if left_content else 0
    
    # Spacing between sections
    spacing = 2
    
    # Clear screen
    print("\033[H\033[J", end="")
    
    # Add padding at top
    print()
    
    # Prepare system info text with colors
    info_lines = []
    
    # Add username@hostname at the top, colored
    info_lines.append(f"{theme['title']}{user_host}{Style.RESET_ALL}")
    info_lines.append(f"{theme['title']}{'-' * len(user_host)}{Style.RESET_ALL}")
    info_lines.append("")  # Empty line
    
    # Format system info with proper coloring
    for key in config["info_display"]:
        if key in system_info:
            info_text = system_info[key]
            
            # Format with proper coloring - assume format is "Label: Value"
            if ": " in info_text:
                label, value = info_text.split(": ", 1)
                # Apply theme colors to label and value
                info_lines.append(f"{theme['label']}{label}:{Style.RESET_ALL} {value}")
            else:
                info_lines.append(color_themes.apply_label_color(info_text, theme["label"]))
    
    # Add execution time if provided
    if execution_time is not None:
        info_lines.append("")
        info_lines.append(f"{theme['label']}Time:{Style.RESET_ALL} {execution_time:.2f}s")
    
    # Measure height of both columns
    left_height = len(left_content)
    info_height = len(info_lines)
    
    # Calculate maximum height needed
    max_height = max(left_height, info_height)
    
    # Print each line with the image on the left and info on the right
    for i in range(max_height):
        # Determine what to print on the left side (image or ASCII art)
        if i < left_height:
            left_line = left_content[i]
        else:
            left_line = ""
        
        # Determine what to print on the right side (system info)
        if i < info_height:
            info_line = info_lines[i]
        else:
            info_line = ""
        
        # Print the left content
        print(left_line, end="")
        
        # Calculate spacing to position info text
        current_pos = len(strip_ansi(left_line))
        if current_pos < left_width:
            # Add space to align with the width of the image/ASCII art
            print(" " * (left_width - current_pos), end="")
        
        # Add the minimal spacing between the image and text
        print(" " * spacing, end="")
        
        # Print the info text
        print(info_line)
    
    # Add color blocks at the bottom
    print()
    color_blocks = create_color_blocks(theme)
    print(f"{' ' * 2}{color_blocks}")
    print()

def strip_ansi(text):
    """Remove ANSI escape sequences for length calculation"""
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

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
            config["image"] = "rei.jpg"  # Default fallback
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
            
        print(f"\n{Fore.YELLOW}Image Width:{Style.RESET_ALL}")
        print("Enter a width value or leave empty for auto-calculation based on aspect ratio")
        print("Recommended: leave empty or 30-60 for best results")
        width_choice = input("Enter image width (default: auto): ").strip()
        if width_choice:
            try:
                config["image_width"] = int(width_choice)
            except:
                config["image_width"] = None
        else:
            config["image_width"] = None
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
    
    if args.version:
        print("WinFetch v1.0.0")
        return
    
    if args.setup:
        setup_wizard()
        return
    
    # Use the debug flag from args
    debug_mode = args.debug
    
    config = load_config(args.config)
    
    if args.height:
        config["image_height"] = args.height
    if args.width:
        config["image_width"] = args.width
    
    # For debugging, we can force ASCII art mode as it's simpler
    if debug_mode:
        display_type = "ascii"
        art_source = load_ascii_art("windows")
        system_info = get_system_info(not args.no_cache)
        execution_time = 0.0
        
        # Simple debug display
        print("=" * 40)
        print("WINFETCH DEBUG MODE")
        print("=" * 40)
        
        # Print system info directly
        for key in config["info_display"]:
            if key in system_info:
                print(system_info[key])
        
        print("\nASCII Art:")
        print(art_source)
        return
        
    # Delete the old cache file if it exists to refresh GPU info
    if os.path.exists(CACHE_FILE) and not args.no_cache:
        try:
            with open(CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
                if 'info' in cache_data and 'gpu' in cache_data['info']:
                    gpu_info = cache_data['info']['gpu']
                    if 'Unknown' in gpu_info:
                        # If GPU is unknown, invalidate the cache
                        os.remove(CACHE_FILE)
        except:
            # If there's any error reading the cache, just delete it
            try:
                os.remove(CACHE_FILE)
            except:
                pass
    
    # Restore user's display type preference from config
    display_type = config.get("display_type", "ascii")
    
    # Override display type if specified in arguments
    if args.image:
        display_type = "image"
        config["image"] = args.image
    elif args.ascii:
        display_type = "ascii"
        config["ascii_art"] = args.ascii
    
    # measure performance
    start_time = time.time()
    
    if display_type == "ascii":
        art_source = load_ascii_art(config["ascii_art"])
    else:
        art_source = config.get("image", "")
    
    system_info = get_system_info(not args.no_cache)
    
    # calculate execution time
    execution_time = time.time() - start_time
    
    display_winfetch(
        display_type=display_type,
        art_source=art_source,
        system_info=system_info,
        config=config,
        execution_time=execution_time
    )

if __name__ == "__main__":
    main() 