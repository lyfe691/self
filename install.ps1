# Self - Windows System Information Tool - Installation Script
$VERSION = "1.0.0"
$INSTALL_DIR = "$env:USERPROFILE\self"
$REPO_URL = "https://github.com/lyfe691/self"
$RAW_URL = "https://raw.githubusercontent.com/lyfe691/self/main"
$API_URL = "https://api.github.com/repos/lyfe691/self/contents"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Self - Windows System Information Tool - Installation" -ForegroundColor Cyan
Write-Host "Version: $VERSION" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Check if Python is installed
Write-Host "Checking if Python is installed..."
$pythonInstalled = $false
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -like "Python*") {
        $pythonInstalled = $true
        Write-Host "Python is installed: $pythonVersion" -ForegroundColor Green
    }
} catch {
    $pythonInstalled = $false
}

if (-not $pythonInstalled) {
    Write-Host "ERROR: Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/downloads/ and try again." -ForegroundColor Red
    Write-Host "Installation aborted." -ForegroundColor Red
    exit 1
}

# Create installation directory
Write-Host "Creating installation directories..."
try {
    New-Item -ItemType Directory -Path $INSTALL_DIR -Force | Out-Null
    New-Item -ItemType Directory -Path "$INSTALL_DIR\ascii", "$INSTALL_DIR\config", "$INSTALL_DIR\images", "$INSTALL_DIR\cache" -Force | Out-Null
} catch {
    Write-Host "ERROR: Failed to create installation directories." -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}

# Download required files
Write-Host "Downloading required files..."
$FILES = @("self.py", "win_sysinfo.py", "color_themes.py", "image_handler.py", "default_image.py", "requirements.txt")
$downloadError = $false
foreach ($file in $FILES) {
    try {
        Invoke-WebRequest -Uri "$RAW_URL/$file" -OutFile "$INSTALL_DIR\$file" -ErrorAction Stop
    } catch {
        Write-Host "ERROR: Failed to download $file" -ForegroundColor Red
        Write-Host $_.Exception.Message
        $downloadError = $true
    }
}

if ($downloadError) {
    Write-Host "Installation failed due to download errors." -ForegroundColor Red
    exit 1
}

# Download directories
Write-Host "Downloading additional resources..."

# Function to download directory contents from GitHub API
function Download-Directory-Contents {
    param (
        [string]$Directory
    )
    
    Write-Host "Downloading $Directory files..."
    
    try {
        # Use GitHub API to list directory contents
        $apiResponse = Invoke-RestMethod -Uri "$API_URL/$Directory" -ErrorAction Stop
        
        foreach ($item in $apiResponse) {
            if ($item.type -eq "file") {
                try {
                    Write-Host "  Downloading $Directory/$($item.name)"
                    Invoke-WebRequest -Uri $item.download_url -OutFile "$INSTALL_DIR\$Directory\$($item.name)" -ErrorAction Stop
                } catch {
                    Write-Host "  Warning: Could not download $($item.name)" -ForegroundColor Yellow
                }
            }
        }
        Write-Host "  Successfully downloaded $Directory files" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "  Warning: Could not retrieve $Directory files listing" -ForegroundColor Yellow
        
        # If we can't get the directory listing, try to clone the entire repository
        try {
            Write-Host "  Attempting to clone repository..."
            $tempDir = "$env:TEMP\self-temp"
            New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
            
            # Check if git is installed
            $gitInstalled = $null
            try {
                $gitInstalled = Get-Command git -ErrorAction SilentlyContinue
            } catch {
                $gitInstalled = $null
            }
            
            if ($gitInstalled) {
                # Use git to clone
                Start-Process -FilePath "git" -ArgumentList "clone $REPO_URL $tempDir" -Wait -NoNewWindow
                
                # Copy the specific directory
                if (Test-Path "$tempDir\$Directory") {
                    Copy-Item -Path "$tempDir\$Directory\*" -Destination "$INSTALL_DIR\$Directory\" -Recurse -Force
                    Write-Host "  Successfully copied $Directory from cloned repository" -ForegroundColor Green
                    
                    # Clean up
                    Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
                    return $true
                }
                
                # Clean up
                Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
            } else {
                Write-Host "  Git not installed. Falling back to direct downloads." -ForegroundColor Yellow
                
                # Fallback for specific directories
                $success = $false
                if ($Directory -eq "ascii") {
                    $files = @("logo.txt", "banner.txt", "computer.txt", "welcome.txt")
                    $success = $true
                } elseif ($Directory -eq "config") {
                    $files = @("config.json", "default.json", "themes.json")
                    $success = $true
                } elseif ($Directory -eq "images") {
                    $files = @("logo.png", "background.png", "icon.png", "default.png", "system.png")
                    $success = $true
                }
                
                if ($success) {
                    foreach ($file in $files) {
                        try {
                            $result = Invoke-WebRequest -Uri "$RAW_URL/$Directory/$file" -OutFile "$INSTALL_DIR\$Directory\$file" -ErrorAction SilentlyContinue
                            if ($result -ne $null) {
                                $success = $true
                            }
                        } catch {
                            # Silently continue if file doesn't exist
                        }
                    }
                    if ($success) {
                        Write-Host "  Downloaded some files for $Directory" -ForegroundColor Yellow
                        return $true
                    }
                }
            }
        } catch {
            Write-Host "  Failed to retrieve $Directory directory contents" -ForegroundColor Red
        }
    }
    return $false
}

# Download files from each directory
$asciiSuccess = Download-Directory-Contents -Directory "ascii"
$configSuccess = Download-Directory-Contents -Directory "config"
$imagesSuccess = Download-Directory-Contents -Directory "images"

if (-not ($asciiSuccess -and $configSuccess -and $imagesSuccess)) {
    Write-Host "Warning: Some resources may be missing. The tool may not function correctly." -ForegroundColor Yellow
}

# Create batch file
Write-Host "Creating launcher..."
try {
    Set-Content -Path "$INSTALL_DIR\self.bat" -Value "@echo off`npython `"$INSTALL_DIR\self.py`" %*" -ErrorAction Stop
} catch {
    Write-Host "ERROR: Failed to create launcher script." -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}

# Add to PATH
Write-Host "Adding to PATH..."
try {
    $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if (-not $userPath.Contains($INSTALL_DIR)) {
        [Environment]::SetEnvironmentVariable("PATH", "$userPath;$INSTALL_DIR", "User")
        Write-Host "Added to PATH successfully." -ForegroundColor Green
    } else {
        Write-Host "Already in PATH." -ForegroundColor Green
    }
} catch {
    Write-Host "WARNING: Could not add to PATH. You may need to add $INSTALL_DIR to your PATH manually." -ForegroundColor Yellow
}

# Install dependencies
Write-Host "Installing dependencies..."
try {
    $pipProcess = Start-Process -FilePath "python" -ArgumentList "-m pip install -r `"$INSTALL_DIR\requirements.txt`"" -Wait -NoNewWindow -PassThru
    if ($pipProcess.ExitCode -ne 0) {
        Write-Host "WARNING: Some dependencies may not have installed correctly." -ForegroundColor Yellow
        Write-Host "You may need to run: pip install -r `"$INSTALL_DIR\requirements.txt`"" -ForegroundColor Yellow
    } else {
        Write-Host "Dependencies installed successfully." -ForegroundColor Green
    }
} catch {
    Write-Host "WARNING: Could not install dependencies." -ForegroundColor Yellow
    Write-Host "You may need to run: pip install -r `"$INSTALL_DIR\requirements.txt`"" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "self installed successfully." -ForegroundColor Cyan
Write-Host "installation location: $INSTALL_DIR" -ForegroundColor Cyan
Write-Host "you may need to restart your terminal or computer for the PATH changes to take effect." -ForegroundColor Yellow
Write-Host "close this window, open a new terminal and type 'self'." -ForegroundColor Cyan
Write-Host "to run the setup, type 'self --setup'" -ForegroundColor Cyan
Write-Host ""
Write-Host "To update in the future, run 'self --update'" -ForegroundColor Cyan 