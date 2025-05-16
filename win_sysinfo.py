"""
Windows System Information Module for WinFetch
"""

import os
import platform
import psutil
import subprocess
import re
import ctypes
from datetime import datetime
import wmi

def get_os_info():
    """Get Windows OS information."""
    os_name = platform.system()
    os_version = platform.version()
    build = platform.win32_ver()[1]
    edition = subprocess.check_output('powershell -command "(Get-WmiObject -Class Win32_OperatingSystem).Caption"', 
                                     shell=True).decode().strip()
    return f"OS: {edition} ({build})"

def get_hostname():
    """Get system hostname."""
    return f"Host: {platform.node()}"

def get_kernel_version():
    """Get Windows kernel version."""
    return f"Kernel: NT {platform.release()}"

def get_uptime():
    """Get system uptime."""
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    now = datetime.now()
    uptime = now - boot_time
    
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    uptime_str = ""
    if days > 0:
        uptime_str += f"{days}d "
    if hours > 0 or days > 0:
        uptime_str += f"{hours}h "
    if minutes > 0 or hours > 0 or days > 0:
        uptime_str += f"{minutes}m "
    uptime_str += f"{seconds}s"
    
    return f"Uptime: {uptime_str}"

def get_packages():
    """Get installed packages count from different package managers."""
    packages = []
    
    # Count Chocolatey packages if installed
    try:
        choco_count = subprocess.check_output('powershell -command "if (Get-Command choco -ErrorAction SilentlyContinue) { (Get-ChildItem -Path $env:ChocolateyInstall\\lib -Directory).Count }"', 
                                           shell=True).decode().strip()
        if choco_count and choco_count.isdigit():
            packages.append(f"{choco_count} (choco)")
    except:
        pass
    
    # Count Scoop packages if installed
    try:
        scoop_count = subprocess.check_output('powershell -command "if (Get-Command scoop -ErrorAction SilentlyContinue) { (Get-ChildItem -Path $env:USERPROFILE\\scoop\\apps -Directory).Count }"', 
                                           shell=True).decode().strip()
        if scoop_count and scoop_count.isdigit():
            packages.append(f"{scoop_count} (scoop)")
    except:
        pass
    
    # Count Winget packages
    try:
        winget_output = subprocess.check_output('powershell -command "if (Get-Command winget -ErrorAction SilentlyContinue) { winget list | Measure-Object -Line }"', 
                                             shell=True).decode().strip()
        winget_count = re.search(r'(\d+)', winget_output)
        if winget_count:
            # Subtract 1 for header line
            count = max(0, int(winget_count.group(1)) - 1)
            packages.append(f"{count} (winget)")
    except:
        pass
    
    if not packages:
        return "Packages: Unknown"
    
    return f"Packages: {', '.join(packages)}"

def get_shell():
    """Get current shell information."""
    powershell_path = os.environ.get('PSModulePath', '')
    if 'powershell' in os.environ.get('ComSpec', '').lower() or 'powershell' in powershell_path.lower():
        try:
            ps_version = subprocess.check_output('powershell -command "$PSVersionTable.PSVersion.ToString()"', 
                                              shell=True).decode().strip()
            return f"Shell: PowerShell {ps_version}"
        except:
            return f"Shell: PowerShell"
    else:
        return f"Shell: {os.environ.get('ComSpec', 'Unknown')}"

def get_resolution():
    """Get screen resolution."""
    try:
        user32 = ctypes.windll.user32
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        return f"Resolution: {width}x{height}"
    except:
        return "Resolution: Unknown"

def get_cpu_info():
    """Get CPU information."""
    try:
        cpu_info = subprocess.check_output('powershell -command "Get-WmiObject -Class Win32_Processor | Select-Object -Property Name, NumberOfCores, NumberOfLogicalProcessors | Format-List"', 
                                        shell=True).decode().strip()
        
        name_match = re.search(r'Name\s*:\s*(.+)', cpu_info)
        cores_match = re.search(r'NumberOfCores\s*:\s*(\d+)', cpu_info)
        threads_match = re.search(r'NumberOfLogicalProcessors\s*:\s*(\d+)', cpu_info)
        
        cpu_name = name_match.group(1) if name_match else "Unknown CPU"
        cores = cores_match.group(1) if cores_match else "?"
        threads = threads_match.group(1) if threads_match else "?"
        
        return f"CPU: {cpu_name} ({cores}C/{threads}T)"
    except:
        return f"CPU: {platform.processor()}"

def get_memory_info():
    """Get memory information."""
    mem = psutil.virtual_memory()
    total_gb = mem.total / (1024**3)
    used_gb = mem.used / (1024**3)
    percent = mem.percent
    
    return f"Memory: {used_gb:.1f}GB / {total_gb:.1f}GB ({percent}%)"

def get_disk_info():
    """Get disk information."""
    partitions = psutil.disk_partitions()
    disks = []
    
    for partition in partitions:
        if 'cdrom' in partition.opts or partition.fstype == '':
            continue
        
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            percent = usage.percent
            
            disks.append(f"{partition.device} ({used_gb:.1f}GB/{total_gb:.1f}GB, {percent}%)")
        except:
            continue
    
    if not disks:
        return "Disk: Not available"
    
    return f"Disk: {', '.join(disks[:2])}" + (f" (+{len(disks)-2} more)" if len(disks) > 2 else "")

def get_gpu_info():
    """Get GPU information."""
    try:
        w = wmi.WMI()
        gpu_info = w.Win32_VideoController()[0]
        return f"GPU: {gpu_info.Name} ({gpu_info.AdapterRAM/(1024**3):.1f}GB)"
    except:
        return "GPU: Unknown"

def get_all_info():
    """Get all system information."""
    return {
        "os": get_os_info(),
        "hostname": get_hostname(),
        "kernel": get_kernel_version(),
        "uptime": get_uptime(),
        "packages": get_packages(),
        "shell": get_shell(),
        "resolution": get_resolution(),
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "disk": get_disk_info(),
        "gpu": get_gpu_info()
    } 