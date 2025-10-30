#!/bin/bash
# Startup script for HDMI Voice Chatbot Vietnamese
# Raspberry Pi 4 Model B 8GB RAM optimized

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHATBOT_SCRIPT="$SCRIPT_DIR/hdmi_chatbot_vietnamese.py"
LOG_FILE="$SCRIPT_DIR/logs/hdmi_chatbot.log"
PID_FILE="$SCRIPT_DIR/logs/hdmi_chatbot.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

echo -e "${BLUE}🖥️ Tiến Minh - Vietnamese HDMI Voice Chatbot Startup${NC}"
echo "================================================================"

# Function to log messages
log_message() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Check if already running
check_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠️ Chatbot is already running (PID: $pid)${NC}"
            echo "Use 'pkill -f hdmi_chatbot_vietnamese.py' to stop it first"
            exit 1
        else
            rm -f "$PID_FILE"
        fi
    fi
}

# System checks
check_system() {
    log_message "🔍 Performing system checks..."
    
    # Check if running on Pi 4
    if [ -f /sys/firmware/devicetree/base/model ]; then
        model=$(cat /sys/firmware/devicetree/base/model)
        log_message "📱 Hardware: $model"
        if [[ "$model" != *"Raspberry Pi 4"* ]]; then
            log_message "⚠️ Warning: Not running on Pi 4, some optimizations may not apply"
        fi
    fi
    
    # Check memory
    total_mem=$(free -h | awk '/^Mem:/ {print $2}')
    log_message "💾 Available RAM: $total_mem"
    
    # Check display
    if [ -n "$DISPLAY" ] || [ -n "$WAYLAND_DISPLAY" ]; then
        log_message "🖥️ Display environment detected"
    else
        log_message "⚠️ No display environment detected, setting DISPLAY=:0"
        export DISPLAY=:0
    fi
    
    # Check audio
    if command -v pw-cat > /dev/null; then
        log_message "🔊 PipeWire audio system detected"
    else
        log_message "❌ PipeWire not found - audio may not work"
    fi
    
    # Check Ollama
    if systemctl is-active --quiet ollama; then
        log_message "✅ Ollama service is running"
    else
        log_message "🚀 Starting Ollama service..."
        sudo systemctl start ollama || {
            log_message "❌ Failed to start Ollama"
            exit 1
        }
        sleep 3
    fi
    
    # Activate virtual environment BEFORE checking packages
    if [ -f ".venv/bin/activate" ]; then
        log_message "🐍 Activating Python virtual environment..."
        source .venv/bin/activate
        log_message "✅ Virtual environment activated: $VIRTUAL_ENV"
    else
        log_message "⚠️ No virtual environment found, using system Python"
    fi

    # Check Python packages
    log_message "🐍 Checking Python environment..."
    python3 -c "
import sys
import importlib.util

# Package mapping for imports
package_imports = {
    'numpy': 'numpy',
    'pygame': 'pygame',
    'faster_whisper': 'faster_whisper',
    'ollama': 'ollama',
    'gtts': 'gtts',
    'gpiozero': 'gpiozero',
    'opencv-python': 'cv2'  # opencv-python imports as cv2
}

missing = []
for package, import_name in package_imports.items():
    try:
        spec = importlib.util.find_spec(import_name)
        if spec is None:
            missing.append(package)
    except (ImportError, ModuleNotFoundError, ValueError):
        missing.append(package)

if missing:
    print(f'❌ Missing packages: {missing}')
    print('Run: pip install ' + ' '.join(missing))
    sys.exit(1)
else:
    print('✅ All required packages available')
" || {
        log_message "❌ Python package check failed"
        echo ""
        echo -e "${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║                    MISSING PACKAGES ERROR                   ║${NC}"
        echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${CYAN}The auto-setup didn't complete properly. Here's how to fix:${NC}"
        echo ""
        echo -e "${YELLOW}Option 1: Run the fix script (RECOMMENDED)${NC}"
        echo -e "  ${GREEN}chmod +x fix_missing_packages.sh${NC}"
        echo -e "  ${GREEN}./fix_missing_packages.sh${NC}"
        echo ""
        echo -e "${YELLOW}Option 2: Manual fix${NC}"
        echo -e "  ${GREEN}source .venv/bin/activate${NC}"
        echo -e "  ${GREEN}pip install faster-whisper ollama gtts opencv-python${NC}"
        echo ""
        echo -e "${YELLOW}Option 3: Re-run complete setup${NC}"
        echo -e "  ${GREEN}./pi4_auto_setup.sh${NC}"
        echo ""
        exit 1
    }
}

# Set environment variables for Pi 4 optimization
setup_environment() {
    log_message "⚙️ Setting up environment for Pi 4..."
    
    # GPIO library selection for Pi 4
    export GPIOZERO_PIN_FACTORY=rpigpio
    
    # Pygame optimization
    export SDL_AUDIODRIVER=pulse
    export SDL_VIDEODRIVER=x11
    
    # PipeWire optimization
    export PIPEWIRE_LATENCY="128/48000"
    
    # CPU optimization for Pi 4
    export OMP_NUM_THREADS=4
    export OPENBLAS_NUM_THREADS=2
    
    log_message "📊 Environment configured for Pi 4 optimization"
}

# Language selection
select_language() {
    if [ -z "$CHATBOT_LANG" ]; then
        echo -e "${BLUE}🌐 Select language / Chọn ngôn ngữ:${NC}"
        echo "1) Vietnamese (Tiếng Việt) - Default"
        echo "2) English"  
        echo "3) Auto-detect"
        echo
        read -p "Enter choice (1-3) [1]: " lang_choice
        
        case ${lang_choice:-1} in
            1) CHATBOT_LANG="vi" ;;
            2) CHATBOT_LANG="en" ;;
            3) CHATBOT_LANG="auto" ;;
            *) CHATBOT_LANG="vi" ;;
        esac
    fi
    
    log_message "🗣️ Language set to: $CHATBOT_LANG"
}

# Microphone selection
select_microphone() {
    if command -v pw-cli > /dev/null; then
        echo -e "${BLUE}🎤 Available microphones:${NC}"
        pw-cli ls Node | grep -A5 -B5 "input" | grep -E "(node.name|node.description)" | head -10
        echo
        read -p "Enter microphone target (or press Enter for default): " mic_target
        if [ -n "$mic_target" ]; then
            MIC_TARGET="--mic-target $mic_target"
            log_message "🎯 Microphone target: $mic_target"
        fi
    fi
}

# Start chatbot
start_chatbot() {
    log_message "🚀 Starting HDMI Vietnamese Voice Chatbot..."
    

    # Build command
    cmd="python3 '$CHATBOT_SCRIPT' --lang $CHATBOT_LANG $MIC_TARGET"
    log_message "📝 Command: $cmd"
    
    # Start in background and save PID
    eval "nohup $cmd > '$LOG_FILE' 2>&1 &"
    local pid=$!
    echo $pid > "$PID_FILE"
    
    log_message "✅ Chatbot started with PID: $pid"
    log_message "📋 Log file: $LOG_FILE"
    
    echo -e "${GREEN}================================================================${NC}"
    echo -e "${GREEN}🤖 Tiến Minh - HDMI Vietnamese Voice Chatbot is now running!${NC}"
    echo -e "${GREEN}================================================================${NC}"
    echo
    echo "📱 Display: Check your HDMI monitor for the GUI interface"
    echo "🎤 Microphone: USB microphone via PipeWire"
    echo "🔊 Audio: Bluetooth speakers or 3.5mm output"
    echo "📋 Logs: tail -f '$LOG_FILE'"
    echo "⏹️ Stop: pkill -f hdmi_chatbot_vietnamese.py"
    echo "🔘 Hardware buttons: GPIO 22 (stop), GPIO 23 (pause), GPIO 24 (resume)"
    echo
    echo "Usage instructions:"
    echo "• Look at your HDMI monitor for the chatbot interface"
    echo "• Say 'Xin chào' (Vietnamese) or 'Hello' (English) to start"
    echo "• The GUI will show conversation history and status"
    echo "• Say 'Tạm biệt' or 'Goodbye' to exit"
    echo
    
    # Monitor for a few seconds
    sleep 3
    if ps -p $pid > /dev/null; then
        echo -e "${GREEN}✅ Chatbot is running successfully${NC}"
    else
        echo -e "${RED}❌ Chatbot failed to start - check logs${NC}"
        cat "$LOG_FILE" | tail -20
        exit 1
    fi
}

# Cleanup function
cleanup() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            kill $pid
            log_message "🛑 Chatbot stopped (PID: $pid)"
        fi
        rm -f "$PID_FILE"
    fi
}

# Trap cleanup on exit
trap cleanup EXIT

# Main execution
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --lang)
                CHATBOT_LANG="$2"
                shift 2
                ;;
            --mic-target)
                MIC_TARGET="--mic-target $2"
                shift 2
                ;;
            --daemon)
                DAEMON_MODE=1
                shift
                ;;
            --help)
                echo "Tiến Minh - HDMI Vietnamese Voice Chatbot Startup Script"
                echo
                echo "Usage: $0 [options]"
                echo "  --lang <vi|en|auto>      Set language"
                echo "  --mic-target <target>    Set microphone target"
                echo "  --daemon                 Run in daemon mode (no interactive prompts)"
                echo "  --help                   Show this help"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    check_running
    check_system
    setup_environment
    
    # Interactive setup unless in daemon mode
    if [ -z "$DAEMON_MODE" ]; then
        select_language
        select_microphone
    else
        CHATBOT_LANG=${CHATBOT_LANG:-vi}
        log_message "🤖 Running in daemon mode with language: $CHATBOT_LANG"
    fi
    
    start_chatbot
}

# Run main function
main "$@"