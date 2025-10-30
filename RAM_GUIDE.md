# 🎯 Lựa chọn cấu hình theo RAM Pi 4

## 📊 Bảng so sánh nhanh

| Thông số | 1GB RAM | 2GB RAM | 4GB RAM ⭐ | 8GB RAM 🏆 |
|----------|---------|---------|-----------|-----------|
| **Whisper Model** | tiny | base | small | medium |
| **Độ chính xác tiếng Việt** | 60% | 70% | 85% | 90% |
| **Thời gian nhận diện** | 1.5s | 2.5s | 4s | 8s |
| **LLM Model** | tinyllama | tinyllama | qwen2:0.5b | gemma2:2b |
| **Thời gian trả lời** | 1-2s | 1-2s | 2-3s | 3-4s |
| **TTS Engine** | espeak | gtts | edge | edge |
| **Chất lượng giọng** | 50% | 80% | 95% | 95% |
| **GUI HDMI** | ❌ | ⚠️ | ✅ | ✅ |
| **Đa nhiệm** | ❌ | ⚠️ | ✅ | ✅ |
| **Khuyến nghị** | Cơ bản | Tạm ổn | **Tốt nhất** | Cao cấp |

---

## 1️⃣ Pi 4 với 1GB RAM

### ⚠️ Cấu hình tối thiểu

**Khả năng:**
- ✅ Chạy được chatbot cơ bản
- ⚠️ Độ chính xác tiếng Việt thấp
- ❌ Không nên dùng GUI
- ❌ Không thể đa nhiệm

**Config:**
```bash
WHISPER_MODEL="tiny"           # ~400MB RAM
LLM_MODEL="tinyllama:1.1b"     # ~800MB RAM
TTS_ENGINE="espeak"            # Offline, instant
GPU_MEM=64
SWAP_SIZE=2048
OMP_THREADS=2
```

**Lệnh cài đặt:**
```bash
./pi4_auto_setup.sh
# Script sẽ tự động phát hiện 1GB và cấu hình phù hợp
```

**Khuyến nghị:**
- Đóng tất cả ứng dụng khác
- Sử dụng terminal-only version (không GUI)
- Chấp nhận giọng máy (espeak)
- Nói chậm và rõ ràng

**Chạy chatbot:**
```bash
cd ~/voice-chatbot
source .venv/bin/activate
MIC_TARGET=<source-id> python3 chatbot_vietnamese.py --lang vi
```

---

## 2️⃣ Pi 4 với 2GB RAM

### ⚠️ Cấu hình trung bình nhẹ

**Khả năng:**
- ✅ Chạy tốt với model nhẹ
- ✅ Độ chính xác tiếng Việt khá
- ⚠️ GUI đơn giản được
- ⚠️ Hạn chế đa nhiệm

**Config:**
```bash
WHISPER_MODEL="base"           # ~1GB RAM
LLM_MODEL="tinyllama:1.1b"     # ~800MB RAM
TTS_ENGINE="gtts"              # Online, chất lượng tốt
GPU_MEM=96
SWAP_SIZE=2048
OMP_THREADS=3
```

**Lệnh cài đặt:**
```bash
./pi4_auto_setup.sh
# Tự động phát hiện 2GB và cấu hình
```

**Khuyến nghị:**
- Đóng trình duyệt web
- Có thể dùng terminal hoặc GUI đơn giản
- Cần kết nối internet cho TTS tốt hơn
- Swap space quan trọng

**Chạy chatbot:**
```bash
# Terminal version (ít RAM hơn)
cd ~/voice-chatbot
source .venv/bin/activate
MIC_TARGET=<source-id> python3 chatbot_vietnamese.py --lang vi

# HDMI GUI (nếu muốn)
./start_hdmi_chatbot.sh
```

---

## 3️⃣ Pi 4 với 4GB RAM ⭐ KHUYẾN NGHỊ

### ✅ Cấu hình cân bằng hoàn hảo

**Khả năng:**
- ✅ Chạy rất mượt
- ✅ Độ chính xác tiếng Việt cao (85%)
- ✅ GUI HDMI đầy đủ tính năng
- ✅ Có thể đa nhiệm nhẹ

**Config:**
```bash
WHISPER_MODEL="small"          # ~2GB RAM - HỖ TRỢ TIẾNG VIỆT TỐT
LLM_MODEL="qwen2:0.5b"         # ~1.5GB RAM - Đa ngôn ngữ
TTS_ENGINE="edge"              # Microsoft Edge TTS - Chất lượng cao
GPU_MEM=128
SWAP_SIZE=2048
OMP_THREADS=4
```

**Lệnh cài đặt:**
```bash
./pi4_auto_setup.sh
# Tự động phát hiện 4GB và cấu hình tối ưu
```

**Khuyến nghị:**
- **Đây là cấu hình tối ưu cho hầu hết người dùng**
- Sử dụng HDMI GUI cho trải nghiệm tốt nhất
- Edge TTS cần internet nhưng giọng rất tự nhiên
- Có thể chạy music player nhẹ cùng lúc

**Chạy chatbot:**
```bash
# HDMI GUI (KHUYẾN NGHỊ)
./start_hdmi_chatbot.sh

# Hoặc terminal
cd ~/voice-chatbot
source .venv/bin/activate
MIC_TARGET=<source-id> python3 chatbot_vietnamese.py --lang vi
```

**Tính năng đầy đủ:**
- ✅ Giao diện đẹp với mặt Tiến Minh
- ✅ Lịch sử hội thoại realtime
- ✅ Tự động nhận diện ngôn ngữ
- ✅ GPIO buttons
- ✅ Giọng nói tự nhiên

---

## 4️⃣ Pi 4 với 8GB RAM 🏆 TỐI ƯU

### 🚀 Cấu hình cao cấp

**Khả năng:**
- ✅ Chạy cực mượt
- ✅ Độ chính xác tiếng Việt cao nhất (90%)
- ✅ GUI phức tạp + nhiều tính năng
- ✅ Đa nhiệm thoải mái

**Config:**
```bash
WHISPER_MODEL="medium"         # ~5GB RAM - CHẤT LƯỢNG CAO NHẤT
LLM_MODEL="gemma2:2b"          # ~2.5GB RAM - Thông minh
TTS_ENGINE="edge"              # Chất lượng cao + nhiều giọng
GPU_MEM=256
SWAP_SIZE=1024
OMP_THREADS=6
```

**Lệnh cài đặt:**
```bash
./pi4_auto_setup.sh
# Tự động phát hiện 8GB và unlock full power
```

**Khuyến nghị:**
- Có thể thử model lớn hơn
- Chạy nhiều ứng dụng cùng lúc
- Có thể thêm web interface
- Overclock nhẹ nếu có tản nhiệt tốt

**Chạy chatbot:**
```bash
# HDMI GUI với full features
./start_hdmi_chatbot.sh

# Có thể thử model lớn hơn
# Edit config.py:
# LLM_MODEL = "llama3.2:3b"  # Cần pull trước
```

**Tính năng nâng cao:**
- ✅ Multiple voice profiles
- ✅ Conversation history database
- ✅ Web dashboard (tùy chọn)
- ✅ Multiple concurrent users
- ✅ Background music + chatbot cùng lúc

**Thử models khác:**
```bash
# Pull models lớn hơn
ollama pull llama3.2:3b
ollama pull qwen2:1.5b

# Test hiệu năng
ollama run llama3.2:3b "Xin chào, hãy giới thiệu về bản thân"
```

---

## 🔄 So sánh Models

### Whisper Models:

| Model | RAM | Tốc độ | Tiếng Việt | Khuyến nghị |
|-------|-----|--------|------------|-------------|
| tiny | ~400MB | Rất nhanh (1.5s) | 60% | 1GB RAM |
| base | ~1GB | Nhanh (2.5s) | 70% | 2GB RAM |
| **small** | ~2GB | Vừa (4s) | **85%** | **4GB RAM** ⭐ |
| medium | ~5GB | Chậm (8s) | 90% | 8GB RAM |

### LLM Models:

| Model | RAM | Tốc độ | Tiếng Việt | Khuyến nghị |
|-------|-----|--------|------------|-------------|
| tinyllama:1.1b | ~800MB | Nhanh (1-2s) | Tạm được | 1-2GB RAM |
| **qwen2:0.5b** | ~1.5GB | Vừa (2-3s) | **Tốt** | **4GB RAM** ⭐ |
| gemma2:2b | ~2.5GB | Vừa (3-4s) | Rất tốt | 8GB RAM |
| llama3.2:3b | ~4GB | Chậm (5-7s) | Xuất sắc | 8GB RAM |

### TTS Engines:

| Engine | Tốc độ | Chất lượng | Offline | Khuyến nghị |
|--------|--------|------------|---------|-------------|
| espeak | Instant | 50% (giọng máy) | ✅ | 1GB RAM |
| gtts | 1-2s | 80% (tự nhiên) | ❌ | 2GB RAM |
| **edge** | 2-3s | **95% (rất tự nhiên)** | ❌ | **4-8GB RAM** ⭐ |

---

## 💡 Tips tối ưu cho từng RAM

### 1GB RAM:
```bash
# Tắt desktop environment
sudo systemctl set-default multi-user.target
sudo reboot

# Giảm cache
sudo sysctl -w vm.drop_caches=3

# Chỉ chạy chatbot, không mở gì khác
```

### 2GB RAM:
```bash
# Tối ưu swap
echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf

# Tắt services không cần
sudo systemctl disable cups
sudo systemctl disable avahi-daemon
```

### 4GB RAM:
```bash
# Overclock nhẹ (nếu có tản nhiệt)
sudo nano /boot/firmware/config.txt
# Thêm:
# arm_freq=1800
# over_voltage=2

sudo reboot
```

### 8GB RAM:
```bash
# Tăng hiệu suất tối đa
sudo nano /boot/firmware/config.txt
# Thêm:
# arm_freq=2000
# gpu_freq=600
# over_voltage=4

# Cần tản nhiệt tốt!
sudo reboot
```

---

## 🎯 Kết luận

| RAM | Trải nghiệm | Khuyến nghị |
|-----|-------------|-------------|
| 1GB | Cơ bản, hạn chế | Chỉ dùng nếu không có lựa chọn khác |
| 2GB | Tạm ổn | Có thể dùng được với model nhẹ |
| **4GB** | **Rất tốt** | **🏆 KHUYẾN NGHỊ - Tốt nhất cho hầu hết người dùng** |
| 8GB | Tuyệt vời | Dành cho người muốn chất lượng cao nhất |

**Lời khuyên:** Nếu đang định mua Pi 4, chọn **phiên bản 4GB** để có trải nghiệm tốt nhất với chatbot tiếng Việt!

