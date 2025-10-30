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

# Check if we're in the right directory
if [ ! -f ".venv/bin/activate" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Please run this from ~/voice-chatbot directory"
    exit 1
fi

# Check if in venv
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo -e "${GREEN}✅ Already in virtual environment: $VIRTUAL_ENV${NC}"
else
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source .venv/bin/activate
    echo -e "${GREEN}✅ Activated: $VIRTUAL_ENV${NC}"
fi

# Test all critical imports
echo -e "${YELLOW}Testing critical packages...${NC}"
python3 -c "
packages = {
    'opencv-python': 'cv2',
    'faster-whisper': 'faster_whisper',
    'ollama': 'ollama',
    'gtts': 'gtts',
    'pygame': 'pygame'
}

missing = []
for pkg_name, import_name in packages.items():
    try:
        __import__(import_name)
        print(f'✅ {pkg_name} ({import_name})')
    except ImportError:
        print(f'❌ {pkg_name} ({import_name}) - MISSING')
        missing.append(pkg_name)

if missing:
    print(f'\\nMissing packages: {missing}')
    print('Run: pip install ' + ' '.join(missing))
    exit(1)
else:
    print('\\n✅ All packages are working correctly!')
"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ All packages installed and working!${NC}"
    echo -e "${YELLOW}The detection script has been fixed.${NC}"
    echo ""
    echo -e "${BLUE}Try these options:${NC}"
    echo -e "  1. ${GREEN}./start_hdmi_chatbot.sh${NC} (full script)"
    echo -e "  2. ${GREEN}./simple_start.sh${NC} (simple launcher)"
else
    echo ""
    echo -e "${RED}❌ Some packages are missing. Install them first.${NC}"
fi
