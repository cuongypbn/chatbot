# 📚 Tài liệu dự án - Vietnamese Voice Chatbot cho Pi 4

## 📂 Cấu trúc files

```
voice-chatbot/
│
├── 📖 Documentation (Tài liệu)
│   ├── README.md                      # Hướng dẫn chi tiết đầy đủ
│   ├── QUICKSTART_PI4.md              # ⭐ BẮT ĐẦU TẠI ĐÂY - Hướng dẫn nhanh
│   ├── PI4_OPTIMIZATION_GUIDE.md      # Hướng dẫn tối ưu hóa chi tiết
│   ├── RAM_GUIDE.md                   # Lựa chọn cấu hình theo RAM
│   └── HDMI_VERSION_SUMMARY.md        # So sánh HDMI vs LCD
│
├── 🤖 Main Programs (Chương trình chính)
│   ├── hdmi_chatbot_vietnamese.py     # ⭐ KHUYẾN NGHỊ - Chatbot với GUI HDMI
│   ├── chatbot_vietnamese.py          # Terminal-only version
│   ├── bobchat_vietnamese.py          # LCD SPI version (nâng cao)
│   └── vietnamese_tts.py               # TTS engine module
│
├── 🚀 Scripts (Các script tiện ích)
│   ├── pi4_auto_setup.sh              # ⭐ Cài đặt tự động (1 lệnh)
│   ├── start_hdmi_chatbot.sh          # Khởi động chatbot HDMI
│   ├── start_vietnamese_chatbot.sh    # Khởi động terminal version
│   ├── pi4_system_check.sh            # Kiểm tra hệ thống
│   └── quick_test.sh                  # Test nhanh các thành phần
│
├── ⚙️ Configuration (Cấu hình)
│   ├── config.py                      # Config tự động tạo
│   ├── .env                           # Environment variables
│   ├── requirements.txt               # Python dependencies
│   ├── hdmi-vietnamese-chatbot.service # Systemd service
│   └── vietnamese-chatbot.service     # Service cho terminal version
│
└── 🧪 Testing (Kiểm tra)
    ├── test_vietnamese_tts.py         # Test TTS engines
    ├── chatbot.py                     # Base chatbot (English)
    └── bobchat.py                     # Base LCD version

```

---

## 🚀 Bắt đầu nhanh (3 bước)

### Bước 1: Clone project
```bash
cd ~
git clone https://github.com/YOUR_USERNAME/voice-chatbot.git
cd voice-chatbot
```

### Bước 2: Chạy auto setup
```bash
chmod +x pi4_auto_setup.sh
./pi4_auto_setup.sh
```

### Bước 3: Reboot và chạy
```bash
sudo reboot

# Sau khi boot lại
cd ~/voice-chatbot
./start_hdmi_chatbot.sh
```

---

## 📖 Hướng dẫn sử dụng files

### Tài liệu nên đọc theo thứ tự:

1. **QUICKSTART_PI4.md** ⭐ BẮT ĐẦU TẠI ĐÂY
   - Hướng dẫn cài đặt đơn giản nhất
   - Giải thích cơ bản về chatbot
   - Cách sử dụng script tự động

2. **RAM_GUIDE.md** - Chọn cấu hình phù hợp
   - So sánh 1GB/2GB/4GB/8GB RAM
   - Bảng so sánh models
   - Tips tối ưu cho từng mức RAM

3. **PI4_OPTIMIZATION_GUIDE.md** - Hướng dẫn nâng cao
   - Cài đặt thủ công từng bước
   - Tối ưu hóa performance
   - Troubleshooting chi tiết

4. **HDMI_VERSION_SUMMARY.md** - Phân biệt phiên bản
   - HDMI vs LCD SPI
   - Ưu nhược điểm từng loại
   - Khi nào dùng phiên bản nào

5. **README.md** - Tham khảo đầy đủ
   - Tất cả thông tin chi tiết
   - Cài đặt thủ công
   - Advanced features

---

## 🤖 Chương trình nên dùng

### Theo màn hình:

**Có màn hình HDMI thông thường:** ⭐ KHUYẾN NGHỊ
```bash
./start_hdmi_chatbot.sh
# Hoặc
python3 hdmi_chatbot_vietnamese.py --lang vi
```

**Chỉ có terminal (SSH):**
```bash
./start_vietnamese_chatbot.sh
# Hoặc
python3 chatbot_vietnamese.py --lang vi
```

**Có màn hình LCD SPI 1.28":** (Nâng cao)
```bash
python3 bobchat_vietnamese.py
```

---

## 🚀 Scripts tiện ích

### 1. `pi4_auto_setup.sh` - Cài đặt tự động
**Khi nào dùng:** Lần đầu setup, hoặc muốn cài lại từ đầu

```bash
./pi4_auto_setup.sh
```

**Chức năng:**
- ✅ Tự động phát hiện RAM
- ✅ Chọn models phù hợp
- ✅ Cài đặt tất cả dependencies
- ✅ Cấu hình hệ thống
- ✅ Tạo config files
- ✅ Test các thành phần

**Thời gian:** 15-30 phút

---

### 2. `start_hdmi_chatbot.sh` - Khởi động chatbot HDMI
**Khi nào dùng:** Mỗi khi muốn chạy chatbot với GUI

```bash
./start_hdmi_chatbot.sh
```

**Chức năng:**
- ✅ Kiểm tra hệ thống
- ✅ Chọn ngôn ngữ (vi/en/auto)
- ✅ Chọn microphone
- ✅ Setup environment
- ✅ Chạy chatbot với GUI

---

### 3. `pi4_system_check.sh` - Kiểm tra hệ thống
**Khi nào dùng:** Khi gặp lỗi, hoặc muốn kiểm tra cấu hình

```bash
./pi4_system_check.sh
```

**Kiểm tra:**
- ✅ Pi 4 model
- ✅ RAM available
- ✅ GPIO/SPI status
- ✅ Audio system
- ✅ Bluetooth
- ✅ TTS engines
- ✅ AI models
- ✅ Fonts

---

### 4. `quick_test.sh` - Test nhanh
**Khi nào dùng:** Sau khi cài đặt, trước khi chạy chatbot

```bash
./quick_test.sh
```

**Test:**
- ✅ Python packages
- ✅ Ollama models
- ✅ Audio devices
- ✅ GPIO access
- ✅ Display environment

---

## ⚙️ Files cấu hình

### `config.py` - Auto-generated
Được tạo tự động bởi `pi4_auto_setup.sh`

```python
WHISPER_MODEL = "small"      # Tùy RAM
LLM_MODEL = "qwen2:0.5b"     # Tùy RAM
TTS_ENGINE = "edge"          # Tùy RAM
OMP_NUM_THREADS = 4          # Tùy CPU
```

**Chỉnh sửa nếu cần:**
```bash
nano ~/voice-chatbot/config.py
```

---

### `.env` - Environment variables
```bash
RAM_TIER=4GB
WHISPER_MODEL=small
LLM_MODEL=qwen2:0.5b
TTS_ENGINE=edge
OMP_NUM_THREADS=4
```

---

### `requirements.txt` - Python dependencies
```bash
# Cài đặt tất cả packages
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🧪 Testing files

### `test_vietnamese_tts.py` - Test TTS engines
```bash
python3 test_vietnamese_tts.py
```

Test các TTS engine:
- espeak-ng
- gTTS
- Edge TTS
- Festival

---

## 🔧 Troubleshooting theo vấn đề

### Vấn đề: Không tìm thấy microphone
```bash
# Kiểm tra
./pi4_system_check.sh

# List microphones
wpctl status | grep -A 10 "Audio/Source"

# Set microphone
MIC_TARGET=<source-id> ./start_hdmi_chatbot.sh
```

### Vấn đề: Ollama không chạy
```bash
# Kiểm tra service
sudo systemctl status ollama

# Restart
sudo systemctl restart ollama

# Pull model lại
ollama pull qwen2:0.5b
```

### Vấn đề: Lỗi Python packages
```bash
# Cài lại
cd ~/voice-chatbot
source .venv/bin/activate
pip install -r requirements.txt
```

### Vấn đề: Không đủ RAM
```bash
# Xem RAM_GUIDE.md để chọn model nhẹ hơn
nano config.py
# Đổi thành:
# WHISPER_MODEL = "tiny"
# LLM_MODEL = "tinyllama:1.1b"
```

---

## 📊 So sánh phiên bản

| Feature | Terminal | HDMI GUI ⭐ | LCD SPI |
|---------|----------|----------|---------|
| **Dễ cài đặt** | ✅✅✅ | ✅✅ | ⚠️ |
| **Giao diện đẹp** | ❌ | ✅✅✅ | ✅✅ |
| **RAM cần** | 1GB+ | 2GB+ | 1GB+ |
| **Hiển thị lịch sử** | Limit | ✅ Full | Limit |
| **Kích thước màn hình** | N/A | Lớn | 1.28" |
| **Giá thành** | Rẻ | Rẻ | Đắt (LCD) |
| **Khuyến nghị** | SSH | **Desktop** | Maker |

---

## 🎯 Workflows phổ biến

### Workflow 1: Cài đặt lần đầu
```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/voice-chatbot.git
cd voice-chatbot

# 2. Auto setup
./pi4_auto_setup.sh

# 3. Reboot
sudo reboot

# 4. Setup Bluetooth
bluetoothctl
# ... pair speaker ...

# 5. Chạy
./start_hdmi_chatbot.sh
```

### Workflow 2: Chạy hàng ngày
```bash
# Vào project
cd ~/voice-chatbot

# Hoặc dùng alias
chatbot

# Chạy chatbot
start-chatbot

# Hoặc
./start_hdmi_chatbot.sh
```

### Workflow 3: Debug khi lỗi
```bash
# 1. Kiểm tra hệ thống
./pi4_system_check.sh

# 2. Test các thành phần
./quick_test.sh

# 3. Xem logs
tail -f logs/hdmi_chatbot.log

# 4. Test riêng TTS
python3 test_vietnamese_tts.py

# 5. Test Ollama
ollama run qwen2:0.5b "Test"
```

### Workflow 4: Nâng cấp
```bash
# Update code
cd ~/voice-chatbot
git pull

# Update models
ollama pull qwen2:0.5b

# Update Python packages
source .venv/bin/activate
pip install --upgrade -r requirements.txt

# Test lại
./quick_test.sh
```

---

## 💡 Tips Pro

### Alias hữu ích (đã có trong auto-setup):
```bash
chatbot          # cd ~/voice-chatbot && source .venv/bin/activate
start-chatbot    # Chạy chatbot HDMI
check-pi4        # Kiểm tra hệ thống
```

### Environment variables:
```bash
# Set microphone mặc định
export MIC_TARGET=alsa_input.usb-xxx

# Set ngôn ngữ
export DEFAULT_LANG=vi

# Set TTS engine
export TTS_ENGINE=edge
```

### Systemd service (auto-start):
```bash
# Enable auto-start
sudo systemctl enable hdmi-vietnamese-chatbot.service

# Start now
sudo systemctl start hdmi-vietnamese-chatbot.service

# Check status
sudo systemctl status hdmi-vietnamese-chatbot.service
```

---

## 📞 Khi cần trợ giúp

1. **Đọc QUICKSTART_PI4.md** - Hướng dẫn cơ bản
2. **Chạy `./pi4_system_check.sh`** - Kiểm tra lỗi
3. **Chạy `./quick_test.sh`** - Test từng phần
4. **Xem `PI4_OPTIMIZATION_GUIDE.md`** - Troubleshooting
5. **Xem logs:** `tail -f logs/hdmi_chatbot.log`

---

**Project được tối ưu hóa cho Raspberry Pi 4 (1GB/2GB/4GB/8GB RAM)**  
**Hỗ trợ đầy đủ tiếng Việt + English** 🇻🇳🇺🇸

*Last updated: 2025*

