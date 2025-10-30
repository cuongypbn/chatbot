# 🤖 Tiến Minh - Chatbot Tiếng Việt cho Raspberry Pi 4

## 🚀 Cài đặt CỰC KỲ ĐƠN GIẢN (1 lệnh)

```bash
# Download và chạy script tự động
cd ~
git clone https://github.com/YOUR_USERNAME/voice-chatbot.git
cd voice-chatbot
chmod +x pi4_auto_setup.sh
./pi4_auto_setup.sh
```

**Script sẽ tự động:**
- ✅ Phát hiện RAM của Pi 4 (1GB/2GB/4GB/8GB)
- ✅ Chọn model phù hợp (Whisper, LLM, TTS)
- ✅ Cài đặt tất cả dependencies
- ✅ Cấu hình hệ thống tối ưu
- ✅ Setup audio, Bluetooth, GPIO
- ✅ Tải models AI
- ✅ Tạo config files

⏱️ Thời gian: **15-30 phút** (tùy tốc độ internet)

## 📋 Cấu hình được khuyến nghị

| RAM  | Whisper | LLM Model | TTS Engine | Trải nghiệm |
|------|---------|-----------|------------|-------------|
| 1GB  | tiny    | tinyllama:1.1b | espeak | Cơ bản |
| 2GB  | base    | tinyllama:1.1b | gtts | Tạm ổn |
| **4GB** ⭐ | **small** | **qwen2:0.5b** | **edge** | **Tốt nhất** |
| 8GB 🏆 | medium | gemma2:2b | edge | Cao cấp |

## 🎮 Sử dụng

### Sau khi cài đặt xong:

```bash
# 1. Reboot (bắt buộc)
sudo reboot

# 2. Kết nối Bluetooth speaker
bluetoothctl
> power on
> scan on
> pair XX:XX:XX:XX:XX:XX
> trust XX:XX:XX:XX:XX:XX
> connect XX:XX:XX:XX:XX:XX
> exit

# 3. Cắm USB microphone

# 4. Chạy chatbot với màn hình HDMI
cd ~/voice-chatbot
./start_hdmi_chatbot.sh
```

### Hoặc dùng lệnh ngắn:
```bash
chatbot          # Vào thư mục project
start-chatbot    # Chạy chatbot
check-pi4        # Kiểm tra hệ thống
```

## 🖥️ Giao diện HDMI

Khi chạy `start_hdmi_chatbot.sh`, bạn sẽ thấy:

```
┌─────────────────────────────────────┐
│     🤖 TIẾN MINH VOICE ASSISTANT    │
├─────────────────────────────────────┤
│                                     │
│         (●‿●)  <- Mặt Tiến Minh    │
│                                     │
├─────────────────────────────────────┤
│ LỊCH SỬ HỘI THOẠI:                 │
│                                     │
│ 👤 You: Xin chào Tiến Minh         │
│ 🤖 Bot: Chào bạn! Tôi có thể giúp  │
│         gì cho bạn?                 │
│                                     │
├─────────────────────────────────────┤
│ 🎤 Micro: Ready  📢 TTS: edge-vi   │
│ 🧠 Model: qwen2:0.5b  💾 4GB RAM   │
└─────────────────────────────────────┘
```

## 🎤 Cách nói chuyện với Tiến Minh

### Tiếng Việt:
```
"Xin chào Tiến Minh"
"Chào bạn"
"Tiến Minh ơi, thời tiết hôm nay thế nào?"
"Kể cho tôi một câu chuyện vui"
```

### English:
```
"Hey computer"
"Okay computer, what's the weather?"
"Tell me a joke"
```

### Auto-detect (tự nhận diện ngôn ngữ):
Chatbot tự động nhận biết bạn nói tiếng Việt hay tiếng Anh!

## 🎛️ GPIO Buttons (tùy chọn)

Nếu bạn kết nối buttons:
- **GPIO 22**: Dừng chatbot
- **GPIO 23**: Tạm dừng
- **GPIO 24**: Tiếp tục

## 📊 Kiểm tra hệ thống

```bash
# Chạy script kiểm tra toàn diện
./pi4_system_check.sh

# Sẽ kiểm tra:
# ✅ Pi 4 model
# ✅ RAM available
# ✅ GPIO/SPI
# ✅ Audio system
# ✅ Bluetooth
# ✅ TTS engines
# ✅ AI models
# ✅ Fonts tiếng Việt
```

## 🔧 Troubleshooting

### ❌ Lỗi "Microphone not found"
```bash
# List microphones
wpctl status | grep -A 10 "Audio/Source"

# Set microphone cụ thể
MIC_TARGET=<source-id> ./start_hdmi_chatbot.sh
```

### ❌ Lỗi "Speaker not working"
```bash
# List speakers
wpctl status | grep -A 10 "Audio/Sink"

# Test speaker
pw-play /usr/share/sounds/alsa/Front_Center.wav
```

### ❌ Lỗi "Out of memory"
```bash
# Kiểm tra RAM
free -h

# Sử dụng model nhỏ hơn (edit config.py)
nano ~/voice-chatbot/config.py
# Đổi WHISPER_MODEL = "tiny"
# Đổi LLM_MODEL = "tinyllama:1.1b"

# Hoặc chạy lại auto setup
./pi4_auto_setup.sh
```

### ❌ Pi 4 quá nóng
```bash
# Kiểm tra nhiệt độ
vcgencmd measure_temp

# Nếu > 70°C: Cần thêm tản nhiệt hoặc quạt!
```

### ❌ Giọng nói không tự nhiên
```bash
# Đổi TTS engine (edit config.py)
nano ~/voice-chatbot/config.py
# Đổi TTS_ENGINE = "edge"  # Tốt nhất, cần internet
# Hoặc TTS_ENGINE = "gtts"   # Tốt, cần internet
# Hoặc TTS_ENGINE = "espeak" # Nhanh, offline, giọng máy
```

## 📁 Cấu trúc project

```
~/voice-chatbot/
├── hdmi_chatbot_vietnamese.py    # Main chatbot với GUI
├── chatbot_vietnamese.py         # Terminal-only version
├── vietnamese_tts.py              # TTS engine
├── config.py                      # Cấu hình (auto-generated)
├── start_hdmi_chatbot.sh         # Script khởi động
├── pi4_auto_setup.sh             # Script cài đặt tự động
├── pi4_system_check.sh           # Script kiểm tra hệ thống
├── .env                          # Environment variables
└── .venv/                        # Python virtual environment
```

## 🎓 Hướng dẫn chi tiết

Xem file `PI4_OPTIMIZATION_GUIDE.md` để:
- Tùy chỉnh cấu hình cho từng mức RAM
- Tối ưu hóa performance
- Cài đặt thủ công từng bước
- Benchmarks và so sánh models
- Advanced troubleshooting

## 🌟 Tính năng

- ✅ **Nhận diện giọng nói tiếng Việt** (Whisper)
- ✅ **AI trả lời thông minh** (Ollama LLM)
- ✅ **Phát giọng tiếng Việt tự nhiên** (Edge TTS)
- ✅ **Giao diện HDMI đẹp** (Pygame GUI)
- ✅ **Tự động chọn ngôn ngữ** (Việt/Anh)
- ✅ **GPIO buttons** (tùy chọn)
- ✅ **Bluetooth speaker** support
- ✅ **USB microphone** support
- ✅ **Tối ưu cho Pi 4** (ARM64)

## 🔄 Updates

```bash
# Update chatbot code
cd ~/voice-chatbot
git pull

# Update models
ollama pull qwen2:0.5b

# Update Python packages
source .venv/bin/activate
pip install --upgrade -r requirements.txt
```

## 💡 Tips

### Tăng tốc độ response:
1. Sử dụng model nhỏ hơn (tiny/base)
2. Giảm `MAX_RECORDING_MS` trong config.py
3. Sử dụng espeak TTS (instant, offline)

### Tăng chất lượng:
1. Sử dụng model lớn hơn (small/medium)
2. Dùng Edge TTS hoặc gTTS
3. Nói rõ ràng, không quá nhanh

### Tiết kiệm RAM:
1. Đóng các ứng dụng khác
2. Sử dụng terminal version thay vì GUI
3. Giảm GPU memory trong config.txt

## 🆘 Hỗ trợ

### Logs:
```bash
# Xem logs chatbot
tail -f ~/voice-chatbot/logs/hdmi_chatbot.log

# Xem logs hệ thống
journalctl -u ollama -f
```

### Test từng phần:
```bash
cd ~/voice-chatbot
source .venv/bin/activate

# Test microphone
python3 -c "import sounddevice as sd; print(sd.query_devices())"

# Test TTS
python3 test_vietnamese_tts.py

# Test Ollama
ollama run qwen2:0.5b "Xin chào"

# Test Whisper
python3 -c "
from faster_whisper import WhisperModel
model = WhisperModel('small')
print('✅ Whisper loaded')
"
```

## 📞 Contact

Nếu gặp vấn đề:
1. Chạy `./pi4_system_check.sh` và gửi output
2. Xem logs: `tail ~/voice-chatbot/logs/hdmi_chatbot.log`
3. Kiểm tra `PI4_OPTIMIZATION_GUIDE.md`

## 📜 License

MIT License - Free to use and modify

## 🙏 Credits

- Whisper by OpenAI
- Ollama for ARM support
- gTTS, Edge TTS for Vietnamese voices
- Raspberry Pi Foundation

---

**Được tối ưu hóa cho Raspberry Pi 4 với tiếng Việt** 🇻🇳  
*Version 2.0 - Pi 4 Optimized*

