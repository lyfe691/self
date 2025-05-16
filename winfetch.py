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
import textwrap

# Initialize colorama
init()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="WinFetch - System info tool for Windows")
    parser.add_argument("--config", help="Path to custom config file")
    parser.add_argument("--setup", action="store_true", help="Run interactive setup to create config file")
    parser.add_argument("--height", type=int, help="Override height of the displayed image")
    parser.add_argument("--width", type=int, help="Override width of the displayed image")
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
        print(f"Warning: Encoding issue with ASCII art file: {art_path}")
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
    left_width = max(len(line) for line in left_content) if left_content else 0
    
    # Spacing between sections
    spacing = 4
    
    # Calculate max width for info text
    info_max_width = terminal_width - left_width - spacing - 5  # 5 chars of safety margin
    
    # Apply color to info text with proper wrapping
    info_list = []
    
    # Add username@hostname at the top of the info section
    info_list.append(f"{theme['title']}{user_host}{Style.RESET_ALL}")
    info_list.append(f"{theme['title']}{'-' * len(user_host)}{Style.RESET_ALL}")
    info_list.append("")  # Empty line after the title
    
    # Process system info with wrapping for long lines
    for key in config["info_display"]:
        if key in system_info:
            info_text = system_info[key]
            # Check if the line is too long and needs wrapping
            if len(info_text) > info_max_width:
                # Find the label part (typically before the colon)
                parts = info_text.split(':', 1)
                if len(parts) == 2:
                    label = parts[0] + ':'
                    content = parts[1]
                    # Apply coloring to label
                    colored_label = color_themes.apply_label_color(label, theme["label"])
                    # Wrap the content part
                    wrapped_content = textwrap.fill(content, width=info_max_width - len(label))
                    # Replace first line with label + first line of wrapped content
                    wrapped_lines = wrapped_content.split('\n')
                    first_line = colored_label + wrapped_lines[0]
                    info_list.append(first_line)
                    # Add remaining wrapped lines with proper indentation
                    for line in wrapped_lines[1:]:
                        info_list.append(' ' * (len(label) + 1) + line)
                else:
                    # No colon found, just wrap the whole text
                    wrapped = textwrap.fill(info_text, width=info_max_width)
                    for line in wrapped.split('\n'):
                        info_list.append(color_themes.apply_label_color(line, theme["label"]))
            else:
                # Line is short enough, no wrapping needed
                info_list.append(color_themes.apply_label_color(info_text, theme["label"]))
    
    # Clear screen
    print("\033[H\033[J", end="")
    
    # Add some padding
    print()
    
    # Get heights after processing
    left_height = len(left_content)
    info_height = len(info_list)
    
    # Prepare the combined display
    max_lines = max(left_height, info_height)
    
    # Create a two-column layout with fixed positions
    for i in range(max_lines):
        # Left column (ASCII art or image)
        if i < left_height:
            left_line = left_content[i]
        else:
            left_line = ""
            
        # Right column (system info)
        if i < info_height:
            info_line = info_list[i]
        else:
            info_line = ""
        
        # Print the line with fixed spacing
        if left_line:
            print(f"{left_line}", end="")
            # Calculate remaining space to the fixed info position
            current_pos = len(left_line)
            if current_pos < left_width + spacing:
                print(" " * (left_width + spacing - current_pos), end="")
        else:
            # No art on this line, just pad to the info position
            print(" " * (left_width + spacing), end="")
            
        # Print the info
        print(f"{info_line}")
    
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
    if args.width:
        config["image_width"] = args.width
    
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