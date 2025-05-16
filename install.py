#!/usr/bin/env python3
"""
Installation wizard for Self - Windows System Information Tool
"""

import os
import sys
import shutil
import winreg
import subprocess
import ctypes
from pathlib import Path
import tempfile

VERSION = "1.0.0"
INSTALL_DIR = os.path.join(os.path.expanduser("~"), "SelfTool")
REQUIRED_FILES = [
    "self.py", "win_sysinfo.py", "color_themes.py", "image_handler.py", 
    "default_image.py", "requirements.txt"
]
REQUIRED_DIRS = ["ascii", "config", "images"]

def is_admin():
    """Check if the script is running with admin privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def check_requirements():
    """Check if all required files exist"""
    missing_files = []
    for file in REQUIRED_FILES:
        if not os.path.isfile(file):
            missing_files.append(file)
    
    missing_dirs = []
    for dir_name in REQUIRED_DIRS:
        if not os.path.isdir(dir_name):
            missing_dirs.append(dir_name)
    
    if missing_files or missing_dirs:
        print("Error: Some required files or directories are missing:")
        if missing_files:
            print(f"Missing files: {', '.join(missing_files)}")
        if missing_dirs:
            print(f"Missing directories: {', '.join(missing_dirs)}")
        return False
    
    return True

def create_batch_file():
    """Create a batch file that will run self.py"""
    batch_content = f'@echo off\npython "{os.path.join(INSTALL_DIR, "self.py")}" %*'
    batch_path = os.path.join(INSTALL_DIR, "self.bat")
    
    with open(batch_path, 'w') as f:
        f.write(batch_content)
    
    return batch_path

def add_to_path(directory):
    """Add the specified directory to the PATH environment variable"""
    try:
        # Open the registry key
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, 
            r"Environment", 
            0, 
            winreg.KEY_READ | winreg.KEY_WRITE
        )
        
        # Get the current PATH value
        try:
            path_value, _ = winreg.QueryValueEx(key, "PATH")
        except FileNotFoundError:
            path_value = ""
        
        # Check if the directory is already in PATH
        paths = [p.lower() for p in path_value.split(';') if p]
        if directory.lower() not in paths:
            # Add to PATH if not already present
            new_path = f"{path_value};{directory}" if path_value else directory
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            print(f"Added {directory} to PATH")
        else:
            print(f"{directory} is already in PATH")
        
        # Close the key
        winreg.CloseKey(key)
        
        # Notify other processes of the change using SendMessageTimeout
        subprocess.run([
            "powershell", 
            "-Command", 
            "$sig = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer([System.Runtime.InteropServices.Marshal]::GetProcAddress([System.Runtime.InteropServices.Marshal]::GetHINSTANCE([System.Reflection.Assembly]::LoadWithPartialName('user32.dll').Location), 'SendMessageTimeoutW'), [System.Runtime.InteropServices.VarEnum]); $result = $null; [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer([System.Runtime.InteropServices.Marshal]::GetProcAddress([System.Runtime.InteropServices.Marshal]::GetHINSTANCE([System.Reflection.Assembly]::LoadWithPartialName('user32.dll').Location), 'SendMessageTimeoutW'), $sig).Invoke([System.IntPtr]0xffff, 0x1a, [System.IntPtr]::Zero, 'Environment', 2, 5000, [ref]$result);"
        ], shell=True, check=False)
        
        return True
    except Exception as e:
        print(f"Error adding to PATH: {e}")
        return False

def install_dependencies():
    """Install required Python dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False

def install():
    """Install the tool"""
    if not check_requirements():
        return False
    
    # Create installation directory
    os.makedirs(INSTALL_DIR, exist_ok=True)
    
    # Copy files
    print(f"Installing to {INSTALL_DIR}...")
    for file in REQUIRED_FILES:
        shutil.copy(file, INSTALL_DIR)
    
    # Copy directories
    for dir_name in REQUIRED_DIRS:
        src_dir = os.path.join(os.getcwd(), dir_name)
        dst_dir = os.path.join(INSTALL_DIR, dir_name)
        
        # Remove directory if it exists
        if os.path.exists(dst_dir):
            shutil.rmtree(dst_dir)
        
        # Copy directory
        shutil.copytree(src_dir, dst_dir)
    
    # Create cache directory
    os.makedirs(os.path.join(INSTALL_DIR, "cache"), exist_ok=True)
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create batch file
    batch_path = create_batch_file()
    
    # Add to PATH
    if not add_to_path(INSTALL_DIR):
        print("Warning: Failed to add to PATH. You may need to run as administrator.")
    
    print("\nInstallation completed!")
    print(f"The 'self' command has been installed to {INSTALL_DIR}")
    print("You may need to restart your terminal or computer for the PATH changes to take effect.")
    print("\nYou can now use 'self' to show system information.")
    
    return True

def run_as_admin():
    """Re-run the script with admin privileges"""
    if not is_admin():
        # Save the current script to a temporary file
        temp_script = os.path.join(tempfile.gettempdir(), "self_installer.py")
        shutil.copy(__file__, temp_script)
        
        # Run the temporary script with admin privileges
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, temp_script, None, 1)
        return True
    return False

def main():
    print("=" * 60)
    print("Self - Windows System Information Tool - Installation Wizard")
    print(f"Version: {VERSION}")
    print("=" * 60)
    
    choice = input("Do you want to install Self? [Y/n]: ").lower()
    if choice not in ['', 'y', 'yes']:
        print("Installation cancelled.")
        return
    
    admin_choice = input("Run as administrator? (Recommended) [Y/n]: ").lower()
    if admin_choice in ['', 'y', 'yes']:
        if run_as_admin():
            print("Installation will continue with admin privileges.")
            return
    
    install()

if __name__ == "__main__":
    main() 