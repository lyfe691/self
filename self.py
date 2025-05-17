#!/usr/bin/env python3
"""
self - windows neofetch

Author: Yanis Sebastian Zürcher
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

# Init colorama
init()

# cache system information with a timeout
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache", "sysinfo.json")
CACHE_TIMEOUT = 300 # 5 min

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="self - System info tool for Windows")
    parser.add_argument("--config", help="Path to custom config file")
    parser.add_argument("--setup", action="store_true", help="Run interactive setup to create config file")
    parser.add_argument("--height", type=int, help="Override height of the displayed image")
    parser.add_argument("--width", type=int, help="Override width of the displayed image")
    parser.add_argument("--version", action="store_true", help="Show version information")
    parser.add_argument("--no-cache", action="store_true", help="Bypass cache and gather fresh system info")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode with simplified output")
    parser.add_argument("--image", help="Use an image (specify name in images folder or path)")
    parser.add_argument("--ascii", help="Use ASCII art (specify name of ASCII art file)")
    parser.add_argument("--update", action="store_true", help="Update self to the latest version")
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
            "display_type": "image",  # image, braille, or ascii
            "render_mode": "block",   # block or braille (only used for image display type)
            "image": "rei.jpg",  # default image
            "ascii_art": "windows",  # default ascii art
            "theme": "blue",  # default theme
            "image_height": 20,  # default image height
            "image_width": None,  # default image width (none = auto calc based on aspect ratio)
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
        # fallback if sum goes wrong
        return """
        ################
        ##            ##
        ##  Windows   ##
        ##            ##
        ################
        """
    except UnicodeDecodeError:
        # fallback if encoding issues
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
    if use_cache and os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
                if time.time() - cache_data['timestamp'] < CACHE_TIMEOUT:
                    return cache_data['info']
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            pass
    
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
    # define colors to use
    colors = [
        (0, 0, 0),         # black
        (170, 0, 0),       # red
        (0, 170, 0),       # green
        (170, 85, 0),      # yellow
        (0, 0, 170),       # blue
        (170, 0, 170),     # magenta
        (0, 170, 170),     # cyan
        (170, 170, 170),   # white
        (85, 85, 85),      # bright black
        (255, 85, 85),     # bright red
        (85, 255, 85),     # bright green
        (255, 255, 85),    # bright yellow
        (85, 85, 255),     # bright blue
        (255, 85, 255),    # bright magenta
        (85, 255, 255),    # bright cyan
        (255, 255, 255)    # bright white
    ]
    
    # import rgb to ansi function
    from image_handler import rgb_to_ansi
    
    # create color blocks
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
        return 80  # default width

def display_self(display_type, art_source, system_info, config, execution_time=None):
    """Display the fetched information with ASCII art or image."""
    # import modules
    import color_themes
    from image_handler import image_to_ansi, get_image_path
    
    # get theme
    theme_name = config.get("theme", "default")
    theme = color_themes.get_theme(theme_name)
    
    # get terminal width for proper wrapping
    terminal_width = get_terminal_width()
    
    # add username@hostname as title
    import os
    import platform
    username = os.environ.get("USERNAME", "user")
    hostname = platform.node()
    user_host = f"{username}@{hostname}"
    
    # prepare left side content (ascii art or image)
    left_content = []
    image_height = config.get("image_height", 20)
    image_width = config.get("image_width", None)
    
    if display_type == "image" or display_type == "braille":
        image_path = get_image_path(art_source)
        if image_path:
            # Get the render mode
            render_mode = "braille" if display_type == "braille" else config.get("render_mode", "block")
            # render image with specified mode
            left_content = image_to_ansi(image_path, height=image_height, width=image_width, render_mode=render_mode)
        else:
            # fallback to ascii if image not found
            left_content = load_ascii_art("windows").split('\n')
    else:
        # ascii art
        left_content = art_source.split('\n')
    
    # determine dimensions
    left_width = max(len(strip_ansi(line)) for line in left_content) if left_content else 0
    
    # spacing between sections
    spacing = 2
    
    # clear screen
    print("\033[H\033[J", end="")
    
    # add padding at top
    print()
    
    # prepare system info text with colors
    info_lines = []
    
    # add username@hostname at the top, colored
    info_lines.append(f"{theme['title']}{user_host}{Style.RESET_ALL}")
    info_lines.append(f"{theme['title']}{'-' * len(user_host)}{Style.RESET_ALL}")
    info_lines.append("")  # empty line
    
    # format system info with proper coloring
    for key in config["info_display"]:
        if key in system_info:
            info_text = system_info[key]
            
            # format with proper coloring - assume format is "Label: Value"
            if ": " in info_text:
                label, value = info_text.split(": ", 1)
                # apply theme colors to label and value
                info_lines.append(f"{theme['label']}{label}:{Style.RESET_ALL} {value}")
            else:
                info_lines.append(color_themes.apply_label_color(info_text, theme["label"]))
    
    # add execution time if provided
    if execution_time is not None:
        info_lines.append("")
        info_lines.append(f"{theme['label']}Executed in{Style.RESET_ALL} {execution_time:.2f}s")
    
    # add empty line and color blocks at the end of info lines
    info_lines.append("")  # empty line
    color_blocks = create_color_blocks(theme)
    info_lines.append(color_blocks)
    
    # measure height of both columns
    left_height = len(left_content)
    info_height = len(info_lines)
    
    # calculate maximum height needed
    max_height = max(left_height, info_height)
    
    # print each line with the image on the left and info on the right
    for i in range(max_height):
        # determine what to print on the left side (image or ascii art)
        if i < left_height:
            left_line = left_content[i]
        else:
            left_line = ""
        
        # determine what to print on the right side (system info)
        if i < info_height:
            info_line = info_lines[i]
        else:
            info_line = ""
        
        # print the left content
        print(left_line, end="")
        
        # calculate spacing to position info text
        current_pos = len(strip_ansi(left_line))
        if current_pos < left_width:
            # add space to align with the width of the image/ascii art
            print(" " * (left_width - current_pos), end="")
        
        # add the minimal spacing between the image and text
        print(" " * spacing, end="")
        
        # print the info text
        print(info_line)
    
    # add final newline
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
    
    print(f"{Fore.CYAN}self Setup Wizard{Style.RESET_ALL}")
    print("-----------------")
    print("This wizard will help you create a custom configuration for self.\n")
    
    # Default config
    config = load_config()
    
    # Display type
    print(f"{Fore.YELLOW}Display Type:{Style.RESET_ALL}")
    print("1. Image with Blocks (half-blocks ▀)")
    print("2. Image with Braille (⠿)")
    print("3. ASCII Art")
    choice = input("Choose [1/2/3] (default: 1): ").strip() or "1"
    
    if choice == "1":
        config["display_type"] = "image"
        config["render_mode"] = "block"
    elif choice == "2":
        config["display_type"] = "braille"
        config["render_mode"] = "braille"
    else:
        config["display_type"] = "ascii"
    print()
    
    # Image selection (for both block and braille display types)
    if config["display_type"] == "image" or config["display_type"] == "braille":
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
    if config["display_type"] == "image" or config["display_type"] == "braille":
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
    
    # save configuration
    config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    config_path = os.path.join(config_dir, "config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    
    print(f"{Fore.GREEN}Configuration saved to {config_path}{Style.RESET_ALL}")
    print(f"Run self with 'self' or if dev 'python self.py' to see your changes.\n")

def update_self():
    """Update self to the latest version."""
    import subprocess
    import shutil
    import tempfile
    import os
    from colorama import Fore, Style
    
    print(f"{Fore.CYAN}Updating self...{Style.RESET_ALL}")
    
    # create a temporary directory for the update
    with tempfile.TemporaryDirectory() as temp_dir:
        # clone the latest version from GitHub
        try:
            print("Fetching the latest version...")
            clone_cmd = f"git clone https://github.com/lyfe691/self.git {temp_dir}"
            
            # use subprocess.run to execute the command
            try:
                subprocess.run(clone_cmd, shell=True, check=True, capture_output=True)
            except subprocess.CalledProcessError:
                print(f"{Fore.RED}Error: Failed to fetch the latest version.{Style.RESET_ALL}")
                print("Please make sure you have Git installed and you're connected to the internet.")
                return False
            
            # get the current installation directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # copy the updated files, preserving user config
            print("updating files...")
            
            # preserve user config
            config_dir = os.path.join(current_dir, "config")
            cache_dir = os.path.join(current_dir, "cache")
            images_dir = os.path.join(current_dir, "images")

            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                dest_path = os.path.join(current_dir, item)
                
                # skip config and cache directories to preserve user settings
                if (item == "config" or item == "cache" or item == "images") and os.path.isdir(item_path):
                    continue
                
                # remove existing file/directory before copying
                if os.path.exists(dest_path):
                    if os.path.isdir(dest_path):
                        shutil.rmtree(dest_path)
                    else:
                        os.remove(dest_path)
                
                # copy file or directory
                if os.path.isdir(item_path):
                    shutil.copytree(item_path, dest_path)
                else:
                    shutil.copy2(item_path, dest_path)
            
            print(f"{Fore.GREEN}Update completed successfully!{Style.RESET_ALL}")
            print("Run 'self' to use the updated version.")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}Error during update: {e}{Style.RESET_ALL}")
            print("Please try again later or download the latest version manually.")
            return False

def main():
    """Main function."""
    args = parse_args()
    
    if args.version:
        print("self v1.0.0")
        return
    
    if args.setup:
        setup_wizard()
        return
    
    if args.update:
        update_self()
        return
        
    # use the debug flag from args
    debug_mode = args.debug
    
    config = load_config(args.config)
    
    if args.height:
        config["image_height"] = args.height
    if args.width:
        config["image_width"] = args.width
    
    # for debugging, force ascii art mode as it's simpler
    if debug_mode:
        display_type = "ascii"
        art_source = load_ascii_art("windows")
        system_info = get_system_info(not args.no_cache)
        execution_time = 0.0
        
        # simple debug display
        print("=" * 40)
        print("self DEBUG MODE")
        print("=" * 40)
        
        # print system info directly
        for key in config["info_display"]:
            if key in system_info:
                print(system_info[key])
        
        print("\nASCII Art:")
        print(art_source)
        return
        
    # delete the old cache file if it exists to refresh gpu info
    if os.path.exists(CACHE_FILE) and not args.no_cache:
        try:
            with open(CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
                if 'info' in cache_data and 'gpu' in cache_data['info']:
                    gpu_info = cache_data['info']['gpu']
                    if 'Unknown' in gpu_info:
                        # if gpu is unknown, invalidate the cache
                        os.remove(CACHE_FILE)
        except:
            # if there's any error reading the cache, just delete it
            try:
                os.remove(CACHE_FILE)
            except:
                pass
    
    # restore users display type preference from config
    display_type = config.get("display_type", "ascii")
    
    # override display type if specified in arguments
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
    
    display_self(
        display_type=display_type,
        art_source=art_source,
        system_info=system_info,
        config=config,
        execution_time=execution_time
    )

if __name__ == "__main__":
    main() 