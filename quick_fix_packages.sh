#!/bin/bash
# Quick fix for package installation errors
# Chạy script này nếu gặp lỗi libatlas-base-dev hoặc packages khác

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Quick Fix - Package Installation Errors                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}Fixing common package issues...${NC}"
echo ""

# Update package list
echo -e "${YELLOW}1/5${NC} Updating package list..."
sudo apt update -qq

# Remove problematic packages from list
echo -e "${YELLOW}2/5${NC} Installing core packages..."
sudo apt install -y \
  build-essential \
  cmake \
  git \
  python3-dev \
  python3-pip \
  python3-venv 2>/dev/null || echo "Some packages skipped"

# Install math libraries (alternatives to libatlas-base-dev)
echo -e "${YELLOW}3/5${NC} Installing math libraries (replacing libatlas-base-dev)..."
sudo apt install -y \
  libopenblas-dev \
  libblas-dev \
  liblapack-dev \
  gfortran 2>/dev/null || echo "Some packages skipped"

# Install audio packages
echo -e "${YELLOW}4/5${NC} Installing audio packages..."
sudo apt install -y \
  libportaudio2 \
  portaudio19-dev \
  ffmpeg \
  libsndfile1 \
  flac \
  alsa-utils \
  pipewire \
  pipewire-pulse \
  wireplumber 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Some audio packages not available, trying alternatives...${NC}"
    sudo apt install -y \
      libportaudio2 \
      ffmpeg \
      alsa-utils 2>/dev/null || echo "Minimal audio packages installed"
  }

# Install TTS and other tools
echo -e "${YELLOW}5/5${NC} Installing TTS and utilities..."
sudo apt install -y \
  bluez \
  espeak-ng \
  fonts-noto-cjk \
  fonts-noto-cjk-extra \
  fonts-dejavu 2>/dev/null || echo "Some packages skipped"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Fix Complete!                           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verify critical packages
echo -e "${CYAN}Verifying critical packages:${NC}"
PASS=0
FAIL=0

check_pkg() {
    if dpkg -l 2>/dev/null | grep -q "^ii.*$1"; then
        echo -e "  ${GREEN}✅${NC} $1"
        ((PASS++))
    else
        echo -e "  ${YELLOW}⚠️${NC}  $1 (not installed, but may not be critical)"
        ((FAIL++))
    fi
}

check_pkg "python3-dev"
check_pkg "python3-pip"
check_pkg "libopenblas-dev"
check_pkg "ffmpeg"
check_pkg "alsa-utils"

echo ""
if [ $PASS -ge 3 ]; then
    echo -e "${GREEN}✅ Enough packages installed to continue!${NC}"
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo -e "  1. Continue with setup: ${GREEN}./pi4_auto_setup.sh${NC}"
    echo -e "  2. Or skip to Python packages: ${GREEN}source .venv/bin/activate && pip install -r requirements.txt${NC}"
else
    echo -e "${YELLOW}⚠️  Some packages missing, but you can try to continue${NC}"
    echo ""
    echo -e "${CYAN}Alternative:${NC}"
    echo -e "  Install Python packages without system dependencies:"
    echo -e "  ${GREEN}python3 -m venv .venv${NC}"
    echo -e "  ${GREEN}source .venv/bin/activate${NC}"
    echo -e "  ${GREEN}pip install numpy --no-binary numpy${NC}"
    echo -e "  ${GREEN}pip install -r requirements.txt${NC}"
fi

echo ""

