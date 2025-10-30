#!/bin/bash
# Vietnamese Voice Chatbot Startup Script for Raspberry Pi 4
# Place this script in /home/pi/voice-chatbot/start_vietnamese_chatbot.sh
# Make executable: chmod +x start_vietnamese_chatbot.sh

set -e

# Configuration
PROJECT_DIR="$HOME/voice-chatbot"
VENV_DIR="$PROJECT_DIR/.venv"
CHATBOT_SCRIPT="chatbot_vietnamese.py"
LOG_FILE="$PROJECT_DIR/chatbot.log"
LANGUAGE="vi"  # vi, en, or auto

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Vietnamese Voice Chatbot for Raspberry Pi 4${NC}"

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ Project directory not found: $PROJECT_DIR${NC}"
    exit 1
fi

cd "$PROJECT_DIR"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}❌ Virtual environment not found: $VENV_DIR${NC}"
    echo -e "${YELLOW}Please run the setup first following the README.md${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}📦 Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

# Check if Ollama is running
echo -e "${YELLOW}🔍 Checking Ollama service...${NC}"
if ! systemctl --user is-active --quiet ollama 2>/dev/null && ! sudo systemctl is-active --quiet ollama 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Starting Ollama service...${NC}"
    sudo systemctl start ollama
    sleep 3
fi

# Check if models are available
echo -e "${YELLOW}🧠 Checking AI models...${NC}"
if ! ollama list | grep -q "qwen2:0.5b"; then
    echo -e "${YELLOW}📥 Downloading qwen2:0.5b model...${NC}"
    ollama pull qwen2:0.5b
fi

if ! ollama list | grep -q "tinyllama"; then
    echo -e "${YELLOW}📥 Downloading tinyllama fallback model...${NC}"
    ollama pull tinyllama:1.1b
fi

# Check audio setup
echo -e "${YELLOW}🔊 Checking audio setup...${NC}"
if ! command -v wpctl &> /dev/null; then
    echo -e "${RED}❌ PipeWire not found. Please install pipewire and wireplumber${NC}"
    exit 1
fi

# Auto-detect microphone
MIC_SOURCE_ID=$(wpctl status | grep -A 20 "Audio" | grep "Sources:" -A 20 | grep -E "(USB|Microphone)" | head -1 | grep -oE '[0-9]+' | head -1)
if [ -z "$MIC_SOURCE_ID" ]; then
    echo -e "${YELLOW}⚠️  No USB microphone detected, using default source${NC}"
    MIC_SOURCE_ID=""
else
    echo -e "${GREEN}✅ Found microphone source ID: $MIC_SOURCE_ID${NC}"
fi

# Check if chatbot script exists
if [ ! -f "$CHATBOT_SCRIPT" ]; then
    echo -e "${RED}❌ Chatbot script not found: $CHATBOT_SCRIPT${NC}"
    echo -e "${YELLOW}Available scripts:${NC}"
    ls -la *.py 2>/dev/null || echo "No Python scripts found"
    exit 1
fi

# Create log file if it doesn't exist
touch "$LOG_FILE"

echo -e "${GREEN}✅ All checks passed!${NC}"
echo -e "${BLUE}🎤 Starting Vietnamese Voice Chatbot...${NC}"
echo -e "${YELLOW}Language: $LANGUAGE${NC}"
if [ -n "$MIC_SOURCE_ID" ]; then
    echo -e "${YELLOW}Microphone: Source ID $MIC_SOURCE_ID${NC}"
else
    echo -e "${YELLOW}Microphone: Default source${NC}"
fi
echo -e "${YELLOW}Log file: $LOG_FILE${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo

# Function to handle cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Stopping chatbot...${NC}"
    echo -e "${BLUE}👋 Goodbye!${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start the chatbot
if [ -n "$MIC_SOURCE_ID" ]; then
    export MIC_TARGET="$MIC_SOURCE_ID"
fi

# Run with error handling
set +e
if [ -n "$MIC_SOURCE_ID" ]; then
    MIC_TARGET="$MIC_SOURCE_ID" python3 "$CHATBOT_SCRIPT" --lang "$LANGUAGE" 2>&1 | tee -a "$LOG_FILE"
else
    python3 "$CHATBOT_SCRIPT" --lang "$LANGUAGE" 2>&1 | tee -a "$LOG_FILE"
fi

exit_code=$?
set -e

if [ $exit_code -ne 0 ]; then
    echo -e "${RED}❌ Chatbot exited with error code: $exit_code${NC}"
    echo -e "${YELLOW}Check the log file: $LOG_FILE${NC}"
    exit $exit_code
fi

cleanup