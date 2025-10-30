#!/bin/bash
# Fix script for common package errors on Pi OS
# Run this if you encounter package installation errors

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Common Package Errors - Auto Fix                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}Fixing known package issues for Raspberry Pi OS...${NC}"
echo ""

# Update first
echo -e "${YELLOW}Updating package list...${NC}"
sudo apt update -qq

# Fix 1: libatlas-base-dev → libopenblas-dev
echo -e "${CYAN}Fix 1: Installing math libraries (replacing libatlas-base-dev)${NC}"
sudo apt install -y libopenblas-dev libblas-dev liblapack-dev gfortran 2>/dev/null && \
    echo -e "${GREEN}✅${NC} Math libraries installed" || \
    echo -e "${YELLOW}⚠️${NC}  Some math packages skipped"

# Fix 2: language-pack-vi → fonts only (not needed on Pi OS)
echo -e "${CYAN}Fix 2: Installing Vietnamese fonts (language-pack-vi not needed)${NC}"
sudo apt install -y fonts-noto-cjk fonts-noto-cjk-extra fonts-dejavu fonts-liberation 2>/dev/null && \
    echo -e "${GREEN}✅${NC} Vietnamese fonts installed" || \
    echo -e "${YELLOW}⚠️${NC}  Some fonts skipped"

# Fix 3: Core packages
echo -e "${CYAN}Fix 3: Installing core packages${NC}"
sudo apt install -y \
    build-essential cmake git \
    python3-dev python3-pip python3-venv \
    swig libffi-dev pkg-config 2>/dev/null && \
    echo -e "${GREEN}✅${NC} Core packages installed" || \
    echo -e "${YELLOW}⚠️${NC}  Some core packages skipped"

# Fix 4: Audio packages
echo -e "${CYAN}Fix 4: Installing audio packages${NC}"
sudo apt install -y \
    libportaudio2 portaudio19-dev \
    ffmpeg libsndfile1 flac alsa-utils 2>/dev/null && \
    echo -e "${GREEN}✅${NC} Audio packages installed" || \
    echo -e "${YELLOW}⚠️${NC}  Some audio packages skipped"

# Fix 5: PipeWire
echo -e "${CYAN}Fix 5: Installing PipeWire audio system${NC}"
sudo apt install -y pipewire pipewire-pulse wireplumber 2>/dev/null && \
    echo -e "${GREEN}✅${NC} PipeWire installed" || \
    echo -e "${YELLOW}⚠️${NC}  PipeWire packages skipped (may already be installed)"

# Fix 6: Bluetooth
echo -e "${CYAN}Fix 6: Installing Bluetooth${NC}"
sudo apt install -y bluez bluez-tools 2>/dev/null && \
    echo -e "${GREEN}✅${NC} Bluetooth installed" || \
    echo -e "${YELLOW}⚠️${NC}  Bluetooth packages skipped"

# Fix 7: TTS engines
echo -e "${CYAN}Fix 7: Installing TTS engines${NC}"
sudo apt install -y espeak-ng festival 2>/dev/null && \
    echo -e "${GREEN}✅${NC} TTS engines installed" || \
    echo -e "${YELLOW}⚠️${NC}  Some TTS packages skipped"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Fix Complete!                           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verify
echo -e "${CYAN}Verification:${NC}"
dpkg -l | grep -q libopenblas && echo -e "  ${GREEN}✅${NC} libopenblas-dev" || echo -e "  ${YELLOW}⚠️${NC}  libopenblas-dev"
dpkg -l | grep -q "fonts-noto-cjk" && echo -e "  ${GREEN}✅${NC} Vietnamese fonts" || echo -e "  ${YELLOW}⚠️${NC}  Vietnamese fonts"
dpkg -l | grep -q python3-dev && echo -e "  ${GREEN}✅${NC} python3-dev" || echo -e "  ${YELLOW}⚠���${NC}  python3-dev"
dpkg -l | grep -q ffmpeg && echo -e "  ${GREEN}✅${NC} ffmpeg" || echo -e "  ${YELLOW}⚠️${NC}  ffmpeg"
dpkg -l | grep -q pipewire && echo -e "  ${GREEN}✅${NC} pipewire" || echo -e "  ${YELLOW}⚠️${NC}  pipewire"

echo ""
echo -e "${CYAN}Next steps:${NC}"
echo -e "  Continue with: ${GREEN}./pi4_auto_setup.sh${NC}"
echo ""

