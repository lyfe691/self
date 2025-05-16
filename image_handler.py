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
    
    Parameters:
    - target_height: Target height in pixels
    - target_width: Target width in pixels (None = auto-calculate based on aspect ratio)
    """
    try:
        img = Image.open(image_path)
        
        # Calculate aspect ratio
        width, height = img.size
        aspect_ratio = width / height
        
        if target_width is None:
            # Terminal characters are typically taller than they are wide
            # Using a factor of 0.5 to account for character aspect ratio in terminals
            target_width = int(target_height * aspect_ratio * 0.5)
        
        # Resize the image with high quality
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

def image_to_ansi(image_path, height=20, width=None):
    """
    Convert an image to ANSI escape codes for terminal display.
    Returns a list of strings, each representing a line of the image.
    Uses half-block characters for higher resolution display.
    
    Parameters:
    - height: Target height in terminal rows
    - width: Target width in terminal columns (None = auto-calculate)
    """
    terminal_width, terminal_height = get_terminal_size()
    
    # Handle square image case explicitly (equal height and width)
    is_square = (width is not None and height == width)
    if is_square:
        # For a truly square appearance, we need to adjust for terminal character aspect ratio
        # Terminal characters are roughly twice as tall as wide
        width = width * 2
    
    # Calculate maximum width based on terminal size (leaving room for text)
    # Use approximately 40% of terminal width for the image if no width specified
    max_width = width if width is not None else int(terminal_width * 0.4)
    
    # Double the target height since we'll use half-blocks (2 pixels per character height)
    effective_height = height * 2
    
    # Resize the image
    img = resize_image(image_path, target_height=effective_height, target_width=width)
    
    if img is None:
        return []
    
    # Check if image width exceeds our calculated max width (only if width wasn't specified)
    img_width, img_height = img.size
    if width is None and img_width > max_width:
        # Recalculate the height to maintain aspect ratio
        aspect_ratio = img_width / img_height
        new_height = int(max_width / aspect_ratio)
        # Ensure new_height is even for the half-block rendering
        if new_height % 2 != 0:
            new_height += 1
        img = resize_image(image_path, target_height=new_height, target_width=max_width)
        img_width, img_height = img.size
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    lines = []
    pixels = img.load()
    
    # Use half-block characters for higher resolution
    # Process two rows at a time (upper and lower half of a character cell)
    for y in range(0, img_height, 2):
        line = ""
        for x in range(img_width):
            # Get upper pixel color
            r_upper, g_upper, b_upper = pixels[x, y]
            
            # Get lower pixel color (if within bounds)
            if y + 1 < img_height:
                r_lower, g_lower, b_lower = pixels[x, y + 1]
            else:
                # If at the edge, use the same color
                r_lower, g_lower, b_lower = r_upper, g_upper, b_upper
            
            # Upper half uses foreground color, lower half uses background color
            # Using '▀' character (upper half block)
            line += f"{rgb_to_ansi(r_upper, g_upper, b_upper)}{rgb_to_ansi(r_lower, g_lower, b_lower, bg=True)}▀{RESET}"
        
        lines.append(line)
    
    return lines

def sharpen_image(image_path):
    """Apply sharpening filter to improve image clarity."""
    try:
        from PIL import ImageEnhance, ImageFilter
        
        img = Image.open(image_path)
        # Apply a slight sharpening filter
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)  # Enhance sharpness by 1.5x
        
        # Also apply a slight contrast adjustment
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)  # Enhance contrast by 1.2x
        
        # Save to a temporary file
        temp_path = os.path.join(os.path.dirname(image_path), "temp_" + os.path.basename(image_path))
        img.save(temp_path)
        return temp_path
    except Exception as e:
        print(f"Warning: Could not enhance image: {e}")
        return image_path

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