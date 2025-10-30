# 🤖 Tiến Minh - Vietnamese Voice Assistant for Raspberry Pi 4

> **Chatbot thông minh nói tiếng Việt - Tối ưu cho TẤT CẢ Pi 4 (1GB/2GB/4GB/8GB RAM)**

[![Pi 4](https://img.shields.io/badge/Raspberry%20Pi-4-C51A4A?logo=raspberry-pi)](https://www.raspberrypi.com/)
[![ARM64](https://img.shields.io/badge/ARM-64bit-blue)](https://www.arm.com/)
[![Vietnamese](https://img.shields.io/badge/Language-Vietnamese-red)](https://vi.wikipedia.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## ⚡ Cài đặt CỰC KỲ ĐƠN GIẢN (1 lệnh)

```bash
cd ~ && git clone https://github.com/YOUR_USERNAME/voice-chatbot.git && cd voice-chatbot && chmod +x pi4_auto_setup.sh && ./pi4_auto_setup.sh
```

**Đợi 15-30 phút → Reboot → Kết nối Bluetooth speaker → Chạy chatbot! 🎉**

---

## 📚 Tài liệu

| File | Mục đích | Thời gian đọc |
|------|----------|---------------|
| **[INDEX.md](INDEX.md)** 📑 | Tìm kiếm nhanh tài liệu | 2 min |
| **[QUICKSTART_PI4.md](QUICKSTART_PI4.md)** ⭐ | **BẮT ĐẦU TẠI ĐÂY** | 15 min |
| **[CHEAT_SHEET.md](CHEAT_SHEET.md)** ⚡ | Lệnh nhanh (print ra!) | 5 min |
| **[RAM_GUIDE.md](RAM_GUIDE.md)** 💾 | Chọn config theo RAM | 20 min |
| **[PI4_OPTIMIZATION_GUIDE.md](PI4_OPTIMIZATION_GUIDE.md)** 🔧 | Tối ưu chi tiết | 45 min |
| **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** 📂 | Giải thích files | 25 min |
| **[README.md](README.md)** 📖 | Tham khảo đầy đủ | 60 min |

**👉 Chưa biết bắt đầu từ đâu? Đọc [QUICKSTART_PI4.md](QUICKSTART_PI4.md)**

---

## 🎯 Tính năng

- ✅ **Nhận diện giọng nói tiếng Việt** (Whisper AI)
- ✅ **Trả lời thông minh** (Ollama LLM local)
- ✅ **Phát giọng tiếng Việt tự nhiên** (Edge TTS / gTTS / espeak)
- ✅ **Giao diện HDMI đẹp** (Pygame GUI với mặt Tiến Minh)
- ✅ **Tự động chọn ngôn ngữ** (Tiếng Việt / English)
- ✅ **Tối ưu theo RAM** (1GB/2GB/4GB/8GB tự động)
- ✅ **Bluetooth speaker** support
- ✅ **USB microphone** support
- ✅ **GPIO buttons** (optional)

---

## 🖥️ Giao diện

### HDMI GUI Version (Khuyến nghị) ⭐
![Chatbot GUI](https://via.placeholder.com/600x400/1a1a2e/16c79a?text=Tien+Minh+Voice+Assistant)

### Terminal Version
![Terminal](https://via.placeholder.com/600x200/0f0f0f/00ff00?text=Terminal+Mode)

---

## 📊 Cấu hình theo RAM

| RAM | Whisper | LLM | TTS | Độ chính xác | Khuyến nghị |
|-----|---------|-----|-----|--------------|-------------|
| 1GB | tiny | tinyllama | espeak | 60% | Cơ bản ⚠️ |
| 2GB | base | tinyllama | gtts | 70% | Tạm ổn 👌 |
| **4GB** | **small** | **qwen2** | **edge** | **85%** | **Tốt nhất** ⭐ |
| 8GB | medium | gemma2 | edge | 90% | Cao cấp 🏆 |

**Script tự động phát hiện RAM và chọn cấu hình tối ưu!**

---

## 🚀 Bắt đầu nhanh

### 1. Cài đặt (chỉ 1 lần)
```bash
cd ~
git clone https://github.com/YOUR_USERNAME/voice-chatbot.git
cd voice-chatbot
chmod +x pi4_auto_setup.sh
./pi4_auto_setup.sh
```

### 2. Reboot
```bash
sudo reboot
```

### 3. Kết nối Bluetooth speaker
```bash
bluetoothctl
> pair XX:XX:XX:XX:XX:XX
> connect XX:XX:XX:XX:XX:XX
> exit
```

### 4. Chạy chatbot
```bash
cd ~/voice-chatbot
./start_hdmi_chatbot.sh
```

**Hoặc dùng alias:** `chatbot` → `start-chatbot`

---

## 🎤 Ví dụ sử dụng

```
👤 You: "Xin chào Tiến Minh"
🤖 Bot: "Chào bạn! Tôi là Tiến Minh, trợ lý ảo của bạn. Tôi có thể giúp gì cho bạn?"

👤 You: "Thời tiết hôm nay thế nào?"
🤖 Bot: "Tôi xin lỗi, tôi không có kết nối internet để kiểm tra thời tiết. 
       Nhưng tôi có thể trò chuyện với bạn về nhiều chủ đề khác!"

👤 You: "Kể một câu chuyện vui"
🤖 Bot: "Được thôi! Ngày xửa ngày xưa..."
```

---

## 🎛️ Scripts tiện ích

```bash
./pi4_auto_setup.sh        # Cài đặt tự động
./start_hdmi_chatbot.sh    # Chạy chatbot GUI
./pi4_system_check.sh      # Kiểm tra hệ thống
./quick_test.sh            # Test nhanh
```

---

## 🔧 Troubleshooting nhanh

### Lỗi microphone:
```bash
wpctl status | grep "Audio/Source"
MIC_TARGET=<ID> ./start_hdmi_chatbot.sh
```

### Lỗi missing packages:
```bash
# Check if venv exists and activate
cd ~/voice-chatbot
source .venv/bin/activate
pip install faster-whisper ollama gtts opencv-python

# Or run quick fix
chmod +x fix_missing_packages.sh
./fix_missing_packages.sh
```

### Lỗi Ollama:
```bash
sudo systemctl restart ollama
ollama pull qwen2:0.5b
```

### Out of memory:
```bash
nano config.py
# Đổi sang model nhỏ hơn (tiny/base)
```

**Xem thêm:** [CHEAT_SHEET.md](CHEAT_SHEET.md)

---

## 📂 Cấu trúc project

```
voice-chatbot/
├── 📖 Docs/           # 7 tài liệu hướng dẫn
├── 🤖 Programs/       # 3 phiên bản chatbot
├── 🚀 Scripts/        # 5 scripts tiện ích
├── ⚙️ Config/         # Auto-generated configs
└── 🧪 Tests/          # Testing tools
```

**Xem chi tiết:** [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

---

## 💡 Tips

### Tăng tốc độ:
- Dùng model nhỏ hơn (tiny/base)
- Dùng espeak TTS (offline, instant)

### Tăng chất lượng:
- Dùng model lớn hơn (small/medium)
- Dùng Edge TTS (cần internet)

### Tiết kiệm RAM:
- Đóng các app khác
- Dùng terminal version
- Tăng swap space

**Xem thêm:** [PI4_OPTIMIZATION_GUIDE.md](PI4_OPTIMIZATION_GUIDE.md)

---

## 🌟 Screenshots

### HDMI GUI
- Mặt Tiến Minh biểu cảm
- Lịch sử hội thoại realtime
- Trạng thái audio/TTS
- Hướng dẫn sử dụng

### Terminal Mode
- Lightweight, chạy qua SSH
- Ít tốn RAM hơn
- Dành cho Pi 1-2GB RAM

---

## 🔄 Updates

```bash
cd ~/voice-chatbot
git pull                              # Update code
ollama pull qwen2:0.5b               # Update models
pip install --upgrade -r requirements.txt  # Update packages
```

---

## 🆘 Hỗ trợ

### Docs:
1. [INDEX.md](INDEX.md) - Tìm kiếm nhanh
2. [QUICKSTART_PI4.md](QUICKSTART_PI4.md) - Bắt đầu
3. [CHEAT_SHEET.md](CHEAT_SHEET.md) - Lệnh nhanh

### Scripts:
```bash
./pi4_system_check.sh      # Check everything
./quick_test.sh            # Test components
```

### Logs:
```bash
tail -f logs/hdmi_chatbot.log
```

---

## 📜 License

MIT License - Free to use and modify

---

## 🙏 Credits

- **Whisper** by OpenAI - Speech recognition
- **Ollama** - Local LLM support
- **gTTS / Edge TTS** - Vietnamese voices
- **Raspberry Pi Foundation** - Amazing hardware
- **Community** - Testing and feedback

---

## 🎯 Roadmap

- [x] Vietnamese speech recognition
- [x] Multiple TTS engines
- [x] HDMI GUI interface
- [x] Auto RAM detection
- [x] Bluetooth support
- [ ] Web interface
- [ ] Voice cloning
- [ ] Smart home integration
- [ ] Multi-user support

---

## 📞 Contact

- GitHub Issues: Report bugs
- Pull Requests: Contributions welcome!
- Discussions: Share ideas

---

<p align="center">
  <b>Được tối ưu hóa cho Raspberry Pi 4</b><br>
  <b>Hỗ trợ đầy đủ tiếng Việt 🇻🇳</b><br>
  <i>Version 2.0 - Pi 4 Optimized</i>
</p>

<p align="center">
  Made with ❤️ for the Vietnamese Raspberry Pi community
</p>

---

**⭐ Nếu project hữu ích, hãy star repo! ⭐**

**👉 BẮT ĐẦU NGAY: [QUICKSTART_PI4.md](QUICKSTART_PI4.md)**

