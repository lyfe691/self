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
    
    print("This demo will show you different ways to use WinFetch.")
    print("Make sure you have installed the required dependencies:")
    print(Fore.YELLOW + "pip install -r requirements.txt" + Style.RESET_ALL)
    print()
    input("Press Enter to start the demo...")
    
    # Demo 1: Basic WinFetch
    clear_screen()
    print_header("Basic WinFetch")
    run_command("python winfetch.py")
    
    # Demo 2: Different ASCII art
    clear_screen()
    print_header("WinFetch with different ASCII art")
    run_command("python winfetch.py --ascii powershell")
    
    # Demo 3: Different theme
    clear_screen()
    print_header("WinFetch with different theme")
    run_command("python winfetch.py --theme magenta")
    
    # Demo 4: List available ASCII art
    clear_screen()
    print_header("List Available ASCII Art")
    run_command("python winfetch.py --list-ascii", wait=False)
    
    print()
    print_header("List Available Themes")
    run_command("python winfetch.py --list-themes")
    
    # Demo 5: List available images
    clear_screen()
    print_header("List Available Images")
    run_command("python winfetch.py --list-images", wait=False)
    
    print()
    print("To add custom images, place them in the 'images' directory.")
    print("Supported formats: PNG, JPG/JPEG, BMP, GIF.")
    print()
    input("Press Enter to continue...")
    
    # Final notes
    clear_screen()
    print_header("Demo Complete")
    print("You've seen the basic features of WinFetch!")
    print()
    print("For more customization, edit the config file:")
    print(Fore.YELLOW + "config/config.json" + Style.RESET_ALL)
    print()
    print("Run with custom options:")
    print(Fore.YELLOW + "python winfetch.py --image myimage.jpg --theme red" + Style.RESET_ALL)
    print()
    print("Thank you for trying WinFetch!")
    print()

if __name__ == "__main__":
    main() 