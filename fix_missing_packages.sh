#!/bin/bash
# Fix Missing Python Packages
# Run this script if you get "Missing packages" error when starting chatbot

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Fix Missing Python Packages                             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if in correct directory
if [ ! -f "start_hdmi_chatbot.sh" ]; then
    echo -e "${RED}❌ Not in voice-chatbot directory!${NC}"
    echo "Please run: cd ~/voice-chatbot"
    exit 1
fi

echo -e "${CYAN}The error you encountered means Python packages are missing.${NC}"
echo -e "${CYAN}This usually happens if the auto-setup didn't complete properly.${NC}"
echo ""

# Check for virtual environment
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${CYAN}Activating virtual environment...${NC}"
source .venv/bin/activate

# Upgrade pip first
echo -e "${CYAN}Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel

# Install system dependencies first (if not already installed)
echo -e "${CYAN}Checking system dependencies...${NC}"
if ! dpkg -l | grep -q swig; then
    echo -e "${YELLOW}Installing missing system dependencies...${NC}"
    sudo apt update
    sudo apt install -y swig build-essential python3-dev libffi-dev pkg-config libopenblas-dev
fi

# List of required packages
PACKAGES=(
    "numpy"
    "torch"
    "torchaudio --index-url https://download.pytorch.org/whl/cpu"
    "faster-whisper"
    "openai-whisper"
    "soundfile"
    "librosa"
    "ollama"
    "gtts"
    "gTTS-token"
    "edge-tts"
    "pyttsx3"
    "pyaudio"
    "pygame"
    "sounddevice"
    "pydub"
    "Pillow"
    "opencv-python"
    "requests"
    "python-dotenv"
)

# Install packages with progress
total=${#PACKAGES[@]}
current=0

echo -e "${CYAN}Installing ${total} Python packages...${NC}"
echo ""

for package in "${PACKAGES[@]}"; do
    ((current++))
    echo -e "${YELLOW}[$current/$total]${NC} Installing $package..."

    if pip install $package --no-cache-dir 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} $package installed"
    else
        echo -e "  ${YELLOW}⚠️${NC}  $package failed (may not be critical)"
    fi
done

# Install GPIO packages (with fallback)
echo -e "\n${CYAN}Installing GPIO packages...${NC}"
pip install RPi.GPIO gpiozero 2>/dev/null || echo -e "${YELLOW}⚠️  Some GPIO packages failed${NC}"

# Try lgpio with system fallback
if ! python3 -c "import lgpio" 2>/dev/null; then
    if pip install lgpio --no-cache-dir 2>/dev/null; then
        echo -e "${GREEN}✅${NC} lgpio installed"
    else
        echo -e "${YELLOW}⚠️${NC}  lgpio failed to build (trying system package)"
        sudo apt install -y python3-lgpio 2>/dev/null || echo -e "${YELLOW}⚠️${NC}  lgpio not available"
    fi
else
    echo -e "${GREEN}✅${NC} lgpio already available"
fi

pip install spidev 2>/dev/null || echo -e "${YELLOW}⚠️${NC}  spidev failed"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}Verification:${NC}"

# Test critical imports
CRITICAL_PACKAGES=("numpy" "torch" "faster_whisper" "ollama" "gtts" "pygame")
PASS=0
FAIL=0

for pkg in "${CRITICAL_PACKAGES[@]}"; do
    if python3 -c "import $pkg" 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} $pkg"
        ((PASS++))
    else
        echo -e "  ${RED}❌${NC} $pkg"
        ((FAIL++))
    fi
done

echo ""
if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 All critical packages installed successfully!${NC}"
    SUCCESS=true
elif [ $PASS -ge 4 ]; then
    echo -e "${YELLOW}⚠️  Some packages failed, but enough are installed to try running${NC}"
    SUCCESS=true
else
    echo -e "${RED}❌ Too many critical packages failed${NC}"
    SUCCESS=false
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                Package Installation Complete               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$SUCCESS" = true ]; then
    echo -e "${CYAN}Next steps:${NC}"
    echo -e "  1. Make sure Ollama model is installed:"
    echo -e "     ${GREEN}ollama pull qwen2:0.5b${NC}"
    echo ""
    echo -e "  2. Test the chatbot:"
    echo -e "     ${GREEN}./start_hdmi_chatbot.sh${NC}"
    echo ""
    echo -e "  3. If still issues, run system check:"
    echo -e "     ${GREEN}./quick_test.sh${NC}"
else
    echo -e "${CYAN}Troubleshooting:${NC}"
    echo -e "  1. Try installing manually:"
    echo -e "     ${GREEN}source .venv/bin/activate${NC}"
    echo -e "     ${GREEN}pip install --no-cache-dir numpy torch faster-whisper ollama gtts pygame${NC}"
    echo ""
    echo -e "  2. Check system dependencies:"
    echo -e "     ${GREEN}sudo apt install -y python3-dev build-essential${NC}"
    echo ""
    echo -e "  3. Use lighter requirements:"
    echo -e "     ${GREEN}pip install --no-binary numpy numpy${NC}"
fi

echo ""
echo -e "${YELLOW}Note:${NC} Keep the terminal open to maintain the virtual environment."
echo -e "To activate again later: ${GREEN}source ~/voice-chatbot/.venv/bin/activate${NC}"
echo ""
