#!/bin/bash
# Pi 4 System Check Script for Vietnamese Voice Chatbot
# Kiểm tra hệ thống Pi 4 cho chatbot tiếng Việt

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Raspberry Pi 4 System Check for Vietnamese Voice Chatbot${NC}"
echo "=================================================================="

# Check Pi model
echo -e "\n${YELLOW}📱 Checking Raspberry Pi Model...${NC}"
PI_MODEL=$(cat /proc/cpuinfo | grep "Model" | head -1)
echo "   $PI_MODEL"

if [[ $PI_MODEL == *"Raspberry Pi 4"* ]]; then
    echo -e "   ${GREEN}✅ Confirmed: Raspberry Pi 4${NC}"
else
    echo -e "   ${YELLOW}⚠️  Warning: Not detected as Pi 4, continuing anyway...${NC}"
fi

# Check memory
echo -e "\n${YELLOW}🧠 Checking Memory...${NC}"
TOTAL_MEM=$(free -h | grep "Mem:" | awk '{print $2}')
echo "   Total Memory: $TOTAL_MEM"

TOTAL_MEM_MB=$(free -m | grep "Mem:" | awk '{print $2}')
if [ $TOTAL_MEM_MB -ge 7000 ]; then
    echo -e "   ${GREEN}✅ 8GB RAM detected - Perfect for AI models${NC}"
elif [ $TOTAL_MEM_MB -ge 3500 ]; then
    echo -e "   ${YELLOW}⚠️  4GB RAM - May need lighter models${NC}"
else
    echo -e "   ${RED}❌ Less than 4GB RAM - Performance issues expected${NC}"
fi

# Check GPIO/SPI
echo -e "\n${YELLOW}🔌 Checking GPIO/SPI Support...${NC}"
if lsmod | grep -q spi_bcm2835; then
    echo -e "   ${GREEN}✅ SPI kernel module loaded${NC}"
else
    echo -e "   ${RED}❌ SPI not enabled - run 'sudo raspi-config'${NC}"
fi

if [ -e /dev/spidev0.0 ]; then
    echo -e "   ${GREEN}✅ SPI device available${NC}"
else
    echo -e "   ${RED}❌ SPI device not found${NC}"
fi

# Check user groups
echo -e "\n${YELLOW}👤 Checking User Permissions...${NC}"
if groups $USER | grep -q gpio; then
    echo -e "   ${GREEN}✅ User in gpio group${NC}"
else
    echo -e "   ${RED}❌ User not in gpio group - run 'sudo usermod -a -G gpio $USER'${NC}"
fi

if groups $USER | grep -q spi; then
    echo -e "   ${GREEN}✅ User in spi group${NC}"
else
    echo -e "   ${RED}❌ User not in spi group - run 'sudo usermod -a -G spi $USER'${NC}"
fi

if groups $USER | grep -q audio; then
    echo -e "   ${GREEN}✅ User in audio group${NC}"
else
    echo -e "   ${RED}❌ User not in audio group - run 'sudo usermod -a -G audio $USER'${NC}"
fi

# Check Python and GPIO libraries
echo -e "\n${YELLOW}🐍 Checking Python GPIO Libraries...${NC}"
python3 -c "import RPi.GPIO; print('✅ RPi.GPIO available')" 2>/dev/null || echo -e "   ${RED}❌ RPi.GPIO not available${NC}"
python3 -c "import gpiozero; print('✅ gpiozero available')" 2>/dev/null || echo -e "   ${RED}❌ gpiozero not available${NC}"
python3 -c "import spidev; print('✅ spidev available')" 2>/dev/null || echo -e "   ${RED}❌ spidev not available${NC}"

# Test basic GPIO functionality
echo -e "\n${YELLOW}⚡ Testing Basic GPIO Functionality...${NC}"
python3 -c "
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)  # Test pin 18
    GPIO.cleanup()
    print('   ✅ GPIO basic test passed')
except Exception as e:
    print(f'   ❌ GPIO test failed: {e}')
" 2>/dev/null

# Check audio system
echo -e "\n${YELLOW}🔊 Checking Audio System...${NC}"
if systemctl --user is-active --quiet pipewire 2>/dev/null; then
    echo -e "   ${GREEN}✅ PipeWire running${NC}"
else
    echo -e "   ${YELLOW}⚠️  PipeWire not running - run 'systemctl --user start pipewire'${NC}"
fi

if command -v wpctl &> /dev/null; then
    echo -e "   ${GREEN}✅ wpctl (PipeWire control) available${NC}"
    
    # List audio devices
    echo "   Audio Sources (microphones):"
    wpctl status | grep -A 10 "Sources:" | grep -E "^\s*[0-9]+" | head -3 | while read line; do
        echo "     $line"
    done
    
    echo "   Audio Sinks (speakers):"
    wpctl status | grep -A 10 "Sinks:" | grep -E "^\s*[0-9]+" | head -3 | while read line; do
        echo "     $line"
    done
else
    echo -e "   ${RED}❌ wpctl not available${NC}"
fi

# Check Bluetooth
echo -e "\n${YELLOW}📶 Checking Bluetooth...${NC}"
if systemctl is-active --quiet bluetooth; then
    echo -e "   ${GREEN}✅ Bluetooth service running${NC}"
else
    echo -e "   ${RED}❌ Bluetooth service not running${NC}"
fi

if command -v bluetoothctl &> /dev/null; then
    echo -e "   ${GREEN}✅ bluetoothctl available${NC}"
else
    echo -e "   ${RED}❌ bluetoothctl not available${NC}"
fi

# Check Vietnamese TTS packages
echo -e "\n${YELLOW}🗣️  Checking Vietnamese TTS Support...${NC}"
if command -v espeak-ng &> /dev/null; then
    echo -e "   ${GREEN}✅ espeak-ng available${NC}"
    if espeak-ng --voices | grep -q "vi"; then
        echo -e "   ${GREEN}✅ Vietnamese voice available in espeak-ng${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Vietnamese voice not found in espeak-ng${NC}"
    fi
else
    echo -e "   ${RED}❌ espeak-ng not available${NC}"
fi

if command -v festival &> /dev/null; then
    echo -e "   ${GREEN}✅ Festival available${NC}"
else
    echo -e "   ${RED}❌ Festival not available${NC}"
fi

# Check Python TTS libraries
python3 -c "import gtts; print('✅ gTTS available')" 2>/dev/null || echo -e "   ${RED}❌ gTTS not available${NC}"
python3 -c "import pygame; print('✅ pygame available')" 2>/dev/null || echo -e "   ${RED}❌ pygame not available${NC}"

# Check AI models
echo -e "\n${YELLOW}🤖 Checking AI Models...${NC}"
if command -v ollama &> /dev/null; then
    echo -e "   ${GREEN}✅ Ollama installed${NC}"
    
    if systemctl is-active --quiet ollama 2>/dev/null || sudo systemctl is-active --quiet ollama 2>/dev/null; then
        echo -e "   ${GREEN}✅ Ollama service running${NC}"
        
        # Check available models
        echo "   Available models:"
        ollama list 2>/dev/null | tail -n +2 | while read line; do
            if [ -n "$line" ]; then
                echo "     $line"
            fi
        done
    else
        echo -e "   ${YELLOW}⚠️  Ollama service not running${NC}"
    fi
else
    echo -e "   ${RED}❌ Ollama not installed${NC}"
fi

python3 -c "import whisper; print('✅ OpenAI Whisper available')" 2>/dev/null || echo -e "   ${RED}❌ OpenAI Whisper not available${NC}"

# Check Vietnamese fonts
echo -e "\n${YELLOW}📝 Checking Vietnamese Font Support...${NC}"
if fc-list :lang=vi | grep -q "DejaVu\|Noto"; then
    echo -e "   ${GREEN}✅ Vietnamese fonts available${NC}"
else
    echo -e "   ${YELLOW}⚠️  Vietnamese fonts may be limited${NC}"
fi

# Performance recommendations
echo -e "\n${YELLOW}⚡ Pi 4 Performance Recommendations...${NC}"
CPU_TEMP=$(vcgencmd measure_temp | cut -d= -f2 | cut -d\' -f1)
echo "   Current CPU temperature: ${CPU_TEMP}°C"

if (( $(echo "$CPU_TEMP > 70" | bc -l) )); then
    echo -e "   ${RED}⚠️  High temperature! Consider better cooling${NC}"
elif (( $(echo "$CPU_TEMP > 60" | bc -l) )); then
    echo -e "   ${YELLOW}⚠️  Moderate temperature, monitor during heavy use${NC}"
else
    echo -e "   ${GREEN}✅ Good temperature${NC}"
fi

# Check GPU memory split
GPU_MEM=$(vcgencmd get_mem gpu | cut -d= -f2 | cut -dM -f1)
echo "   GPU memory split: ${GPU_MEM}MB"

if [ $GPU_MEM -gt 256 ]; then
    echo -e "   ${YELLOW}⚠️  High GPU memory - consider reducing if not using desktop${NC}"
elif [ $GPU_MEM -lt 64 ]; then
    echo -e "   ${YELLOW}⚠️  Low GPU memory - may affect LCD performance${NC}"
else
    echo -e "   ${GREEN}✅ Good GPU memory allocation${NC}"
fi

# Summary and recommendations
echo -e "\n${BLUE}📋 Summary and Recommendations:${NC}"
echo "=================================================================="

if [[ $PI_MODEL == *"Raspberry Pi 4"* ]] && [ $TOTAL_MEM_MB -ge 7000 ]; then
    echo -e "${GREEN}✅ Your Pi 4 8GB is well-suited for this Vietnamese chatbot project!${NC}"
    echo
    echo "Recommended optimizations:"
    echo "• Use qwen2:0.5b or tinyllama:1.1b for Ollama (lightweight models)"
    echo "• Use Whisper 'small' model for better Vietnamese recognition"
    echo "• Prioritize Edge TTS > gTTS > espeak for voice quality"
    echo "• Monitor temperature during heavy use"
else
    echo -e "${YELLOW}⚠️  Your system may need some optimizations for best performance${NC}"
fi

echo
echo "Next steps:"
echo "1. Fix any red (❌) issues above"
echo "2. Follow the README.md installation guide"
echo "3. Test with: python3 test_vietnamese_tts.py"
echo "4. Run chatbot with: ./start_vietnamese_chatbot.sh"

echo -e "\n${BLUE}🎉 System check complete!${NC}"