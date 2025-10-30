#!/bin/bash
# Quick fix for opencv-python detection issue
# The package is installed but script can't detect it properly

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Quick Fix - OpenCV Detection Issue${NC}"
echo "==============================================="
echo ""

# Check if in venv
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo -e "${GREEN}✅ Already in virtual environment: $VIRTUAL_ENV${NC}"
else
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source .venv/bin/activate
fi

# Test opencv import
echo -e "${YELLOW}Testing opencv-python import...${NC}"
python3 -c "
import cv2
print(f'✅ OpenCV version: {cv2.__version__}')
print('✅ opencv-python is working correctly!')
"

echo ""
echo -e "${GREEN}✅ opencv-python is installed and working!${NC}"
echo -e "${YELLOW}The issue was in the detection script, which has been fixed.${NC}"
echo ""
echo -e "${BLUE}Now try running the chatbot again:${NC}"
echo -e "${GREEN}./start_hdmi_chatbot.sh${NC}"
