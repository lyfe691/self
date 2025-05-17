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

# Function to download directory contents from GitHub
function Download-Directory-Contents {
    param (
        [string]$Directory
    )
    
    Write-Host "Downloading $Directory files..."
    
    try {
        # First try to get the filelist.txt which contains all files in the directory
        $filelistUrl = "$RAW_URL/$Directory/filelist.txt"
        $filelistResponse = Invoke-WebRequest -Uri $filelistUrl -ErrorAction SilentlyContinue
        
        if ($filelistResponse.StatusCode -eq 200) {
            # Parse the filelist and download each file
            $files = $filelistResponse.Content -split "`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
            
            foreach ($file in $files) {
                $file = $file.Trim()
                try {
                    Write-Host "  Downloading $Directory/$file"
                    Invoke-WebRequest -Uri "$RAW_URL/$Directory/$file" -OutFile "$INSTALL_DIR\$Directory\$file" -ErrorAction Stop
                } catch {
                    Write-Host "  Warning: Could not download $file" -ForegroundColor Yellow
                }
            }
        } else {
            # Fallback: Try to download some common files if filelist.txt doesn't exist
            Write-Host "  No filelist found. Trying common file patterns..." -ForegroundColor Yellow
            
            # Try common image formats for images directory
            if ($Directory -eq "images") {
                $extensions = @(".png", ".jpg", ".jpeg", ".gif")
                $baseNames = @("logo", "background", "icon", "default", "system")
                
                foreach ($baseName in $baseNames) {
                    foreach ($ext in $extensions) {
                        $fileName = "$baseName$ext"
                        try {
                            Invoke-WebRequest -Uri "$RAW_URL/$Directory/$fileName" -OutFile "$INSTALL_DIR\$Directory\$fileName" -ErrorAction SilentlyContinue
                        } catch {
                            # Silently continue if file doesn't exist
                        }
                    }
                }
            }
            
            # Try common ASCII art files
            if ($Directory -eq "ascii") {
                $artFiles = @("logo.txt", "banner.txt", "welcome.txt", "computer.txt")
                
                foreach ($file in $artFiles) {
                    try {
                        Invoke-WebRequest -Uri "$RAW_URL/$Directory/$file" -OutFile "$INSTALL_DIR\$Directory\$file" -ErrorAction SilentlyContinue
                    } catch {
                        # Silently continue if file doesn't exist
                    }
                }
            }
            
            # Try common config files
            if ($Directory -eq "config") {
                $configFiles = @("default.json", "settings.json", "config.json", "themes.json")
                
                foreach ($file in $configFiles) {
                    try {
                        Invoke-WebRequest -Uri "$RAW_URL/$Directory/$file" -OutFile "$INSTALL_DIR\$Directory\$file" -ErrorAction SilentlyContinue
                    } catch {
                        # Silently continue if file doesn't exist
                    }
                }
            }
        }
    } catch {
        Write-Host "  Warning: Could not download files for $Directory" -ForegroundColor Yellow
    }
}

# Download files from each directory
Download-Directory-Contents -Directory "ascii"
Download-Directory-Contents -Directory "config"
Download-Directory-Contents -Directory "images"

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