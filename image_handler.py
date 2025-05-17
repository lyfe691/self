"""
image handling module for self
"""

import os
import sys
from PIL import Image
import math
import shutil
import hashlib
import time

# try to import numpy for faster image processing
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

RESET = '\033[0m'
IMAGE_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache", "images")
IMAGE_CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours

def get_terminal_size():
    try:
        columns, lines = shutil.get_terminal_size()
        return columns, lines
    except:
        return 80, 24

def resize_image(image_path, target_height=20, target_width=None):
    try:
        img = Image.open(image_path)
        
        width, height = img.size
        aspect_ratio = width / height
        
        if target_width is None:
            # factor of 0.5 for terminal character aspect ratio
            target_width = int(target_height * aspect_ratio * 0.5)
        
        # use NEAREST for faster resizing when quality isn't critical
        img = img.resize((target_width, target_height), Image.NEAREST)
        return img
    except Exception as e:
        print(f"error processing image: {e}")
        return None

def rgb_to_ansi(r, g, b, bg=False):
    if bg:
        return f'\033[48;2;{r};{g};{b}m'
    else:
        return f'\033[38;2;{r};{g};{b}m'

def _get_cached_image_path(image_path, height, width, render_mode="block"):
    """get path to a cached rendered image if it exists and is valid"""
    if not os.path.exists(IMAGE_CACHE_DIR):
        os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)
        
    # generate a unique identifier for this image and settings
    img_stat = os.stat(image_path)
    cache_key = f"{image_path}_{img_stat.st_mtime}_{height}_{width}_{render_mode}"
    cache_hash = hashlib.md5(cache_key.encode()).hexdigest()
    cache_path = os.path.join(IMAGE_CACHE_DIR, f"{cache_hash}.txt")
    
    # check if cache exists and is valid
    if os.path.exists(cache_path):
        # check if cache is too old
        cache_stat = os.stat(cache_path)
        if time.time() - cache_stat.st_mtime < IMAGE_CACHE_TIMEOUT:
            return cache_path
    
    return None

def _save_image_cache(image_path, height, width, rendered_lines, render_mode="block"):
    """save rendered image to cache"""
    if not os.path.exists(IMAGE_CACHE_DIR):
        os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)
        
    # generate a unique identifier for this image and settings
    img_stat = os.stat(image_path)
    cache_key = f"{image_path}_{img_stat.st_mtime}_{height}_{width}_{render_mode}"
    cache_hash = hashlib.md5(cache_key.encode()).hexdigest()
    cache_path = os.path.join(IMAGE_CACHE_DIR, f"{cache_hash}.txt")
    
    # save the rendered image
    with open(cache_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(rendered_lines))
    
    return cache_path

def pixel_to_braille(pixels):
    """Convert a 2x4 pixel grid to a braille character
    
    Braille dots are arranged as:
    0 3
    1 4
    2 5
    6 7
    
    Where 0-7 are bit positions.
    """
    # The base braille character (⠀) is U+2800 (empty braille)
    # Each raised dot adds a specific value to this base
    
    # Initialize with empty braille
    value = 0
    
    # Each bit position corresponds to a specific power of 2
    bit_values = [1, 2, 4, 8, 16, 32, 64, 128]
    
    # Check each pixel in the grid and set the corresponding bit if the pixel is "on"
    threshold = 127  # Threshold for considering a pixel "on"
    
    # Map pixel positions to bit positions in braille
    # [0, 0] -> 0, [1, 0] -> 3, [0, 1] -> 1, [1, 1] -> 4, etc.
    pixel_to_bit_map = [
        [(0, 0), (0, 1), (0, 2), (0, 3)],  # Left column
        [(1, 0), (1, 1), (1, 2), (1, 3)]   # Right column
    ]
    
    # Map (col, row) to bit position
    bit_position_map = {
        (0, 0): 0, (1, 0): 3,
        (0, 1): 1, (1, 1): 4,
        (0, 2): 2, (1, 2): 5,
        (0, 3): 6, (1, 3): 7
    }
    
    # Set bits based on pixel intensity
    for col in range(2):
        for row in range(4):
            x, y = pixel_to_bit_map[col][row]
            if x < len(pixels[0]) and y < len(pixels):  # Ensure we're within bounds
                if pixels[y][x] < threshold:  # If the pixel is "on" (darker than threshold)
                    bit_pos = bit_position_map[(col, row)]
                    value |= bit_values[bit_pos]
    
    # Convert to braille character
    return chr(0x2800 + value)

def image_to_ansi_block(image_path, height=20, width=None):
    """Render image using block characters (original method)"""
    # try to use cached rendered image if available
    cache_path = _get_cached_image_path(image_path, height, width, "block")
    if cache_path:
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read().splitlines()
        except:
            pass  # if any error reading cache, proceed to regenerate
    
    terminal_width, terminal_height = get_terminal_size()
    
    is_square = (width is not None and height == width)
    if is_square:
        width = width * 2
    
    max_width = width if width is not None else int(terminal_width * 0.4)
    
    # double height for half-blocks (2 pixels per character)
    effective_height = height * 2
    
    img = resize_image(image_path, target_height=effective_height, target_width=width)
    
    if img is None:
        return []
    
    img_width, img_height = img.size
    if width is None and img_width > max_width:
        aspect_ratio = img_width / img_height
        new_height = int(max_width / aspect_ratio)
        if new_height % 2 != 0:
            new_height += 1
        img = resize_image(image_path, target_height=new_height, target_width=max_width)
        img_width, img_height = img.size
    
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    lines = []
    
    # faster processing using numpy if available
    if HAS_NUMPY:
        # convert to numpy array for faster processing
        pixels = np.array(img)
        
        # process two rows at a time using half-block characters
        for y in range(0, img_height, 2):
            line = ""
            for x in range(img_width):
                # get upper pixel color
                if y < img_height:
                    r_upper, g_upper, b_upper = pixels[y, x]
                else:
                    r_upper, g_upper, b_upper = 0, 0, 0
                
                # get lower pixel color
                if y + 1 < img_height:
                    r_lower, g_lower, b_lower = pixels[y + 1, x]
                else:
                    r_lower, g_lower, b_lower = r_upper, g_upper, b_upper
                
                # '▀' character (upper half block)
                line += f"{rgb_to_ansi(r_upper, g_upper, b_upper)}{rgb_to_ansi(r_lower, g_lower, b_lower, bg=True)}▀{RESET}"
            
            lines.append(line)
    else:
        # fallback to slower PIL method
        pixels = img.load()
        
        # process two rows at a time using half-block characters
        for y in range(0, img_height, 2):
            line = ""
            for x in range(img_width):
                r_upper, g_upper, b_upper = pixels[x, y]
                
                if y + 1 < img_height:
                    r_lower, g_lower, b_lower = pixels[x, y + 1]
                else:
                    r_lower, g_lower, b_lower = r_upper, g_upper, b_upper
                
                # '▀' character (upper half block)
                line += f"{rgb_to_ansi(r_upper, g_upper, b_upper)}{rgb_to_ansi(r_lower, g_lower, b_lower, bg=True)}▀{RESET}"
            
            lines.append(line)
    
    # save to cache for future use
    _save_image_cache(image_path, height, width, lines, "block")
    
    return lines

def image_to_ansi_braille(image_path, height=20, width=None):
    """Render image using braille characters"""
    # try to use cached rendered image if available
    cache_path = _get_cached_image_path(image_path, height, width, "braille")
    if cache_path:
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read().splitlines()
        except:
            pass  # if any error reading cache, proceed to regenerate
    
    terminal_width, terminal_height = get_terminal_size()
    
    # Adjust width for braille characters (each is 2×4 pixels)
    is_square = (width is not None and height == width)
    if is_square:
        width = width * 2
    
    max_width = width if width is not None else int(terminal_width * 0.4)
    
    # For braille, each character represents a 2×4 grid of pixels
    # Adjust height and width accordingly
    effective_height = height * 4
    effective_width = width * 2 if width is not None else None
    
    img = resize_image(image_path, target_height=effective_height, target_width=effective_width)
    
    if img is None:
        return []
    
    img_width, img_height = img.size
    if width is None and img_width > max_width * 2:  # Each braille char is 2 pixels wide
        aspect_ratio = img_width / img_height
        new_height = int((max_width * 2) / aspect_ratio)
        if new_height % 4 != 0:
            new_height += (4 - (new_height % 4))  # Ensure height is multiple of 4
        img = resize_image(image_path, target_height=new_height, target_width=max_width * 2)
        img_width, img_height = img.size
    
    # Convert to grayscale for braille mapping
    img_gray = img.convert('L')
    # Keep color image for coloring
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    lines = []
    
    # Process in 2×4 pixel blocks (the size of a braille character)
    if HAS_NUMPY:
        # Convert to numpy arrays for faster processing
        gray_pixels = np.array(img_gray)
        color_pixels = np.array(img)
        
        for y in range(0, img_height, 4):
            line = ""
            for x in range(0, img_width, 2):
                # Extract a 2×4 block of pixels for braille mapping
                block = []
                for by in range(4):
                    row = []
                    for bx in range(2):
                        py, px = y + by, x + bx
                        if py < img_height and px < img_width:
                            row.append(gray_pixels[py, px])
                        else:
                            row.append(255)  # White (empty) for out-of-bounds
                    block.append(row)
                
                # Get average color for the block
                r_sum, g_sum, b_sum = 0, 0, 0
                count = 0
                for by in range(min(4, img_height - y)):
                    for bx in range(min(2, img_width - x)):
                        r, g, b = color_pixels[y + by, x + bx]
                        r_sum += r
                        g_sum += g
                        b_sum += b
                        count += 1
                
                if count > 0:
                    r_avg = r_sum // count
                    g_avg = g_sum // count
                    b_avg = b_sum // count
                else:
                    r_avg, g_avg, b_avg = 255, 255, 255  # White for empty blocks
                
                # Generate braille character
                braille_char = pixel_to_braille(block)
                
                # Add colored braille character to the line
                line += f"{rgb_to_ansi(r_avg, g_avg, b_avg)}{braille_char}{RESET}"
            
            if line:  # Only add non-empty lines
                lines.append(line)
    else:
        # Fallback using PIL
        gray_pixels = img_gray.load()
        color_pixels = img.load()
        
        for y in range(0, img_height, 4):
            line = ""
            for x in range(0, img_width, 2):
                # Extract a 2×4 block of pixels for braille mapping
                block = []
                for by in range(4):
                    row = []
                    for bx in range(2):
                        py, px = y + by, x + bx
                        if py < img_height and px < img_width:
                            row.append(gray_pixels[px, py])
                        else:
                            row.append(255)  # White (empty) for out-of-bounds
                    block.append(row)
                
                # Get average color for the block
                r_sum, g_sum, b_sum = 0, 0, 0
                count = 0
                for by in range(min(4, img_height - y)):
                    for bx in range(min(2, img_width - x)):
                        if y + by < img_height and x + bx < img_width:
                            r, g, b = color_pixels[x + bx, y + by]
                            r_sum += r
                            g_sum += g
                            b_sum += b
                            count += 1
                
                if count > 0:
                    r_avg = r_sum // count
                    g_avg = g_sum // count
                    b_avg = b_sum // count
                else:
                    r_avg, g_avg, b_avg = 255, 255, 255  # White for empty blocks
                
                # Generate braille character
                braille_char = pixel_to_braille(block)
                
                # Add colored braille character to the line
                line += f"{rgb_to_ansi(r_avg, g_avg, b_avg)}{braille_char}{RESET}"
            
            if line:  # Only add non-empty lines
                lines.append(line)
    
    # Save to cache for future use
    _save_image_cache(image_path, height, width, lines, "braille")
    
    return lines

def image_to_ansi(image_path, height=20, width=None, render_mode="block"):
    """Render image using the specified mode (block or braille)"""
    if render_mode == "braille":
        return image_to_ansi_braille(image_path, height, width)
    else:
        return image_to_ansi_block(image_path, height, width)

def sharpen_image(image_path):
    try:
        from PIL import ImageEnhance, ImageFilter
        
        img = Image.open(image_path)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)
        
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        
        temp_path = os.path.join(os.path.dirname(image_path), "temp_" + os.path.basename(image_path))
        img.save(temp_path)
        return temp_path
    except Exception as e:
        print(f"warning: could not enhance image: {e}")
        return image_path

def get_images_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")

def list_available_images():
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
    if not image_name:
        return None
        
    if os.path.isfile(image_name):
        return image_name
    
    images_dir = get_images_dir()
    image_path = os.path.join(images_dir, image_name)
    if os.path.isfile(image_path):
        return image_path
    
    for ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
        test_path = os.path.join(images_dir, f"{image_name}{ext}")
        if os.path.isfile(test_path):
            return test_path
    
    return None 