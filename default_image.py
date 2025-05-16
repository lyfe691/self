#!/usr/bin/env python3
"""
Create a simple Windows logo image for WinFetch
"""

from PIL import Image, ImageDraw

def create_windows_logo(size=400, filename="images/windows_logo.png"):
    """Create a simple Windows logo image"""
    # Create a transparent image
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Calculate dimensions
    border = int(size * 0.05)
    square_size = (size - (border * 3)) // 2
    
    # Windows logo colors
    colors = [
        (246, 83, 20),  # Red (top-left)
        (124, 187, 0),  # Green (top-right)
        (0, 161, 241),  # Blue (bottom-left)
        (255, 187, 0)   # Yellow (bottom-right)
    ]
    
    # Draw the four squares
    positions = [
        (border, border),  # Top-left
        (border * 2 + square_size, border),  # Top-right
        (border, border * 2 + square_size),  # Bottom-left
        (border * 2 + square_size, border * 2 + square_size)  # Bottom-right
    ]
    
    for i, (x, y) in enumerate(positions):
        draw.rectangle(
            [x, y, x + square_size, y + square_size],
            fill=colors[i]
        )
    
    # Save the image
    img.save(filename)
    print(f"Windows logo created at {filename}")

if __name__ == "__main__":
    create_windows_logo() 