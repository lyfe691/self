"""
windows system information module for winfetch
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
    os_name = platform.system()
    os_version = platform.version()
    build = platform.win32_ver()[1]
    edition = "Unknown"
    
    try:
        edition = subprocess.check_output('powershell -command "(Get-WmiObject -Class Win32_OperatingSystem).Caption"', 
                                     shell=True).decode().strip()
    except:
        pass
    
    if "Windows" in edition:
        edition = edition.replace("Microsoft ", "")
    
    return f"OS: {edition} {platform.machine()}"

def get_hostname():
    return f"Host: {platform.node()}"

def get_kernel_version():
    return f"Kernel: {platform.release()}"

def get_uptime():
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
    packages = []
    
    try:
        choco_count = subprocess.check_output('powershell -command "if (Get-Command choco -ErrorAction SilentlyContinue) { (Get-ChildItem -Path $env:ChocolateyInstall\\lib -Directory).Count }"', 
                                           shell=True).decode().strip()
        if choco_count and choco_count.isdigit():
            packages.append(f"{choco_count} (choco)")
    except:
        pass
    
    try:
        scoop_count = subprocess.check_output('powershell -command "if (Get-Command scoop -ErrorAction SilentlyContinue) { (Get-ChildItem -Path $env:USERPROFILE\\scoop\\apps -Directory).Count }"', 
                                           shell=True).decode().strip()
        if scoop_count and scoop_count.isdigit():
            packages.append(f"{scoop_count} (scoop)")
    except:
        pass
    
    try:
        winget_output = subprocess.check_output('powershell -command "if (Get-Command winget -ErrorAction SilentlyContinue) { winget list | Measure-Object -Line }"', 
                                             shell=True).decode().strip()
        winget_count = re.search(r'(\d+)', winget_output)
        if winget_count:
            count = max(0, int(winget_count.group(1)) - 1)
            packages.append(f"{count} (winget)")
    except:
        pass
    
    if not packages:
        return "Packages: Unknown"
    
    return f"Packages: {', '.join(packages)}"

def get_shell():
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
    try:
        user32 = ctypes.windll.user32
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        return f"Resolution: {width}x{height}"
    except:
        return "Resolution: Unknown"

def get_window_manager():
    return "WM: Windows Explorer"

def get_window_theme():
    try:
        theme_value = subprocess.check_output(
            'powershell -command "Get-ItemProperty -Path HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize -Name AppsUseLightTheme | Select-Object -ExpandProperty AppsUseLightTheme"',
            shell=True
        ).decode().strip()
        
        theme_mode = "Light" if theme_value == "1" else "Dark"
        
        try:
            theme_name = subprocess.check_output(
                'powershell -command "(Get-ItemProperty -Path \'HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\' -Name CurrentTheme).CurrentTheme | Split-Path -Leaf"',
                shell=True
            ).decode().strip().replace(".theme", "")
        except:
            theme_name = f"Windows {theme_mode}"
        
        return f"Theme: {theme_name} ({theme_mode})"
    except:
        return "Theme: Unknown"

def get_icons():
    return "Icons: Windows Default"

def get_terminal():
    try:
        process_name = subprocess.check_output('powershell -command "Get-Process -Id $PID | Select-Object -ExpandProperty Name"',
                                             shell=True).decode().strip()
        
        if "powershell" in process_name.lower():
            return "Terminal: Windows PowerShell"
        elif "cmd" in process_name.lower():
            return "Terminal: Command Prompt"
        elif "windowsterminal" in process_name.lower():
            return "Terminal: Windows Terminal"
        else:
            return f"Terminal: {process_name}"
    except:
        return "Terminal: Unknown"

def get_font():
    try:
        return "Font: Consolas"
    except:
        return "Font: Unknown"

def get_cpu_info():
    try:
        w = wmi.WMI()
        cpu = w.Win32_Processor()[0]
        cpu_name = cpu.Name.strip()
        
        cpu_name = re.sub(r'\s+', ' ', cpu_name)
        
        try:
            freq = f" @ {round(cpu.MaxClockSpeed/1000, 2)}GHz"
        except:
            freq = ""
        
        try:
            cores = cpu.NumberOfCores
            threads = cpu.NumberOfLogicalProcessors
            cores_threads = f" ({cores}C/{threads}T)"
        except:
            cores_threads = ""
        
        return f"CPU: {cpu_name}{freq}{cores_threads}"
    except:
        return f"CPU: {platform.processor()}"

def get_gpu_info():
    try:
        w = wmi.WMI()
        gpu_info = w.Win32_VideoController()[0]
        gpu_name = gpu_info.Name
        
        try:
            gpu_ram = gpu_info.AdapterRAM
            if gpu_ram and gpu_ram > 0:
                ram_str = f" ({gpu_ram/(1024**3):.1f}GB)"
            else:
                ram_str = ""
        except:
            ram_str = ""
        
        return f"GPU: {gpu_name}{ram_str}"
    except:
        return "GPU: Unknown"

def get_memory_info():
    mem = psutil.virtual_memory()
    total_gb = mem.total / (1024**3)
    used_gb = mem.used / (1024**3)
    
    total_mb = int(total_gb * 1024)
    used_mb = int(used_gb * 1024)
    
    return f"Memory: {used_mb}MiB / {total_mb}MiB"

def get_disk_info():
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

def get_all_info():
    return {
        "os": get_os_info(),
        "hostname": get_hostname(),
        "kernel": get_kernel_version(),
        "uptime": get_uptime(),
        "packages": get_packages(),
        "shell": get_shell(),
        "resolution": get_resolution(),
        "wm": get_window_manager(),
        "theme": get_window_theme(),
        "icons": get_icons(),
        "terminal": get_terminal(),
        "font": get_font(),
        "cpu": get_cpu_info(),
        "gpu": get_gpu_info(),
        "memory": get_memory_info(),
        "disk": get_disk_info()
    }

def safe_get(func, fallback="Unknown"):
    try:
        return func()
    except Exception as e:
        print(f"warning: {e}")
        return fallback 