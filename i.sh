#!/bin/bash

# Self - Windows System Information Tool - Installation Script
VERSION="1.0.0"
INSTALL_DIR="$HOME/SelfTool"
REPO_URL="https://github.com/YOUR_USERNAME/YOUR_REPO_NAME"
RAW_URL="https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO_NAME/main"

echo "========================================================"
echo "Self - Windows System Information Tool - Installation"
echo "Version: $VERSION"
echo "========================================================"

# Check if running on Windows
if [[ "$(uname -s)" != MINGW* ]] && [[ "$(uname -s)" != CYGWIN* ]] && [[ "$(uname -s)" != MSYS* ]]; then
    echo "Error: This tool is designed for Windows systems only."
    exit 1
fi

# Create installation directory
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/ascii" "$INSTALL_DIR/config" "$INSTALL_DIR/images" "$INSTALL_DIR/cache"

# Download required files
echo "Downloading required files..."
FILES=("self.py" "win_sysinfo.py" "color_themes.py" "image_handler.py" "default_image.py" "requirements.txt")
for file in "${FILES[@]}"; do
    wget -q "$RAW_URL/$file" -O "$INSTALL_DIR/$file"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to download $file"
        exit 1
    fi
done

# Download directories
echo "Downloading additional resources..."
# Download ASCII files
wget -q "$RAW_URL/ascii/filelist.txt" -O "$INSTALL_DIR/ascii/filelist.txt"
if [ -f "$INSTALL_DIR/ascii/filelist.txt" ]; then
    while IFS= read -r ascii_file; do
        wget -q "$RAW_URL/ascii/$ascii_file" -O "$INSTALL_DIR/ascii/$ascii_file"
    done < "$INSTALL_DIR/ascii/filelist.txt"
fi

# Download config files
wget -q "$RAW_URL/config/filelist.txt" -O "$INSTALL_DIR/config/filelist.txt"
if [ -f "$INSTALL_DIR/config/filelist.txt" ]; then
    while IFS= read -r config_file; do
        wget -q "$RAW_URL/config/$config_file" -O "$INSTALL_DIR/config/$config_file"
    done < "$INSTALL_DIR/config/filelist.txt"
fi

# Download image files
wget -q "$RAW_URL/images/filelist.txt" -O "$INSTALL_DIR/images/filelist.txt"
if [ -f "$INSTALL_DIR/images/filelist.txt" ]; then
    while IFS= read -r image_file; do
        wget -q "$RAW_URL/images/$image_file" -O "$INSTALL_DIR/images/$image_file"
    done < "$INSTALL_DIR/images/filelist.txt"
fi

# Create batch file
echo "Creating launcher..."
cat > "$INSTALL_DIR/self.bat" << EOF
@echo off
python "$INSTALL_DIR/self.py" %*
EOF

# Add to PATH
echo "Adding to PATH..."
# Check if INSTALL_DIR is already in PATH
if [[ ";$PATH;" != *";$INSTALL_DIR;"* ]]; then
    # Use PowerShell to modify PATH in Windows registry
    powershell.exe -Command "
        \$path = [Environment]::GetEnvironmentVariable('PATH', 'User')
        if (\$path -notlike '*$INSTALL_DIR*') {
            [Environment]::SetEnvironmentVariable('PATH', \"\$path;$INSTALL_DIR\", 'User')
            echo 'Added to PATH successfully.'
        } else {
            echo 'Already in PATH.'
        }
    "
else
    echo "Already in PATH."
fi

# Install dependencies
echo "Installing dependencies..."
python -m pip install -r "$INSTALL_DIR/requirements.txt"

echo ""
echo "Installation completed!"
echo "The 'self' command has been installed to $INSTALL_DIR"
echo "You may need to restart your terminal or computer for the PATH changes to take effect."
echo "You can now use 'self' to show system information." 