# Using Custom Images with WinFetch

WinFetch supports displaying custom images in the terminal instead of ASCII art.

## Quick Start

1. Place your image files in the `images/` directory
2. Run the setup wizard: `python winfetch.py --setup`
3. Select "Image" as the display type and choose your image

## Image Recommendations

For best results, use images with:

- Clear subjects with good contrast against background
- Simple backgrounds or transparent backgrounds
- Reasonable dimensions (around 400-800px height)
- Common formats (PNG, JPG, GIF)

## Adjusting Image Quality

If your image appears blurry or distorted:

1. Try adjusting the image height in the config file
   ```json
   {
       "image_height": 22  # Try values between 18-25
   }
   ```

2. Use images with clean edges and good contrast

3. Use PNG files with transparency for best results

## Troubleshooting

If you don't see your image:

1. Make sure the image file exists in the `images/` directory
2. Check that the filename in `config.json` matches exactly
3. Try running with `python winfetch.py --setup` to select the image interactively

## Technical Details

WinFetch displays images by:

1. Resizing the image to fit your terminal dimensions
2. Converting each pixel to a colored space using ANSI color codes
3. Displaying the result alongside system information

This means image quality depends on:
- Terminal support for 24-bit color
- Font and character spacing in your terminal
- Terminal dimensions 