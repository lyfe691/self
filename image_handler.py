"""
Image handling module for WinFetch
Supports displaying images in the terminal
"""

import os
import sys
from PIL import Image
import math
import shutil

# ANSI color codes
RESET = '\033[0m'

def get_terminal_size():
    """Get the dimensions of the terminal."""
    try:
        columns, lines = shutil.get_terminal_size()
        return columns, lines
    except:
        return 80, 24  # Default fallback size

def resize_image(image_path, target_height=20, target_width=None):
    """
    Resize an image to fit the terminal dimensions.
    Returns the PIL Image object.
    """
    try:
        img = Image.open(image_path)
        
        # Calculate aspect ratio
        width, height = img.size
        aspect_ratio = width / height
        
        if target_width is None:
            # Calculate width based on height and aspect ratio
            target_width = int(target_height * aspect_ratio * 0.5)  # * 0.5 to account for terminal character aspect ratio
        
        # Resize the image
        img = img.resize((target_width, target_height), Image.LANCZOS)
        return img
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def rgb_to_ansi(r, g, b, bg=False):
    """Convert RGB color to ANSI escape code."""
    if bg:
        return f'\033[48;2;{r};{g};{b}m'
    else:
        return f'\033[38;2;{r};{g};{b}m'

def image_to_ansi(image_path, height=20):
    """
    Convert an image to ANSI escape codes for terminal display.
    Returns a list of strings, each representing a line of the image.
    """
    terminal_width, terminal_height = get_terminal_size()
    img = resize_image(image_path, target_height=height, target_width=None)
    
    if img is None:
        return []
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    lines = []
    width, height = img.size
    pixels = img.load()
    
    for y in range(height):
        line = ""
        for x in range(width):
            r, g, b = pixels[x, y]
            line += f"{rgb_to_ansi(r, g, b, bg=True)}  {RESET}"
        lines.append(line)
    
    return lines

def get_images_dir():
    """Get the path to the images directory."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")

def list_available_images():
    """List all available images in the images directory."""
    images_dir = get_images_dir()
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        return []
    
    image_files = []
    for file in os.listdir(images_dir):
        lower_file = file.lower()
        if lower_file.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            image_files.append(file)
    
    return image_files

def get_image_path(image_name):
    """Get the full path for an image by name."""
    if not image_name:
        return None
        
    # If it's a full path, return it
    if os.path.isfile(image_name):
        return image_name
    
    # Check if it's in the images directory
    images_dir = get_images_dir()
    image_path = os.path.join(images_dir, image_name)
    if os.path.isfile(image_path):
        return image_path
    
    # Try adding extensions
    for ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
        test_path = os.path.join(images_dir, f"{image_name}{ext}")
        if os.path.isfile(test_path):
            return test_path
    
    return None 