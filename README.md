# WinFetch

A customizable system information tool for Windows, inspired by Neofetch.

## Features
- Display system information in a Neofetch-like format
- Support for real images (not just ASCII art)
- Customizable ASCII art templates
- Color themes
- Configurable display options

## Requirements
- Python 3.6+
- Windows 10/11
- Pip packages: colorama, psutil, wmi, Pillow, rich

## Usage
```
python winfetch.py [options]
```

## Options
```
--image IMAGE       Path to an image file or name of image in the images directory
--ascii ASCII       Use ASCII art instead of an image (specify art name)
--theme THEME       Color theme (default, powershell, windows, red, green, magenta, etc.)
--height HEIGHT     Height of the displayed image (default: 20 lines)
--list-images       List available images
--list-themes       List available color themes
--list-ascii        List available ASCII art templates
--config CONFIG     Path to custom config file
```

## Using Custom Images
1. Place your images in the `images/` directory
2. Run WinFetch with `--image filename.png` or `--image /path/to/your/image.jpg`
3. Or edit `config/config.json` to set your image as the default

Supported image formats:
- PNG
- JPG/JPEG
- BMP
- GIF (first frame only)

## Configuration
Edit `config/config.json` to customize your WinFetch experience:
```json
{
    "display_type": "image",  // "image" or "ascii"
    "image": "windows_logo.png",  // Default image
    "ascii_art": "windows",  // Default ASCII art
    "theme": "blue",  // Default theme
    "info_display": [
        "os", "hostname", "kernel", "uptime", "packages", 
        "shell", "resolution", "wm", "theme", "terminal", 
        "font", "cpu", "gpu", "memory", "disk"
    ]
}
```

## Examples
- Show system info with a custom image:
  ```
  python winfetch.py --image my_photo.jpg
  ```

- Use ASCII art instead of an image:
  ```
  python winfetch.py --ascii windows
  ```

- Change the color theme:
  ```
  python winfetch.py --theme powershell
  ``` 