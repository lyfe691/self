# Self - Windows System Information Tool - Installation Script
$VERSION = "1.0.0"
$INSTALL_DIR = "$env:USERPROFILE\SelfTool"
$REPO_URL = "https://github.com/lyfe691/self"
$RAW_URL = "https://raw.githubusercontent.com/lyfe691/self/main"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Self - Windows System Information Tool - Installation" -ForegroundColor Cyan
Write-Host "Version: $VERSION" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Create installation directory
Write-Host "Creating installation directories..."
New-Item -ItemType Directory -Path $INSTALL_DIR -Force | Out-Null
New-Item -ItemType Directory -Path "$INSTALL_DIR\ascii", "$INSTALL_DIR\config", "$INSTALL_DIR\images", "$INSTALL_DIR\cache" -Force | Out-Null

# Download required files
Write-Host "Downloading required files..."
$FILES = @("self.py", "win_sysinfo.py", "color_themes.py", "image_handler.py", "default_image.py", "requirements.txt")
foreach ($file in $FILES) {
    try {
        Invoke-WebRequest -Uri "$RAW_URL/$file" -OutFile "$INSTALL_DIR\$file" -ErrorAction Stop
    } catch {
        Write-Host "Error: Failed to download $file" -ForegroundColor Red
        Write-Host $_.Exception.Message
        exit 1
    }
}

# Download directories
Write-Host "Downloading additional resources..."

# Function to download files from filelist.txt
function Download-Files-From-List {
    param (
        [string]$Directory,
        [string]$FilePath
    )
    
    try {
        Invoke-WebRequest -Uri "$RAW_URL/$Directory/filelist.txt" -OutFile "$INSTALL_DIR\$Directory\filelist.txt" -ErrorAction SilentlyContinue
        if (Test-Path "$INSTALL_DIR\$Directory\filelist.txt") {
            foreach ($line in Get-Content "$INSTALL_DIR\$Directory\filelist.txt") {
                if (-not [string]::IsNullOrWhiteSpace($line)) {
                    try {
                        Invoke-WebRequest -Uri "$RAW_URL/$Directory/$line" -OutFile "$INSTALL_DIR\$Directory\$line" -ErrorAction SilentlyContinue
                    } catch {
                        Write-Host "Warning: Could not download $line" -ForegroundColor Yellow
                    }
                }
            }
        }
    } catch {
        Write-Host "Warning: Could not download files for $Directory" -ForegroundColor Yellow
    }
}

# Download files from each directory
Download-Files-From-List -Directory "ascii"
Download-Files-From-List -Directory "config"
Download-Files-From-List -Directory "images"

# Create batch file
Write-Host "Creating launcher..."
Set-Content -Path "$INSTALL_DIR\self.bat" -Value "@echo off`npython `"$INSTALL_DIR\self.py`" %*"

# Add to PATH
Write-Host "Adding to PATH..."
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if (-not $userPath.Contains($INSTALL_DIR)) {
    [Environment]::SetEnvironmentVariable("PATH", "$userPath;$INSTALL_DIR", "User")
    Write-Host "Added to PATH successfully."
} else {
    Write-Host "Already in PATH."
}

# Install dependencies
Write-Host "Installing dependencies..."
try {
    Start-Process -FilePath "python" -ArgumentList "-m pip install -r `"$INSTALL_DIR\requirements.txt`"" -Wait -NoNewWindow
} catch {
    Write-Host "Warning: Could not install dependencies. You may need to run: pip install -r `"$INSTALL_DIR\requirements.txt`"" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "installed" -ForegroundColor Green
Write-Host "self has been installed to $INSTALL_DIR" -ForegroundColor Green
Write-Host "you may need to restart your terminal or computer for the PATH changes to take effect." -ForegroundColor Yellow
Write-Host "you can now use 'self' to show system information." -ForegroundColor Green 