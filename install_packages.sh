#!/bin/bash
# Pi OS Package Compatibility Checker
# Kiểm tra và cài đặt packages phù hợp với Pi OS version

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Pi OS Package Compatibility Checker                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Detect Pi OS version
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo -e "${GREEN}OS:${NC} $PRETTY_NAME"
    echo -e "${GREEN}Version:${NC} $VERSION"
    echo ""
fi

# Function to check if package exists
package_exists() {
    apt-cache show "$1" > /dev/null 2>&1
}

# Function to install package or alternative
install_package_or_alt() {
    local primary="$1"
    shift
    local alternatives=("$@")

    if package_exists "$primary"; then
        echo -e "${GREEN}✅${NC} Installing $primary"
        sudo apt install -y "$primary"
        return 0
    else
        echo -e "${YELLOW}⚠️${NC}  Package $primary not available"

        for alt in "${alternatives[@]}"; do
            if package_exists "$alt"; then
                echo -e "${GREEN}✅${NC} Installing alternative: $alt"
                sudo apt install -y "$alt"
                return 0
            fi
        done

        echo -e "${RED}❌${NC} No alternatives found for $primary"
        return 1
    fi
}

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}Installing Core Packages${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Update package list
echo -e "${CYAN}Updating package list...${NC}"
sudo apt update

# Core build tools (always needed)
echo -e "\n${CYAN}Core build tools:${NC}"
sudo apt install -y \
    build-essential \
    cmake \
    git \
    pkg-config

# Python development
echo -e "\n${CYAN}Python development:${NC}"
sudo apt install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-setuptools \
    python3-wheel

# Math libraries (with alternatives)
echo -e "\n${CYAN}Math libraries:${NC}"
install_package_or_alt "libatlas-base-dev" "libopenblas-dev" "libblas-dev"
install_package_or_alt "libopenblas-dev" "libblas-dev"
install_package_or_alt "libblas-dev"
install_package_or_alt "liblapack-dev"
install_package_or_alt "gfortran"

# HDF5 libraries
echo -e "\n${CYAN}HDF5 libraries:${NC}"
install_package_or_alt "libhdf5-dev"
install_package_or_alt "libhdf5-serial-dev" "libhdf5-dev"

# Audio libraries
echo -e "\n${CYAN}Audio libraries:${NC}"
install_package_or_alt "libportaudio2"
install_package_or_alt "libportaudiocpp0" "libportaudio2"
install_package_or_alt "portaudio19-dev"
install_package_or_alt "libsndfile1-dev" "libsndfile1"
install_package_or_alt "libsndfile1"

# Video/Audio codecs
echo -e "\n${CYAN}Codecs:${NC}"
install_package_or_alt "ffmpeg"
install_package_or_alt "libavcodec-extra" "libavcodec-dev" "ffmpeg"
install_package_or_alt "flac"

# Audio system
echo -e "\n${CYAN}Audio system:${NC}"
install_package_or_alt "pipewire" "pulseaudio"
install_package_or_alt "pipewire-pulse" "pulseaudio"
install_package_or_alt "wireplumber" "pipewire"
install_package_or_alt "libspa-0.2-bluetooth" "pipewire-audio-client-libraries"
install_package_or_alt "alsa-utils"

# Bluetooth
echo -e "\n${CYAN}Bluetooth:${NC}"
install_package_or_alt "bluez"
install_package_or_alt "bluez-tools" "bluez"
install_package_or_alt "pi-bluetooth" "bluez"

# TTS engines
echo -e "\n${CYAN}TTS engines:${NC}"
install_package_or_alt "espeak-ng"
install_package_or_alt "espeak-ng-data" "espeak-ng"
install_package_or_alt "festival"
install_package_or_alt "festvox-us-slt-hts" "festival"

# Fonts
echo -e "\n${CYAN}Fonts:${NC}"
install_package_or_alt "fonts-noto-cjk" "fonts-noto-core"
install_package_or_alt "fonts-dejavu"
install_package_or_alt "fonts-liberation" "fonts-dejavu"
install_package_or_alt "fonts-vlgothic" "fonts-noto-cjk"

# GUI libraries (if desktop is available)
if [ -n "$DISPLAY" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    echo -e "\n${CYAN}GUI libraries:${NC}"
    install_package_or_alt "python3-pygame" "python3-pip"
    install_package_or_alt "python3-opencv" "python3-pip"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Package Installation Complete!                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check what was installed
echo -e "${CYAN}Verifying installations:${NC}"

# Critical packages check
CRITICAL_PACKAGES=(
    "python3-dev"
    "python3-pip"
    "python3-venv"
    "ffmpeg"
    "alsa-utils"
    "bluez"
    "espeak-ng"
)

FAILED=0
for pkg in "${CRITICAL_PACKAGES[@]}"; do
    if dpkg -l | grep -q "^ii.*$pkg"; then
        echo -e "  ${GREEN}✅${NC} $pkg"
    else
        echo -e "  ${RED}❌${NC} $pkg (not critical, but recommended)"
        ((FAILED++))
    fi
done

echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All critical packages installed successfully!${NC}"
else
    echo -e "${YELLOW}⚠️  Some packages failed, but you can continue${NC}"
fi

echo ""
echo -e "${CYAN}Next steps:${NC}"
echo -e "  1. Continue with: ${GREEN}./pi4_auto_setup.sh${NC}"
echo -e "  2. Or manually install Python packages in venv"
echo ""

