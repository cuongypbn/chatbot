#!/bin/bash
# Quick Fix - Install missing ollama package and run chatbot

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🔧 Quick Fix - Installing missing ollama package${NC}"
echo "=================================================="
echo ""

# Ensure we're in the right directory
if [ ! -f "hdmi_chatbot_vietnamese.py" ]; then
    echo -e "${RED}❌ Please run this from ~/voice-chatbot directory${NC}"
    exit 1
fi

# Use explicit venv paths to avoid externally-managed-environment error
VENV_PYTHON="$(pwd)/.venv/bin/python3"
VENV_PIP="$(pwd)/.venv/bin/pip"

if [ ! -f "$VENV_PYTHON" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo -e "${GREEN}✅ Using venv: $VENV_PYTHON${NC}"
$VENV_PYTHON -c "
echo -e "${YELLOW}Installing missing ollama Python package...${NC}"
$VENV_PIP install ollama

echo -e "${YELLOW}Installing other essential packages...${NC}"
$VENV_PIP install faster-whisper gtts opencv-python pygame sounddevice requests python-dotenv

# Try to install GPIO packages (may fail on some systems)
$VENV_PIP install RPi.GPIO gpiozero 2>/dev/null || echo -e "${YELLOW}⚠️ GPIO packages failed (not critical)${NC}"

echo ""
echo -e "${GREEN}✅ Packages installed! Testing imports...${NC}"

python3 -c "
try:
    import ollama
    print('✅ ollama package imported successfully')

    import faster_whisper
    print('✅ faster_whisper imported')

    import gtts
    print('✅ gtts imported')

    import cv2
    print('✅ opencv-python (cv2) imported')

    import pygame
    print('✅ pygame imported')

    print('\\n🎉 All critical packages working!')

except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

    # Run the chatbot using explicit venv python
    $VENV_PYTHON hdmi_chatbot_vietnamese.py --lang vi
    echo -e "${GREEN}🚀 Ready to start chatbot!${NC}"
    echo ""

    # Set environment variables
    export DISPLAY=:0
    export GPIOZERO_PIN_FACTORY=rpigpio

    echo -e "${BLUE}Starting Vietnamese Voice Chatbot...${NC}"
    echo -e "${YELLOW}Say 'Xin chào Tiến Minh' to start conversation${NC}"
    echo ""

    # Run the chatbot
    python3 hdmi_chatbot_vietnamese.py --lang vi

else
    echo -e "${RED}❌ Package import failed. Try manual installation:${NC}"
    echo -e "   pip install ollama faster-whisper gtts opencv-python pygame"
fi
