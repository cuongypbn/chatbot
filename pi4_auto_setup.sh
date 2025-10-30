th#!/bin/bash
# Pi 4 Auto Configuration Script for Vietnamese Voice Chatbot
# Tự động cấu hình Pi 4 cho chatbot tiếng Việt

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Pi 4 Auto Setup - Vietnamese Voice Chatbot              ║${NC}"
echo -e "${BLUE}║   Tự động cấu hình Raspberry Pi 4 cho chatbot tiếng Việt   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Detect RAM
echo -e "${CYAN}🔍 Đang phát hiện cấu hình Pi 4...${NC}"
TOTAL_RAM_MB=$(free -m | grep "Mem:" | awk '{print $2}')
PI_MODEL=$(cat /proc/cpuinfo | grep "Model" | head -1 | cut -d: -f2 | xargs)

echo -e "   Pi Model: ${GREEN}$PI_MODEL${NC}"
echo -e "   Total RAM: ${GREEN}${TOTAL_RAM_MB}MB${NC}"

# Determine RAM tier
if [ $TOTAL_RAM_MB -ge 7000 ]; then
    RAM_TIER="8GB"
    WHISPER_MODEL="medium"
    LLM_MODEL="gemma2:2b"
    TTS_ENGINE="edge"
    GPU_MEM=256
    SWAP_SIZE=1024
    OMP_THREADS=6
    echo -e "   RAM Tier: ${GREEN}8GB - TỐI ƯU 🏆${NC}"
elif [ $TOTAL_RAM_MB -ge 3500 ]; then
    RAM_TIER="4GB"
    WHISPER_MODEL="small"
    LLM_MODEL="qwen2:0.5b"
    TTS_ENGINE="edge"
    GPU_MEM=128
    SWAP_SIZE=2048
    OMP_THREADS=4
    echo -e "   RAM Tier: ${GREEN}4GB - KHUYẾN NGHỊ ⭐${NC}"
elif [ $TOTAL_RAM_MB -ge 1800 ]; then
    RAM_TIER="2GB"
    WHISPER_MODEL="base"
    LLM_MODEL="tinyllama:1.1b"
    TTS_ENGINE="gtts"
    GPU_MEM=96
    SWAP_SIZE=2048
    OMP_THREADS=3
    echo -e "   RAM Tier: ${YELLOW}2GB - TỐI THIỂU${NC}"
else
    RAM_TIER="1GB"
    WHISPER_MODEL="tiny"
    LLM_MODEL="tinyllama:1.1b"
    TTS_ENGINE="espeak"
    GPU_MEM=64
    SWAP_SIZE=2048
    OMP_THREADS=2
    echo -e "   RAM Tier: ${RED}1GB - HẠN CHẾ${NC}"
fi

echo ""
echo -e "${CYAN}📋 Cấu hình được khuyến nghị:${NC}"
echo -e "   Whisper Model: ${GREEN}$WHISPER_MODEL${NC}"
echo -e "   LLM Model: ${GREEN}$LLM_MODEL${NC}"
echo -e "   TTS Engine: ${GREEN}$TTS_ENGINE${NC}"
echo -e "   GPU Memory: ${GREEN}${GPU_MEM}MB${NC}"
echo -e "   Swap Size: ${GREEN}${SWAP_SIZE}MB${NC}"
echo -e "   OMP Threads: ${GREEN}$OMP_THREADS${NC}"
echo ""

# Ask for confirmation
read -p "Tiếp tục cài đặt với cấu hình này? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Đã hủy cài đặt.${NC}"
    exit 0
fi

# Function to check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        echo -e "${RED}❌ Không nên chạy script này với sudo!${NC}"
        echo -e "   Chạy lại: ${YELLOW}./pi4_auto_setup.sh${NC}"
        exit 1
    fi
}

# Function to log
log() {
    echo -e "${GREEN}✅${NC} $1"
}

warn() {
    echo -e "${YELLOW}⚠️${NC}  $1"
}

error() {
    echo -e "${RED}❌${NC} $1"
}

check_root

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}BƯỚC 1: Cập nhật hệ thống${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Update system
sudo apt update
sudo apt upgrade -y
log "Đã cập nhật hệ thống"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}BƯỚC 2: Cài đặt dependencies${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Core packages (updated for Pi OS Bookworm)
sudo apt install -y \
    build-essential cmake git \
    python3-dev python3-pip python3-venv \
    libopenblas-dev \
    libhdf5-dev libportaudio2 portaudio19-dev \
    ffmpeg libavcodec-extra libsndfile1 flac \
    libblas-dev liblapack-dev gfortran \
    swig libffi-dev pkg-config
log "Đã cài đặt core packages"

# GPIO libraries (system packages to avoid building)
sudo apt install -y \
    python3-lgpio python3-gpiozero python3-rpi.gpio \
    python3-spidev 2>/dev/null || {
    warn "Some GPIO packages not available via apt, will install via pip"
}
log "Đã cài đặt GPIO system packages"

# Audio stack
sudo apt install -y \
    pipewire pipewire-pulse wireplumber \
    libspa-0.2-bluetooth alsa-utils
log "Đã cài đặt audio stack"

# Bluetooth
sudo apt install -y bluez bluez-tools pi-bluetooth
log "Đã cài đặt Bluetooth 5.0"

# TTS engines and fonts
sudo apt install -y \
    espeak-ng espeak-ng-data \
    festival festvox-us-slt-hts \
    fonts-noto-cjk fonts-noto-cjk-extra \
    fonts-dejavu fonts-liberation
log "Đã cài đặt TTS engines và fonts tiếng Việt"

# GUI libraries (nếu có desktop)
if [ -n "$DISPLAY" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    sudo apt install -y \
        python3-pygame python3-opencv \
        fonts-liberation fonts-vlgothic
    log "Đã cài đặt GUI libraries"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}BƯỚC 3: Setup Python virtual environment${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Create project directory
PROJECT_DIR="$HOME/voice-chatbot"
if [ ! -d "$PROJECT_DIR" ]; then
    mkdir -p "$PROJECT_DIR"
    log "Đã tạo thư mục project: $PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# Create venv
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    log "Đã tạo Python virtual environment"
fi

# Activate venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
log "Đã upgrade pip"

# Install Python packages
echo -e "${CYAN}   Đang cài đặt Python packages (có thể mất vài phút)...${NC}"

# Core packages
pip install numpy
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Whisper
pip install faster-whisper openai-whisper soundfile librosa

# Ollama
pip install ollama

# TTS
pip install gtts gTTS-token edge-tts pyttsx3

# Audio
pip install pyaudio pygame sounddevice pydub

# GUI
pip install pygame Pillow

# GPIO (with fallback handling)
echo -e "${CYAN}   Installing GPIO packages...${NC}"
pip install RPi.GPIO gpiozero || warn "Some GPIO packages failed but may not be critical"

# Try lgpio separately with better error handling
if ! python3 -c "import lgpio" 2>/dev/null; then
    echo -e "${CYAN}   Installing lgpio (may take time to build)...${NC}"
    pip install --no-cache-dir lgpio 2>/dev/null || {
        warn "lgpio failed to build, using system package fallback"
        # Try to use system lgpio if available
        if dpkg -l | grep -q python3-lgpio; then
            echo -e "${GREEN}   Using system python3-lgpio package${NC}"
        else
            warn "lgpio not available - GPIO features may be limited"
        fi
    }
fi

# SpiDev
pip install spidev || warn "spidev failed but may not be critical"

# Utilities
pip install python-dotenv requests

log "Đã cài đặt tất cả Python packages"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}BƯỚC 4: Cài đặt Ollama và models${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo -e "${CYAN}   Đang cài đặt Ollama...${NC}"
    curl -fsSL https://ollama.com/install.sh | sh
    sudo systemctl enable --now ollama
    log "Đã cài đặt Ollama"
else
    log "Ollama đã được cài đặt"
fi

# Wait for Ollama to start
sleep 3

# Pull models based on RAM
echo -e "${CYAN}   Đang tải model $LLM_MODEL (có thể mất vài phút)...${NC}"
ollama pull $LLM_MODEL
log "Đã tải LLM model: $LLM_MODEL"

# Pull additional models for better Vietnamese support
if [ "$RAM_TIER" == "8GB" ]; then
    echo -e "${CYAN}   Đang tải thêm models cho 8GB RAM...${NC}"
    ollama pull qwen2:1.5b
    ollama pull llama3.2:3b
    log "Đã tải additional models"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}BƯỚC 5: Cấu hình hệ thống${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Add user to groups
sudo usermod -aG audio,gpio,spi $USER
log "Đã thêm user vào groups: audio, gpio, spi"

# Enable services
sudo systemctl enable --now bluetooth
systemctl --user enable --now pipewire pipewire-pulse wireplumber
sudo loginctl enable-linger $USER
log "Đã enable audio và bluetooth services"

# Configure swap
echo -e "${CYAN}   Đang cấu hình swap...${NC}"
if [ -f /etc/dphys-swapfile ]; then
    sudo dphys-swapfile swapoff
    sudo sed -i "s/^CONF_SWAPSIZE=.*/CONF_SWAPSIZE=$SWAP_SIZE/" /etc/dphys-swapfile
    sudo dphys-swapfile setup
    sudo dphys-swapfile swapon
    log "Đã cấu hình swap: ${SWAP_SIZE}MB"
fi

# Configure config.txt
CONFIG_FILE="/boot/firmware/config.txt"
if [ ! -f "$CONFIG_FILE" ]; then
    CONFIG_FILE="/boot/config.txt"
fi

if [ -f "$CONFIG_FILE" ]; then
    echo -e "${CYAN}   Đang cấu hình $CONFIG_FILE...${NC}"

    # Backup
    sudo cp "$CONFIG_FILE" "${CONFIG_FILE}.backup_$(date +%Y%m%d_%H%M%S)"

    # Add optimization settings if not exists
    if ! grep -q "# === Pi 4 Voice Chatbot Optimization ===" "$CONFIG_FILE"; then
        sudo tee -a "$CONFIG_FILE" > /dev/null <<EOF

# === Pi 4 Voice Chatbot Optimization ===
gpu_mem=$GPU_MEM
dtparam=audio=on
audio_pwm_mode=2
dtparam=krnbt=on
hdmi_force_hotplug=1
hdmi_drive=2
max_usb_current=1
EOF
        log "Đã thêm optimization settings vào config.txt"
    else
        warn "Config.txt đã có optimization settings"
    fi
fi

# Create environment file
ENV_FILE="$PROJECT_DIR/.env"
cat > "$ENV_FILE" <<EOF
# Pi 4 Configuration - Auto-generated
RAM_TIER=$RAM_TIER
WHISPER_MODEL=$WHISPER_MODEL
LLM_MODEL=$LLM_MODEL
TTS_ENGINE=$TTS_ENGINE
OMP_NUM_THREADS=$OMP_THREADS
MKL_NUM_THREADS=$OMP_THREADS
GPIOZERO_PIN_FACTORY=rpigpio
EOF
log "Đã tạo file cấu hình: .env"

# Create bashrc additions
BASHRC_ADDITION="$HOME/.bashrc_chatbot"
cat > "$BASHRC_ADDITION" <<EOF
# Vietnamese Voice Chatbot Environment
export OMP_NUM_THREADS=$OMP_THREADS
export MKL_NUM_THREADS=$OMP_THREADS
export GPIOZERO_PIN_FACTORY=rpigpio

# Chatbot aliases
alias chatbot='cd ~/voice-chatbot && source .venv/bin/activate'
alias start-chatbot='cd ~/voice-chatbot && ./start_hdmi_chatbot.sh'
alias check-pi4='cd ~/voice-chatbot && ./pi4_system_check.sh'
EOF

if ! grep -q "source ~/.bashrc_chatbot" "$HOME/.bashrc"; then
    echo "source ~/.bashrc_chatbot" >> "$HOME/.bashrc"
    log "Đã thêm environment variables vào .bashrc"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}BƯỚC 6: Tạo config file cho chatbot${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Create config.py
CONFIG_PY="$PROJECT_DIR/config.py"
cat > "$CONFIG_PY" <<EOF
"""
Auto-generated configuration for Pi 4 Vietnamese Voice Chatbot
RAM Tier: $RAM_TIER
"""

# Models configuration
WHISPER_MODEL = "$WHISPER_MODEL"
LLM_MODEL = "$LLM_MODEL"
TTS_ENGINE = "$TTS_ENGINE"

# Performance tuning
OMP_NUM_THREADS = $OMP_THREADS
MKL_NUM_THREADS = $OMP_THREADS

# Audio settings
PREF_SAMPLE_RATE = 16000
PREF_CHANNELS = 1

# VAD settings
FRAME_MS = 30
SILENCE_THRESHOLD = 120
END_SILENCE_MS = 800
MIN_SPEECH_MS = 300
MAX_RECORDING_MS = 15000

# Display settings (for HDMI version)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# GPIO pins
STOP_BUTTON_PIN = 22
PAUSE_BUTTON_PIN = 23
RESUME_BUTTON_PIN = 24

# Language
DEFAULT_LANGUAGE = "vi"
SUPPORTED_LANGUAGES = ["vi", "en", "auto"]

# Wake words
VIETNAMESE_WAKE_WORDS = ["xin chào", "chào bạn", "hey tiến minh", "tiến minh ơi"]
ENGLISH_WAKE_WORDS = ["hey computer", "okay computer", "hey assistant"]
EOF
log "Đã tạo config.py"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}BƯỚC 7: Test cài đặt${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Test Python imports
echo -e "${CYAN}   Testing Python packages...${NC}"
python3 -c "
import sys
packages = {
    'numpy': 'NumPy',
    'torch': 'PyTorch',
    'faster_whisper': 'Faster Whisper',
    'ollama': 'Ollama',
    'gtts': 'gTTS',
    'pygame': 'Pygame',
    'RPi.GPIO': 'RPi.GPIO',
    'gpiozero': 'gpiozero'
}

failed = []
for pkg, name in packages.items():
    try:
        __import__(pkg)
        print(f'✅ {name}')
    except ImportError:
        print(f'❌ {name}')
        failed.append(name)

if failed:
    print(f'\n⚠️  Some packages failed: {failed}')
    sys.exit(1)
else:
    print('\n✅ All packages installed successfully!')
"

if [ $? -eq 0 ]; then
    log "Python packages test passed"
else
    error "Some Python packages failed to import"
fi

# Test Ollama
echo -e "${CYAN}   Testing Ollama...${NC}"
if ollama list | grep -q "$LLM_MODEL"; then
    log "Ollama model $LLM_MODEL available"
else
    warn "Ollama model $LLM_MODEL not found in list"
fi

# Test audio
echo -e "${CYAN}   Testing audio system...${NC}"
if systemctl --user is-active --quiet pipewire; then
    log "PipeWire is running"
else
    warn "PipeWire is not running"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    CÀI ĐẶT HOÀN TẤT! 🎉                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}📊 Tóm tắt cấu hình:${NC}"
echo -e "   Pi 4 RAM: ${GREEN}$RAM_TIER${NC}"
echo -e "   Whisper: ${GREEN}$WHISPER_MODEL${NC}"
echo -e "   LLM: ${GREEN}$LLM_MODEL${NC}"
echo -e "   TTS: ${GREEN}$TTS_ENGINE${NC}"
echo ""
echo -e "${YELLOW}⚠️  QUAN TRỌNG: Cần REBOOT để áp dụng tất cả thay đổi!${NC}"
echo ""
echo -e "${CYAN}Các bước tiếp theo:${NC}"
echo -e "   1️⃣  Reboot Pi: ${GREEN}sudo reboot${NC}"
echo -e "   2️⃣  Sau khi boot lại, kết nối Bluetooth speaker"
echo -e "   3️⃣  Cắm USB microphone"
echo -e "   4️⃣  Chạy chatbot: ${GREEN}cd ~/voice-chatbot && ./start_hdmi_chatbot.sh${NC}"
echo ""
echo -e "${CYAN}Hữu ích:${NC}"
echo -e "   • Kiểm tra hệ thống: ${GREEN}check-pi4${NC}"
echo -e "   • Vào project: ${GREEN}chatbot${NC}"
echo -e "   • Chạy chatbot: ${GREEN}start-chatbot${NC}"
echo ""

# Ask for reboot
read -p "Reboot ngay bây giờ? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Đang reboot...${NC}"
    sudo reboot
else
    echo -e "${YELLOW}Nhớ reboot sau: sudo reboot${NC}"
fi

