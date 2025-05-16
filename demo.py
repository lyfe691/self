#!/usr/bin/env python3
"""
WinFetch Demo Script
Shows different ways to use WinFetch
"""

import os
import subprocess
import time
import shutil
from colorama import init, Fore, Style

# Initialize colorama
init()

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    """Print a formatted header."""
    term_width = shutil.get_terminal_size().columns
    print(Fore.CYAN + "=" * term_width + Style.RESET_ALL)
    print(Fore.CYAN + f" {text} ".center(term_width, "-") + Style.RESET_ALL)
    print(Fore.CYAN + "=" * term_width + Style.RESET_ALL)
    print()

def run_command(command, wait=True):
    """Run a command and optionally wait for user input."""
    print(Fore.GREEN + f"Running: {command}" + Style.RESET_ALL)
    print()
    
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Error executing command: {e}" + Style.RESET_ALL)
    
    if wait:
        print()
        input(Fore.YELLOW + "Press Enter to continue..." + Style.RESET_ALL)
        print()

def main():
    """Main demo function."""
    clear_screen()
    print_header("Welcome to WinFetch Demo")
    
    print("This demo will show you how to use WinFetch.")
    print("Make sure you have installed the required dependencies:")
    print(Fore.YELLOW + "pip install -r requirements.txt" + Style.RESET_ALL)
    print()
    input("Press Enter to start the demo...")
    
    # Demo 1: Basic WinFetch
    clear_screen()
    print_header("Basic WinFetch")
    run_command("python winfetch.py")
    
    # Demo 2: Setup Configuration
    clear_screen()
    print_header("Setup Wizard")
    print("The setup wizard lets you configure WinFetch interactively.")
    print("It's the easiest way to customize WinFetch.")
    print()
    print("We won't run it as part of this demo, but you can try it with:")
    print(Fore.YELLOW + "python winfetch.py --setup" + Style.RESET_ALL)
    print()
    input("Press Enter to continue...")
    
    # Demo 3: Config File
    clear_screen()
    print_header("Configuration File")
    print("WinFetch is primarily configured through the config.json file.")
    print(f"Location: {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'config.json')}")
    print()
    print("You can edit this file to customize:")
    print("- Display type (image or ASCII art)")
    print("- Image file or ASCII art selection")
    print("- Color theme")
    print("- Image height")
    print("- Information displayed")
    print()
    print("After editing, just run WinFetch normally:")
    print(Fore.YELLOW + "python winfetch.py" + Style.RESET_ALL)
    print()
    
    # Final notes
    clear_screen()
    print_header("Tips for Best Results")
    print("1. Place your preferred images in the 'images' directory")
    print("2. For best image quality, try images with:")
    print("   - Clear subjects with good contrast")
    print("   - Simple backgrounds")
    print("   - Height around 400-800 pixels")
    print()
    print("3. Adjust image height in the config file for best results")
    print("   Recommended: 18-25 lines for most terminal sizes")
    print()
    print("4. Experiment with different color themes")
    print()
    input("Press Enter to finish the demo...")
    
    # Final screen
    clear_screen()
    print_header("Demo Complete")
    print("You've learned how to use WinFetch!")
    print()
    print("Basic usage:")
    print(Fore.YELLOW + "python winfetch.py" + Style.RESET_ALL)
    print()
    print("Run setup wizard:")
    print(Fore.YELLOW + "python winfetch.py --setup" + Style.RESET_ALL)
    print()
    print("Thank you for trying WinFetch!")
    print()

if __name__ == "__main__":
    main() 