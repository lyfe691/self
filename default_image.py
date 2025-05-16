#!/usr/bin/env python3
"""
create a simple windows logo image for winfetch
"""

from PIL import Image, ImageDraw

def create_windows_logo(size=400, filename="images/windows_logo.png"):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    border = int(size * 0.05)
    square_size = (size - (border * 3)) // 2
    
    colors = [
        (246, 83, 20),  # red (top-left)
        (124, 187, 0),  # green (top-right)
        (0, 161, 241),  # blue (bottom-left)
        (255, 187, 0)   # yellow (bottom-right)
    ]
    
    positions = [
        (border, border),
        (border * 2 + square_size, border),
        (border, border * 2 + square_size),
        (border * 2 + square_size, border * 2 + square_size)
    ]
    
    for i, (x, y) in enumerate(positions):
        draw.rectangle(
            [x, y, x + square_size, y + square_size],
            fill=colors[i]
        )
    
    img.save(filename)
    print(f"windows logo created at {filename}")

if __name__ == "__main__":
    create_windows_logo() 