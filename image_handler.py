"""
image handling module for winfetch
"""

import os
import sys
from PIL import Image
import math
import shutil

RESET = '\033[0m'

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
        
        img = img.resize((target_width, target_height), Image.LANCZOS)
        return img
    except Exception as e:
        print(f"error processing image: {e}")
        return None

def rgb_to_ansi(r, g, b, bg=False):
    if bg:
        return f'\033[48;2;{r};{g};{b}m'
    else:
        return f'\033[38;2;{r};{g};{b}m'

def image_to_ansi(image_path, height=20, width=None):
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
    
    return lines

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