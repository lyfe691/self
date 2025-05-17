# Self

<!-- might add if it actually gets stars -->
<!-- ![GitHub stars](https://img.shields.io/github/stars/lyfe691/self?style=flat-square&color=blue) -->
![GitHub issues](https://img.shields.io/github/issues/lyfe691/self?style=flat-square&color=green)
![GitHub last commit](https://img.shields.io/github/last-commit/lyfe691/self?style=flat-square&color=purple)
![GitHub repo size](https://img.shields.io/github/repo-size/lyfe691/self?style=flat-square&color=orange)
![GitHub](https://img.shields.io/github/license/lyfe691/self?style=flat-square&color=yellow)
![Visitors](https://visitor-badge.laobi.icu/badge?page_id=lyfe691.self&style=flat-square&color=teal)

A customizable Windows system information display tool inspired by [Neofetch](https://github.com/dylanaraps/neofetch).

## Install

> [!NOTE]
> Install via PowerShell. It'll install at user level so no need to run as administrator. If you want it beyond user level just move the folder to `C:\Program Files\Self`.

```powershell
iwr -Uri "https://raw.githubusercontent.com/lyfe691/self/main/install.ps1" -UseBasicParsing | iex
```

## Features

- System info + image/ASCII art display
- Image Render modes: Block (▀), Braille (⠿). i recommend block due to better color visibility.
- Customizable themes and layout

## Usage

```
self                 # Run with default settings
self --setup         # Run setup wizard
self --update        # Update to latest version
self --image <file>  # Use specific image
self --ascii <file>  # Use specific ASCII art
self --height <n>    # Set image height
self --width <n>     # Set image width
self --version       # Show version information
self --config <path> # Use custom config file
self --no-cache      # Skip cached system info
self --debug         # Run in simplified debug mode
```

<details>
<summary>More options</summary>

- `--ascii <file>`: Use specific ASCII art
- `--height <n>`, `--width <n>`: Set image dimensions
- `--no-cache`: Skip using cached system info
- `--debug`: Run in simplified mode
- `--version`: Show version info

</details>

## Screenshots

<img src="https://raw.githubusercontent.com/lyfe691/self/main/docs/self.png" width="80%" alt="self screenshot">

## License

[MIT](LICENSE) © [Yanis Sebastian Zürcher](https://ysz.life)
