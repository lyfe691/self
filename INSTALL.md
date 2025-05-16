# WinFetch Installation Guide

## Prerequisites
- Python 3.6 or higher
- pip (Python package manager)

## Basic Installation

1. Clone the repository or download the ZIP file:
```
git clone https://github.com/yourusername/winfetch.git
cd winfetch
```

2. Install required dependencies:
```
pip install -r requirements.txt
```

## Running WinFetch

Run WinFetch with Python:
```
python winfetch.py
```

## Optional Installation Steps

### Create a PowerShell alias

Add this to your PowerShell profile to create an alias:

1. Open your PowerShell profile:
```powershell
notepad $PROFILE
```

2. Add the following line (adjust the path as needed):
```powershell
function winfetch { python "C:\path\to\winfetch\winfetch.py" $args }
```

3. Save the file and restart PowerShell.

### Create a batch file for command-line use

Create a `winfetch.bat` file in a directory that's in your PATH:

```batch
@echo off
python "C:\path\to\winfetch\winfetch.py" %*
```

## Customization

### Custom ASCII Art

Create your own ASCII art files in the `ascii` directory with a `.txt` extension.

### Configuration

Edit `config/config.json` to customize display options:

- Change the default ASCII art
- Change the color theme
- Reorder or hide system information

## Command-line Options

```
python winfetch.py --help
```

Available options:
- `--config <path>`: Use a custom config file
- `--ascii <name>`: Use a specific ASCII template
- `--theme <name>`: Use a specific color theme
- `--list-themes`: List available color themes
- `--list-ascii`: List available ASCII templates 