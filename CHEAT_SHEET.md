# ⚡ CHEAT SHEET - Vietnamese Voice Chatbot Pi 4

## 🚀 CÀI ĐẶT NHANH (1 LỆNH)

```bash
cd ~ && git clone https://github.com/YOUR_USERNAME/voice-chatbot.git && cd voice-chatbot && chmod +x pi4_auto_setup.sh && ./pi4_auto_setup.sh
```

---

## 📋 LỆNH THƯỜNG DÙNG

### Chạy chatbot:
```bash
cd ~/voice-chatbot && ./start_hdmi_chatbot.sh    # GUI HDMI (khuyến nghị)
chatbot && start-chatbot                          # Alias ngắn
python3 chatbot_vietnamese.py --lang vi          # Terminal only
```

### Kiểm tra:
```bash
./pi4_system_check.sh      # Kiểm tra toàn bộ hệ thống
./quick_test.sh            # Test nhanh
free -h                    # Check RAM
vcgencmd measure_temp      # Check nhiệt độ
```

### Audio:
```bash
wpctl status                          # List tất cả audio devices
wpctl status | grep "Audio/Source"    # List microphones
wpctl status | grep "Audio/Sink"      # List speakers
wpctl set-default <ID>                # Set default device
```

### Bluetooth:
```bash
bluetoothctl                # Vào Bluetooth control
> power on
> scan on
> pair XX:XX:XX:XX:XX:XX
> trust XX:XX:XX:XX:XX:XX
> connect XX:XX:XX:XX:XX:XX
> exit
```

### Ollama:
```bash
ollama list                           # List models
ollama pull qwen2:0.5b               # Download model
ollama run qwen2:0.5b "Test"         # Test model
sudo systemctl status ollama          # Check service
sudo systemctl restart ollama         # Restart service
```

### Logs:
```bash
tail -f ~/voice-chatbot/logs/hdmi_chatbot.log    # Chatbot logs
journalctl -u ollama -f                          # Ollama logs
systemctl --user status pipewire                 # Audio logs
dmesg | tail                                     # System logs
```

---

## 🎯 CẤU HÌNH THEO RAM

| RAM | Whisper | LLM | TTS | Lệnh pull |
|-----|---------|-----|-----|-----------|
| 1GB | tiny | tinyllama:1.1b | espeak | `ollama pull tinyllama:1.1b` |
| 2GB | base | tinyllama:1.1b | gtts | `ollama pull tinyllama:1.1b` |
| 4GB ⭐ | small | qwen2:0.5b | edge | `ollama pull qwen2:0.5b` |
| 8GB 🏆 | medium | gemma2:2b | edge | `ollama pull gemma2:2b` |

---

## 🔧 FIX NHANH LỖI THƯỜNG GẶP

### ❌ Không tìm thấy mic:
```bash
wpctl status | grep -A 10 "Audio/Source"
MIC_TARGET=<ID> ./start_hdmi_chatbot.sh
```

### ❌ Ollama lỗi:
```bash
sudo systemctl restart ollama
ollama pull qwen2:0.5b
```

### ❌ Out of memory:
```bash
nano config.py
# Đổi: WHISPER_MODEL = "tiny"
# Đổi: LLM_MODEL = "tinyllama:1.1b"
```

### ❌ Python lỗi:
```bash
cd ~/voice-chatbot
source .venv/bin/activate
pip install -r requirements.txt
```

### ❌ Pi quá nóng (>70°C):
```bash
# Thêm heatsink/fan!
vcgencmd measure_temp
```

### ❌ Giọng không tự nhiên:
```bash
nano config.py
# Đổi: TTS_ENGINE = "edge"  # Cần internet
```

### ❌ GPIO lỗi:
```bash
sudo usermod -aG gpio,spi $USER
sudo reboot
export GPIOZERO_PIN_FACTORY=rpigpio
```

---

## 🎤 CÁC CÂU NÓI MẪU

### Tiếng Việt:
```
"Xin chào Tiến Minh"
"Chào bạn"
"Tiến Minh ơi, thời tiết hôm nay thế nào?"
"Hãy kể cho tôi một câu chuyện"
"Bạn có thể làm gì?"
```

### English:
```
"Hey computer"
"Hello assistant"
"What's the weather today?"
"Tell me a joke"
```

---

## 📁 CẤU TRÚC QUAN TRỌNG

```
~/voice-chatbot/
├── hdmi_chatbot_vietnamese.py    ⭐ Main program (GUI)
├── chatbot_vietnamese.py         📝 Terminal version
├── config.py                      ⚙️ Cấu hình (edit file này)
├── start_hdmi_chatbot.sh         🚀 Script chạy
├── pi4_auto_setup.sh             📦 Script cài đặt
└── .venv/                         🐍 Python environment
```

---

## ⚙️ EDIT CẤU HÌNH

```bash
nano ~/voice-chatbot/config.py
```

**Các thông số quan trọng:**
```python
WHISPER_MODEL = "small"           # tiny/base/small/medium
LLM_MODEL = "qwen2:0.5b"          # Model Ollama
TTS_ENGINE = "edge"               # espeak/gtts/edge
DEFAULT_LANGUAGE = "vi"           # vi/en/auto
SILENCE_THRESHOLD = 120           # Độ nhạy mic (cao = ít nhạy)
MAX_RECORDING_MS = 15000          # Max thời gian ghi (ms)
```

---

## 🔄 UPDATE

```bash
# Update code
cd ~/voice-chatbot && git pull

# Update models
ollama pull qwen2:0.5b

# Update packages
source .venv/bin/activate
pip install --upgrade -r requirements.txt
```

---

## 🆘 EMERGENCY

### Chatbot không phản hồi:
```bash
pkill -f chatbot
./start_hdmi_chatbot.sh
```

### Hệ thống lag:
```bash
sudo reboot
```

### Reset toàn bộ:
```bash
cd ~/voice-chatbot
rm -rf .venv
./pi4_auto_setup.sh
```

---

## 📊 MONITOR

```bash
# CPU/RAM real-time
htop

# Nhiệt độ real-time
watch -n 1 vcgencmd measure_temp

# Audio devices real-time
watch -n 2 wpctl status

# Chatbot logs real-time
tail -f ~/voice-chatbot/logs/hdmi_chatbot.log
```

---

## 🎛️ GPIO PINS (Tùy chọn)

```python
STOP_BUTTON_PIN = 22      # Dừng chatbot
PAUSE_BUTTON_PIN = 23     # Tạm dừng
RESUME_BUTTON_PIN = 24    # Tiếp tục
```

Kết nối: Pin → GPIO → GND

---

## 🌐 TEST RIÊNG TỪNG PHẦN

```bash
cd ~/voice-chatbot
source .venv/bin/activate

# Test mic
python3 -c "import sounddevice as sd; print(sd.query_devices())"

# Test TTS
python3 test_vietnamese_tts.py

# Test Whisper
python3 -c "from faster_whisper import WhisperModel; m=WhisperModel('small'); print('OK')"

# Test Ollama
ollama run qwen2:0.5b "Xin chào"

# Test Pygame (GUI)
python3 -c "import pygame; pygame.init(); print('OK')"
```

---

## 💾 BACKUP QUAN TRỌNG

```bash
# Backup config
cp config.py config.py.backup

# Backup .env
cp .env .env.backup

# Backup toàn bộ
tar -czf ~/chatbot-backup-$(date +%Y%m%d).tar.gz ~/voice-chatbot
```

---

## 📞 FILES HƯỚNG DẪN

| File | Mục đích |
|------|----------|
| **QUICKSTART_PI4.md** | ⭐ BẮT ĐẦU TẠI ĐÂY |
| **PI4_OPTIMIZATION_GUIDE.md** | Chi tiết tối ưu |
| **RAM_GUIDE.md** | Chọn config theo RAM |
| **PROJECT_STRUCTURE.md** | Giải thích files |
| **README.md** | Tham khảo đầy đủ |

---

## 🎯 WORKFLOW NHANH

### Lần đầu setup:
```bash
1. Clone repo
2. ./pi4_auto_setup.sh
3. sudo reboot
4. Pair Bluetooth speaker
5. ./start_hdmi_chatbot.sh
```

### Chạy hàng ngày:
```bash
chatbot              # Vào thư mục
start-chatbot        # Chạy
```

### Khi lỗi:
```bash
./quick_test.sh      # Test
check-pi4            # Check system
tail -f logs/...     # Xem logs
```

---

**Print file này ra để tham khảo nhanh!** 📄

*Raspberry Pi 4 Vietnamese Voice Chatbot - Quick Reference v2.0*

