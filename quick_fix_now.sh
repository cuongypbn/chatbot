#!/bin/bash
# Quick Fix for "Missing packages" error
# Run this if you get missing packages error when starting chatbot

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Quick Fix - Missing Packages Error${NC}"
echo "══════════════════════════════════════════════"
echo ""

# Check current directory
if [ ! -f "start_hdmi_chatbot.sh" ]; then
    echo -e "${RED}❌ Please run this from ~/voice-chatbot directory${NC}"
    echo "cd ~/voice-chatbot"
    exit 1
fi

echo -e "${CYAN}Your error: Missing packages ['faster_whisper', 'ollama', 'gtts', 'opencv-python']${NC}"
echo ""

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}1/3 Creating virtual environment...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
fi

# Activate venv
echo -e "${YELLOW}2/3 Activating virtual environment...${NC}"
source .venv/bin/activate
echo -e "Active Python: $(which python3)"
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Install missing packages
echo -e "${YELLOW}3/3 Installing missing packages...${NC}"
echo ""

# Essential packages first
pip install --upgrade pip

echo "Installing core packages..."
pip install numpy torch --index-url https://download.pytorch.org/whl/cpu

echo "Installing AI packages..."
pip install faster-whisper ollama

echo "Installing TTS packages..."
pip install gtts edge-tts

echo "Installing other packages..."
pip install opencv-python pygame sounddevice requests python-dotenv

echo "Installing GPIO packages..."
pip install RPi.GPIO gpiozero || echo "GPIO packages failed (not critical)"

echo ""
echo -e "${GREEN}✅ Package installation complete!${NC}"

# Test imports
echo -e "${CYAN}Testing imports...${NC}"
python3 -c "
import faster_whisper, ollama, gtts
import cv2 as opencv_python
print('✅ All critical packages imported successfully!')
"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                     FIX COMPLETE!                           ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}Next steps:${NC}"
echo -e "1. Make sure Ollama model is downloaded:"
echo -e "   ${GREEN}ollama pull qwen2:0.5b${NC}"
echo ""
echo -e "2. Try running the chatbot again:"
echo -e "   ${GREEN}./start_hdmi_chatbot.sh${NC}"
echo ""
echo -e "3. If still issues, check Ollama:"
echo -e "   ${GREEN}systemctl status ollama${NC}"

echo ""
echo -e "${YELLOW}Note: Keep this terminal open to maintain the virtual environment.${NC}"
