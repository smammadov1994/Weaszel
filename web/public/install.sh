#!/bin/bash

# Colors
# Version 2.0
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}🦊 Weaszel 2.0 Installer${NC}"
echo "========================="

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3.12+ is required.${NC}"
    exit 1
fi

# Check for uv
if ! command -v uv &> /dev/null; then
    echo -e "${CYAN}Installing uv package manager...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Install Directory
INSTALL_DIR="$HOME/.weaszel"

if [ -d "$INSTALL_DIR" ]; then
    echo -e "${CYAN}Updating existing installation...${NC}"
    cd "$INSTALL_DIR" || exit 1

    # Always update from main so users don't get stuck on old feature branches
    git fetch origin

    # Ensure we're on main (create it if needed)
    if git rev-parse --verify main >/dev/null 2>&1; then
        git checkout main >/dev/null 2>&1
    else
        git checkout -b main origin/main >/dev/null 2>&1 || true
    fi

    # Pull latest changes from main explicitly (avoids tracking issues)
    git pull origin main || git pull
else
    # Clone the repo
    echo -e "${GREEN}Cloning repository...${NC}"
    git clone https://github.com/smammadov1994/Weaszel.git "$INSTALL_DIR"
fi

# Change into the root directory
cd "$INSTALL_DIR" || exit 1

# Install Dependencies with uv
echo -e "${GREEN}Installing dependencies with uv...${NC}"
uv sync

# Install Playwright Browsers
echo -e "${GREEN}Installing browsers...${NC}"
uv run playwright install chromium

# Create Alias
echo -e "${GREEN}Creating alias...${NC}"
SHELL_CONFIG="$HOME/.zshrc"
if [ -f "$HOME/.bashrc" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
fi

# Remove old alias if exists
sed -i '' '/alias weaszel/d' "$SHELL_CONFIG" 2>/dev/null || sed -i '/alias weaszel/d' "$SHELL_CONFIG"

# Add new alias
# Use full path to uv if possible, or assume it's in path
UV_BIN="$HOME/.cargo/bin/uv"
if [ -f "$UV_BIN" ]; then
    echo "alias weaszel='cd $INSTALL_DIR && $UV_BIN run python job-weasel-agent/weasel.py'" >> "$SHELL_CONFIG"
else
    echo "alias weaszel='cd $INSTALL_DIR && uv run python job-weasel-agent/weasel.py'" >> "$SHELL_CONFIG"
fi

echo -e "\n${GREEN}✅ Weaszel 2.0 Installation Complete!${NC}"
echo -e "Restart your terminal or run 'source $SHELL_CONFIG'"
echo -e "Then type ${CYAN}weaszel${NC} to start! 🦊"
echo -e "\n${CYAN}What's new in 2.0:${NC}"
echo -e "  ⚡ 3-5x faster with Browser-Use"
echo -e "  🧹 Simpler, cleaner codebase"
echo -e "  🛡️ Built-in retry logic"
