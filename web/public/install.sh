#!/bin/bash

# Colors
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
    echo -e "${GREEN}Cloning repository...${NC}"
    git clone https://github.com/smammadov94/job-weasel.git "$INSTALL_DIR"
fi

cd "$INSTALL_DIR/job-weasel-agent"

# Setup Venv
echo -e "${GREEN}Setting up virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install Dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install -r requirements.txt
pip install loguru python-dotenv rich playwright google-genai browserbase termcolor

# Install Playwright Browsers
echo -e "${GREEN}Installing browsers...${NC}"
playwright install chromium

# Create Alias
SHELL_CONFIG=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
fi

if [ ! -z "$SHELL_CONFIG" ]; then
    if ! grep -q "alias weaszel=" "$SHELL_CONFIG"; then
        echo -e "${GREEN}Adding 'weaszel' alias to $SHELL_CONFIG...${NC}"
        echo "alias weaszel='cd $INSTALL_DIR/job-weasel-agent && source venv/bin/activate && python weasel.py'" >> "$SHELL_CONFIG"
    fi
fi

echo -e "\n${GREEN}✅ Installation Complete!${NC}"
echo -e "Restart your terminal or run 'source $SHELL_CONFIG'"
echo -e "Then type ${CYAN}weaszel${NC} to start your companion! 🦊"
