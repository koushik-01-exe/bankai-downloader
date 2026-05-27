#!/data/data/com.termux/files/usr/bin/bash
set -e

CYAN='\033[1;36m'
GREEN='\033[1;32m'
RED='\033[1;31m'
NC='\033[0m'

echo ""
echo -e "${CYAN}  ⚡ Installing Bankai Downloader...${NC}"
echo ""

# Step 0: Grant storage permission (needed for /storage/emulated/0/Download)
echo -e "${CYAN}  [0/4] Granting storage permission...${NC}"
termux-setup-storage -y 2>/dev/null

# Step 1: System dependencies
echo -e "${CYAN}  [1/4] Installing system dependencies...${NC}"
pkg install -y python ffmpeg git || { echo -e "${RED}  ✗ Failed to install system dependencies.${NC}"; exit 1; }

# Step 2: Python packages
echo -e "${CYAN}  [2/4] Installing Python packages...${NC}"
pip install -r requirements.txt || { echo -e "${RED}  ✗ Failed to install Python packages.${NC}"; exit 1; }

# Step 3: Install to $PREFIX/bin
echo -e "${CYAN}  [3/4] Setting up 'bankai' command...${NC}"
cp bankai_downloader.py "$PREFIX/bin/bankai" || { echo -e "${RED}  ✗ Failed to copy file.${NC}"; exit 1; }
chmod +x "$PREFIX/bin/bankai" || { echo -e "${RED}  ✗ Failed to set permissions.${NC}"; exit 1; }

echo -e "${RED}Deleting Base Files For Clean Look${NC}"
rm -rf /data/data/com.termux/files/home/bankai-downloader

echo ""
echo -e "${GREEN}  ✓ Done! Type 'bankai' anywhere to launch.${NC}"
echo ""
