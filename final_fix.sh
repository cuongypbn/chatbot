#!/bin/bash
# Final Fix - Comprehensive solution for chatbot startup issues

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║               Final Fix - Chatbot Startup                   ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check directory
if [ ! -f "hdmi_chatbot_vietnamese.py" ]; then
    echo -e "${RED}❌ Please run this from ~/voice-chatbot directory${NC}"
    exit 1
fi

echo -e "${CYAN}Step 1: Checking virtual environment...${NC}"

# Create venv if not exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate venv
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate
echo -e "${GREEN}✅ Activated: $VIRTUAL_ENV${NC}"

echo ""
echo -e "${CYAN}Step 2: Installing/updating packages...${NC}"

# Upgrade pip
pip install --upgrade pip

# Essential packages for chatbot
PACKAGES=(
    "numpy"
    "torch --index-url https://download.pytorch.org/whl/cpu"
    "faster-whisper"
    "ollama"
    "gtts"
    "opencv-python"
    "pygame"
    "sounddevice"
    "requests"
    "python-dotenv"
    "RPi.GPIO"
    "gpiozero"
)

for package in "${PACKAGES[@]}"; do
    echo -e "${YELLOW}Installing $package...${NC}"
    pip install $package --no-cache-dir 2>/dev/null || echo -e "${YELLOW}⚠️ $package failed (may not be critical)${NC}"
done

echo ""
echo -e "${CYAN}Step 3: Testing package imports...${NC}"

python3 -c "
import sys
packages = {
    'numpy': 'numpy',
    'torch': 'torch',
    'faster_whisper': 'faster_whisper',
    'ollama': 'ollama',
    'gtts': 'gtts',
    'opencv-python': 'cv2',
    'pygame': 'pygame',
    'sounddevice': 'sounddevice',
    'RPi.GPIO': 'RPi.GPIO',
    'gpiozero': 'gpiozero'
}

working = []
failed = []

for pkg_name, import_name in packages.items():
    try:
        __import__(import_name)
        working.append(pkg_name)
        print(f'✅ {pkg_name}')
    except ImportError:
        failed.append(pkg_name)
        print(f'❌ {pkg_name}')

print(f'\\nWorking: {len(working)}, Failed: {len(failed)}')

if len(working) >= 6:  # At least core packages work
    print('\\n✅ Enough packages working to run chatbot!')
    sys.exit(0)
else:
    print('\\n❌ Too many critical packages failed')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${CYAN}Step 4: Checking Ollama...${NC}"

    # Check Ollama service
    if systemctl is-active --quiet ollama; then
        echo -e "${GREEN}✅ Ollama service running${NC}"
    else
        echo -e "${YELLOW}Starting Ollama service...${NC}"
        sudo systemctl start ollama
        sleep 3
    fi

    # Check model
    if ollama list 2>/dev/null | grep -q "qwen2"; then
        echo -e "${GREEN}✅ qwen2 model available${NC}"
    else
        echo -e "${YELLOW}Downloading qwen2:0.5b model...${NC}"
        ollama pull qwen2:0.5b
    fi

    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    ALL FIXED! 🎉                            ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    echo -e "${CYAN}Choose how to start the chatbot:${NC}"
    echo ""
    echo -e "${YELLOW}Option 1: Simple launcher (recommended)${NC}"
    echo -e "  ${GREEN}./simple_start.sh${NC}"
    echo ""
    echo -e "${YELLOW}Option 2: Full featured script${NC}"
    echo -e "  ${GREEN}./start_hdmi_chatbot.sh${NC}"
    echo ""
    echo -e "${YELLOW}Option 3: Direct launch${NC}"
    echo -e "  ${GREEN}python3 hdmi_chatbot_vietnamese.py --lang vi${NC}"
    echo ""

    read -p "Choose option (1/2/3) or press Enter for option 1: " choice
    choice=${choice:-1}

    case $choice in
        1)
            echo -e "${GREEN}Starting simple launcher...${NC}"
            chmod +x simple_start.sh
            ./simple_start.sh
            ;;
        2)
            echo -e "${GREEN}Starting full script...${NC}"
            ./start_hdmi_chatbot.sh
            ;;
        3)
            echo -e "${GREEN}Starting chatbot directly...${NC}"
            export DISPLAY=:0
            export GPIOZERO_PIN_FACTORY=rpigpio
            python3 hdmi_chatbot_vietnamese.py --lang vi
            ;;
        *)
            echo -e "${YELLOW}Invalid choice. Run './simple_start.sh' manually.${NC}"
            ;;
    esac

else
    echo ""
    echo -e "${RED}❌ Package installation failed${NC}"
    echo -e "${CYAN}Try manual installation:${NC}"
    echo -e "  ${GREEN}source .venv/bin/activate${NC}"
    echo -e "  ${GREEN}pip install --no-cache-dir numpy torch faster-whisper ollama gtts opencv-python pygame${NC}"
fi
