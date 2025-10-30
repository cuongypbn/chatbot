#!/bin/bash
# Quick Test Script for Pi 4 Vietnamese Voice Chatbot
# Kiểm tra nhanh các thành phần chính

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Pi 4 Vietnamese Chatbot - Quick Test                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

PASS=0
FAIL=0

test_pass() {
    echo -e "${GREEN}✅${NC} $1"
    ((PASS++))
}

test_fail() {
    echo -e "${RED}❌${NC} $1"
    ((FAIL++))
}

test_warn() {
    echo -e "${YELLOW}⚠️${NC}  $1"
}

# Test 1: Check Pi 4
echo -e "${CYAN}Test 1: Checking Pi 4 Model...${NC}"
if grep -q "Raspberry Pi 4" /proc/cpuinfo 2>/dev/null; then
    test_pass "Raspberry Pi 4 detected"
else
    test_warn "Not detected as Pi 4 (may still work)"
fi

# Test 2: Check RAM
echo -e "\n${CYAN}Test 2: Checking RAM...${NC}"
TOTAL_RAM_MB=$(free -m | grep "Mem:" | awk '{print $2}')
if [ $TOTAL_RAM_MB -ge 7000 ]; then
    test_pass "8GB RAM detected - Excellent!"
elif [ $TOTAL_RAM_MB -ge 3500 ]; then
    test_pass "4GB RAM detected - Very Good!"
elif [ $TOTAL_RAM_MB -ge 1800 ]; then
    test_warn "2GB RAM detected - Will work with lighter models"
else
    test_fail "Less than 2GB RAM - May have issues"
fi

# Test 3: Check OS
echo -e "\n${CYAN}Test 3: Checking OS...${NC}"
if uname -m | grep -q "aarch64"; then
    test_pass "64-bit OS detected"
else
    test_warn "Not 64-bit OS (32-bit may work but not optimal)"
fi

# Test 4: Check Python
echo -e "\n${CYAN}Test 4: Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VER=$(python3 --version)
    test_pass "Python available: $PYTHON_VER"
else
    test_fail "Python3 not found"
fi

# Test 5: Check virtual environment
echo -e "\n${CYAN}Test 5: Checking Virtual Environment...${NC}"
if [ -d ".venv" ]; then
    test_pass "Virtual environment exists"

    # Activate and check packages
    source .venv/bin/activate

    # Test critical packages
    python3 -c "import numpy" 2>/dev/null && test_pass "NumPy installed" || test_fail "NumPy not installed"
    python3 -c "import torch" 2>/dev/null && test_pass "PyTorch installed" || test_fail "PyTorch not installed"
    python3 -c "from faster_whisper import WhisperModel" 2>/dev/null && test_pass "Faster-Whisper installed" || test_fail "Faster-Whisper not installed"
    python3 -c "import ollama" 2>/dev/null && test_pass "Ollama client installed" || test_fail "Ollama client not installed"
    python3 -c "from gtts import gTTS" 2>/dev/null && test_pass "gTTS installed" || test_fail "gTTS not installed"
    python3 -c "import pygame" 2>/dev/null && test_pass "Pygame installed" || test_fail "Pygame not installed"
    python3 -c "import cv2" 2>/dev/null && test_pass "OpenCV (cv2) installed" || test_fail "OpenCV not installed"
    python3 -c "import RPi.GPIO" 2>/dev/null && test_pass "RPi.GPIO installed" || test_fail "RPi.GPIO not installed"

else
    test_fail "Virtual environment not found"
    echo "   Run: python3 -m venv .venv"
fi

# Test 6: Check Ollama
echo -e "\n${CYAN}Test 6: Checking Ollama...${NC}"
if command -v ollama &> /dev/null; then
    test_pass "Ollama installed"

    if systemctl is-active --quiet ollama 2>/dev/null; then
        test_pass "Ollama service running"

        # Check available models
        if ollama list 2>/dev/null | grep -q "qwen2"; then
            test_pass "qwen2 model available"
        elif ollama list 2>/dev/null | grep -q "tinyllama"; then
            test_pass "tinyllama model available"
        elif ollama list 2>/dev/null | grep -q "gemma"; then
            test_pass "gemma model available"
        else
            test_warn "No recommended models found"
            echo "   Run: ollama pull qwen2:0.5b"
        fi
    else
        test_fail "Ollama service not running"
        echo "   Run: sudo systemctl start ollama"
    fi
else
    test_fail "Ollama not installed"
    echo "   Run: curl -fsSL https://ollama.com/install.sh | sh"
fi

# Test 7: Check Audio System
echo -e "\n${CYAN}Test 7: Checking Audio System...${NC}"
if systemctl --user is-active --quiet pipewire 2>/dev/null; then
    test_pass "PipeWire running"
else
    test_warn "PipeWire not running"
    echo "   Run: systemctl --user start pipewire pipewire-pulse wireplumber"
fi

if command -v wpctl &> /dev/null; then
    test_pass "wpctl (WirePlumber) available"

    # Count audio sources (microphones)
    SOURCE_COUNT=$(wpctl status 2>/dev/null | grep -A 20 "Audio/Source" | grep -c "vol:" || echo "0")
    if [ "$SOURCE_COUNT" -gt 0 ]; then
        test_pass "Found $SOURCE_COUNT audio source(s)"
    else
        test_warn "No audio sources found (microphone)"
    fi

    # Count audio sinks (speakers)
    SINK_COUNT=$(wpctl status 2>/dev/null | grep -A 20 "Audio/Sink" | grep -c "vol:" || echo "0")
    if [ "$SINK_COUNT" -gt 0 ]; then
        test_pass "Found $SINK_COUNT audio sink(s)"
    else
        test_warn "No audio sinks found (speaker)"
    fi
else
    test_fail "wpctl not found"
fi

# Test 8: Check Bluetooth
echo -e "\n${CYAN}Test 8: Checking Bluetooth...${NC}"
if systemctl is-active --quiet bluetooth 2>/dev/null; then
    test_pass "Bluetooth service running"
else
    test_warn "Bluetooth service not running"
    echo "   Run: sudo systemctl start bluetooth"
fi

if command -v bluetoothctl &> /dev/null; then
    test_pass "bluetoothctl available"
else
    test_fail "bluetoothctl not found"
fi

# Test 9: Check GPIO/SPI
echo -e "\n${CYAN}Test 9: Checking GPIO/SPI...${NC}"
if lsmod | grep -q spi_bcm2835; then
    test_pass "SPI kernel module loaded"
else
    test_warn "SPI not enabled (needed for LCD display only)"
fi

if [ -e /dev/spidev0.0 ]; then
    test_pass "SPI device available"
else
    test_warn "SPI device not found (needed for LCD display only)"
fi

if groups $USER | grep -q gpio; then
    test_pass "User in gpio group"
else
    test_fail "User not in gpio group"
    echo "   Run: sudo usermod -aG gpio $USER && sudo reboot"
fi

# Test 10: Check Display
echo -e "\n${CYAN}Test 10: Checking Display...${NC}"
if [ -n "$DISPLAY" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    test_pass "Display environment available (for HDMI GUI)"
else
    test_warn "No display environment (will use terminal-only mode)"
fi

# Test 11: Check TTS Engines
echo -e "\n${CYAN}Test 11: Checking TTS Engines...${NC}"
if command -v espeak-ng &> /dev/null; then
    test_pass "espeak-ng available (offline TTS)"
else
    test_warn "espeak-ng not found"
    echo "   Run: sudo apt install espeak-ng"
fi

# Test 12: Check Vietnamese Fonts
echo -e "\n${CYAN}Test 12: Checking Vietnamese Fonts...${NC}"
if fc-list :lang=vi 2>/dev/null | grep -q .; then
    test_pass "Vietnamese fonts available"
else
    test_warn "Vietnamese fonts not found"
    echo "   Run: sudo apt install fonts-noto-cjk"
fi

# Summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                     TEST SUMMARY                           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "   ${GREEN}Passed: $PASS${NC}"
echo -e "   ${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 All critical tests passed! You're ready to run the chatbot!${NC}"
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo -e "   1. Connect Bluetooth speaker (if not connected)"
    echo -e "   2. Plug in USB microphone"
    echo -e "   3. Run: ${GREEN}./start_hdmi_chatbot.sh${NC}"
    echo ""
elif [ $FAIL -lt 3 ]; then
    echo -e "${YELLOW}⚠️  Some tests failed, but you may still be able to run the chatbot${NC}"
    echo -e "   Review the failures above and fix if needed"
    echo ""
else
    echo -e "${RED}❌ Multiple critical tests failed. Please fix the issues above.${NC}"
    echo -e "   Run the auto-setup script: ${GREEN}./pi4_auto_setup.sh${NC}"
    echo ""
fi

exit $FAIL

