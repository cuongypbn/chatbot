#!/bin/bash
# Simple Fix - Just activate venv and run chatbot
# This bypasses all the complex checks

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Simple Chatbot Launcher${NC}"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "hdmi_chatbot_vietnamese.py" ]; then
    echo -e "${RED}❌ Please run this from ~/voice-chatbot directory${NC}"
    echo "cd ~/voice-chatbot"
    exit 1
fi

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source .venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment activated: $VIRTUAL_ENV${NC}"
else
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Run: python3 -m venv .venv"
    exit 1
fi

# Quick package check
echo -e "${YELLOW}Quick package check...${NC}"
python3 -c "
import sys
try:
    import cv2, faster_whisper, ollama, gtts, pygame
    print('✅ All packages available')
except ImportError as e:
    print(f'❌ Missing package: {e}')
    print('Run: pip install faster-whisper ollama gtts opencv-python pygame')
    sys.exit(1)
"

# Check if the check passed
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}Installing missing packages...${NC}"
    pip install faster-whisper ollama gtts opencv-python pygame sounddevice requests python-dotenv
fi

# Set display
export DISPLAY=:0
export GPIOZERO_PIN_FACTORY=rpigpio

echo ""
echo -e "${GREEN}🚀 Starting Vietnamese Voice Chatbot...${NC}"
echo -e "${YELLOW}Language: Vietnamese (vi)${NC}"
echo ""

# Run the chatbot directly
python3 hdmi_chatbot_vietnamese.py --lang vi

echo ""
echo -e "${GREEN}Chatbot stopped.${NC}"
