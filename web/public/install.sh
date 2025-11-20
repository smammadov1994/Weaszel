#!/bin/bash

# Colors
# Version 1.1
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}🌰 Weaszel Installer${NC}"
echo "========================="

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    exit 1
fi

# Install Directory
INSTALL_DIR="$HOME/.weaszel"

if [ -d "$INSTALL_DIR" ]; then
    echo -e "${CYAN}Updating existing installation...${NC}"
    cd "$INSTALL_DIR"
    git pull
else
    # Clone the repo
    echo -e "${GREEN}Cloning repository...${NC}"
    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR"
    fi
    git clone https://github.com/smammadov1994/Weaszel.git "$INSTALL_DIR"
fi

# Change into the agent directory
cd "$INSTALL_DIR/job-weasel-agent" || exit 1

# Setup Virtual Environment
echo "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Dependencies
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "ERROR: requirements.txt not found in $(pwd)"
    exit 1
fi


# Install Playwright Browsers
echo -e "${GREEN}Installing browsers...${NC}"
playwright install chromium

# Create Alias
echo "Creating alias..."
SHELL_CONFIG="$HOME/.zshrc"
if [ -f "$HOME/.bashrc" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
fi

# Remove old alias if exists
sed -i '' '/alias weaszel/d' "$SHELL_CONFIG"

# Add new alias
echo "alias weaszel='source $INSTALL_DIR/job-weasel-agent/venv/bin/activate && python $INSTALL_DIR/job-weasel-agent/weasel.py'" >> "$SHELL_CONFIG"

echo -e "\n${GREEN}✅ Installation Complete!${NC}"
echo -e "Restart your terminal or run 'source $SHELL_CONFIG'"
echo -e "Then type ${CYAN}weaszel${NC} to start your companion! 🦊"
