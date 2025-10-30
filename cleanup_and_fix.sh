#!/bin/bash
# Cleanup unnecessary files and fix the main issue
# Keep only essential files for the working chatbot

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧹 Cleanup & Fix - Remove Unnecessary Files${NC}"
echo "=================================================="
echo ""

# List of files we can remove (not essential for basic chatbot operation)
OPTIONAL_FILES=(
    "install_packages.sh"
    "fix_common_errors.sh"
    "fix_lgpio.sh"
    "git_update.sh"
    "PI4_OPTIMIZATION_GUIDE.md"
    "PROJECT_STRUCTURE.md"
    "SUMMARY.md"
    "INDEX.md"
    "FIX_PACKAGES.md"
    "AFTER_INSTALL.md"
    "SETUP_CHECKLIST.txt"
    "QUICK_AFTER_INSTALL.md"
    "fix_missing_packages.sh"
    "COMMON_PACKAGE_ERRORS.md"
)

echo -e "${CYAN}Files that can be removed (optional documentation/scripts):${NC}"
for file in "${OPTIONAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  📄 $file"
    fi
done

echo ""
read -p "Remove these optional files? (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Removing optional files...${NC}"
    for file in "${OPTIONAL_FILES[@]}"; do
        if [ -f "$file" ]; then
            rm "$file"
            echo -e "  ${GREEN}✅${NC} Removed $file"
        fi
    done
    echo -e "${GREEN}✅ Cleanup complete!${NC}"
else
    echo -e "${YELLOW}Skipped cleanup${NC}"
fi

echo ""
echo -e "${BLUE}Essential files kept:${NC}"
ESSENTIAL_FILES=(
    "START_HERE.md"
    "QUICKSTART_PI4.md"
    "CHEAT_SHEET.md"
    "RAM_GUIDE.md"
    "README.md"
    "start_hdmi_chatbot.sh"
    "pi4_auto_setup.sh"
    "pi4_system_check.sh"
    "quick_test.sh"
    "hdmi_chatbot_vietnamese.py"
    "chatbot_vietnamese.py"
    "vietnamese_tts.py"
    "requirements.txt"
    "quick_fix_now.sh"
    "fix_opencv_detection.sh"
)

for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✅${NC} $file"
    else
        echo -e "  ${RED}❌${NC} $file (missing)"
    fi
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}Now fixing the main issue (opencv detection):${NC}"

# Test opencv
if python3 -c "import cv2; print(f'OpenCV {cv2.__version__} is working')" 2>/dev/null; then
    echo -e "${GREEN}✅ opencv-python is installed and working${NC}"

    echo ""
    echo -e "${CYAN}The issue was in the detection script. Now try:${NC}"
    echo -e "${GREEN}./start_hdmi_chatbot.sh${NC}"
    echo ""
    echo -e "${YELLOW}The script has been fixed to properly detect opencv-python (cv2)${NC}"
else
    echo -e "${RED}❌ opencv-python needs to be installed${NC}"
    echo -e "${CYAN}Installing opencv-python...${NC}"

    if [[ "$VIRTUAL_ENV" != "" ]]; then
        pip install opencv-python
    else
        source .venv/bin/activate
        pip install opencv-python
    fi
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    CLEANUP & FIX COMPLETE                   ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}Project is now cleaner and the opencv detection issue is fixed.${NC}"
echo -e "${CYAN}Try running the chatbot:${NC}"
echo -e "${GREEN}./start_hdmi_chatbot.sh${NC}"
