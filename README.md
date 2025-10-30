# Tiến Minh — Vietnamese Voice Assistant (Raspberry Pi Voice Chatbot)

## 🚀 HƯỚNG DẪN NHANH CHO PI 4 (MỚI!)

### ⚡ Cài đặt tự động (1 lệnh - KHUYẾN NGHỊ):
```bash
cd ~
git clone https://github.com/YOUR_USERNAME/voice-chatbot.git
cd voice-chatbot
chmod +x pi4_auto_setup.sh
./pi4_auto_setup.sh
# Script sẽ tự động phát hiện RAM và cấu hình tối ưu!
```

📖 **Xem hướng dẫn đơn giản:** [QUICKSTART_PI4.md](QUICKSTART_PI4.md)  
🔧 **Tối ưu hóa chi tiết:** [PI4_OPTIMIZATION_GUIDE.md](PI4_OPTIMIZATION_GUIDE.md)

### 🎯 Tương thích với tất cả Pi 4:
- ✅ **Pi 4 1GB** - Chạy được với model nhẹ
- ✅ **Pi 4 2GB** - Chạy tốt với model base
- ✅ **Pi 4 4GB** - Chạy rất tốt với model small ⭐ KHUYẾN NGHỊ
- ✅ **Pi 4 8GB** - Chạy mượt với model medium 🏆

---

## Hướng dẫn cài đặt CHI TIẾT cho Raspberry Pi 4 Model B (Tất cả phiên bản RAM)

> **Thông tin quan trọng**
>
> Phiên bản này được tối ưu hóa cho **TẤT CẢ** Raspberry Pi 4 Model B (1GB/2GB/4GB/8GB RAM) với khả năng nhận diện và phát giọng nói tiếng Việt.
> Bao gồm tích hợp Whisper model hỗ trợ tiếng Việt và TTS engine cho tiếng Việt.
> 
> **Script tự động** sẽ phát hiện RAM và chọn cấu hình phù hợp!

---

## Contents

- [3D Printed Parts](#3d-printed-parts)
- [Step 1 — Audio, Bluetooth & Chatbot Base](#step-1--audio-bluetooth--chatbot-base)
  - [1. System packages](#1-system-packages)
  - [2. Enable services](#2-enable-services)
  - [3. Bluetooth speaker setup](#3-bluetooth-speaker-setup)
  - [4. USB microphone setup](#4-usb-microphone-setup)
  - [5. Project & Python deps](#5-project--python-deps)
  - [6. Install Ollama & model](#6-install-ollama--model)
  - [7. Create & run `chatbot.py`](#7-create--run-chatbotpy)
- [Step 2 — SPI Display (Waveshare) & "Tiến Minh" Chat](#step-2--spi-display-waveshare--tiến-minh-chat)
  - [1. Enable SPI & groups, reboot](#1-enable-spi--groups-reboot)
  - [2. Display packages (Pi 5 note)](#2-display-packages-pi-5-note)
  - [3. Waveshare driver](#3-waveshare-driver)
  - [4. Use project venv](#4-use-project-venv)
  - [5. Python deps for display](#5-python-deps-for-display)
  - [6. Test Waveshare demo](#6-test-waveshare-demo)
  - [7. Create `bobchat.py`](#7-create-bobchatpy)
  - [8. Link driver lib & sprites; run](#8-link-driver-lib--sprites-run)
- [Quick Reference](#quick-reference)
- [Notes](#notes)

---

## 3D Printed Parts

All print files are available here:  
**Printables:** <https://www.printables.com/model/1404129-bob-the-sentient-washing-machine>

A **limited number of pre‑printed kits** (including screens, switches, and microphones) are available here **[ominousindustries.com](https://ominousindustries.com/collections/robots/products/bob-the-sentient-washing-machine-parts-kit-no-pi-included)**.

---

## Step 1 — Audio, Bluetooth & Chatbot Base (Raspberry Pi 4 - Vietnamese Support)

### 1) System packages

~~~bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Core tools, audio stack, BT, and TTS with Vietnamese support
sudo apt install -y \
  git python3-venv python3-pip \
  python3-gpiozero python3-rpi.gpio \
  bluez \
  pipewire pipewire-pulse wireplumber \
  espeak-ng espeak-ng-data \
  festival festival-vi \
  libportaudio2 \
  alsa-utils \
  libspa-0.2-bluetooth \
  ffmpeg \
  libavcodec-extra \
  language-pack-vi \
  fonts-noto-cjk

# Install Vietnamese TTS support
sudo apt install -y festival-vi espeak-ng-vi

# Add user to audio group for device permissions
sudo usermod -aG audio $USER

# Set Vietnamese locale support
sudo locale-gen vi_VN.UTF-8

# Reboot for group membership to take effect
sudo reboot
~~~

> After reboot, log back in and continue.

---

### 2) Enable services

~~~bash
# Enable Bluetooth system service
sudo systemctl enable --now bluetooth

# Start PipeWire audio stack for your user
systemctl --user enable --now pipewire wireplumber pipewire-pulse

# Keep user services running even when not logged in (headless)
sudo loginctl enable-linger $USER

# Verify PipeWire is up
systemctl --user status pipewire
~~~

---

### 3) Bluetooth speaker setup

~~~bash
# Enter the Bluetooth controller
bluetoothctl
~~~

Inside the `bluetoothctl` prompt, run:

~~~
power on
agent on
default-agent
scan on
# Wait until your speaker appears; note its MAC XX:XX:XX:XX:XX:XX

pair XX:XX:XX:XX:XX:XX
trust XX:XX:XX:XX:XX:XX
connect XX:XX:XX:XX:XX:XX
exit
~~~

Set as default output and test:

~~~bash
# List PipeWire nodes; note your speaker's Sink ID
wpctl status

# Set default output (replace <sink-id> with the ID you noted)
wpctl set-default <sink-id>

# Test sound output
pw-play /usr/share/sounds/alsa/Front_Center.wav
~~~

---

### 4) USB microphone setup

~~~bash
# Plug in the USB mic, then list audio Sources
wpctl status

# Note the Source ID for your USB mic (e.g., 66) and set it as default:
wpctl set-default <source-id>

# Quick record test from the default source
pw-record --rate 44100 --channels 1 test.wav
# Speak ~3 seconds, then Ctrl+C

# Play back through default sink (BT speaker)
pw-play test.wav
~~~

---

### 5) Project & Python deps (với hỗ trợ tiếng Việt)

~~~bash
# Create project
mkdir -p ~/voice-chatbot
cd ~/voice-chatbot

# Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install packages with Vietnamese support
pip install --upgrade pip
pip install faster-whisper ollama numpy
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install openai-whisper
pip install gTTS
pip install pygame
pip install pydub
pip install SpeechRecognition
pip install pyaudio

# Advanced Vietnamese TTS engines
pip install gtts-token
pip install edge-tts  # Microsoft Edge TTS (high quality Vietnamese voices)
pip install pyttsx3   # Cross-platform TTS
pip install requests  # For API-based TTS services

# Optional: thread tuning for Faster-Whisper optimized for Pi 4 8GB
echo 'export OMP_NUM_THREADS=6' >> ~/.bashrc
echo 'export MKL_NUM_THREADS=6' >> ~/.bashrc
source ~/.bashrc

# Ensure venv is active for the rest of the setup
source .venv/bin/activate
~~~

---

### 6) Install Ollama & model (tối ưu cho Pi 4)

~~~bash
# Install Ollama server
curl -fsSL https://ollama.com/install.sh | sh

# Enable and start the Ollama daemon
sudo systemctl enable --now ollama

# Download models optimized for Pi 4 8GB RAM and Vietnamese support
# Sử dụng model nhỏ hơn để tối ưu cho Pi 4
ollama pull tinyllama:1.1b
ollama pull qwen2:0.5b

# Download Vietnamese-capable model (if available)
ollama pull gemma2:2b

# Verify it responds in Vietnamese
ollama run qwen2:0.5b "Chào bạn, bạn có khỏe không?"

# Test English response
ollama run tinyllama:1.1b "Hello, how are you?"
~~~

---

### 7) Create & run `chatbot.py`

~~~bash
# Create the chatbot script (paste in the chatbot.py script from the repo)
nano chatbot.py
~~~

Find your mic Source ID via `wpctl status`, then launch:

~~~bash
# Example: MIC_TARGET=66 (replace with your actual Source ID)
MIC_TARGET=66 python3 chatbot.py
~~~

---

## 🎯 Cách sử dụng đơn giản

### Chạy với màn hình HDMI (khuyến nghị):
```bash
# Khởi chạy script tự động
./start_hdmi_chatbot.sh

# Sẽ hiển thị giao diện chatbot trên màn hình HDMI
# Giao diện bao gồm:
# - Mặt Tiến Minh thay đổi khi nói
# - Lịch sử đàm thoại
# - Trạng thái microphone/TTS
# - Hướng dẫn sử dụng
```

### Chạy với màn hình LCD (nâng cao):
```bash
# Sử dụng script bob với LCD
./start_vietnamese_chatbot.sh
```

---

## 📺 Chatbot với màn hình HDMI - Hướng dẫn chi tiết

### Giới thiệu
Phiên bản `hdmi_chatbot_vietnamese.py` được thiết kế đặc biệt cho những ai **KHÔNG có màn hình LCD SPI** mà chỉ sử dụng màn hình HDMI thông thường.

### Tính năng chính:
- 🖥️ **Giao diện đồ họa**: Hiển thị trên màn hình HDMI với GUI đẹp mắt
- 🤖 **Mặt Tiến Minh**: Biểu hiện cảm xúc khi nói chuyện  
- 📝 **Lịch sử hội thoại**: Hiển thị 8 tin nhắn gần nhất
- 🎤 **Trạng thái real-time**: Hiển thị trạng thái micro, TTS
- 🎛️ **GPIO Buttons**: Hỗ trợ nút dừng (GPIO 22), tạm dừng (GPIO 23), tiếp tục (GPIO 24)
- 🌐 **Đa ngôn ngữ**: Hỗ trợ Tiếng Việt, English, và tự động nhận diện

### Yêu cầu hệ thống:
- Raspberry Pi 4 Model B với 8GB RAM
- Màn hình HDMI (bất kỳ kích thước nào)
- USB microphone  
- Bluetooth speakers hoặc 3.5mm audio output
- Desktop environment (Raspberry Pi OS with Desktop)

### Cài đặt phụ thuộc cho HDMI version:
```bash
# Cài đặt pygame cho giao diện đồ họa
pip install pygame

# Các package đồ họa cần thiết
sudo apt install -y python3-pygame
sudo apt install -y fonts-dejavu fonts-liberation
sudo apt install -y python3-opencv

# Nếu cần fonts tiếng Việt đẹp hơn
sudo apt install -y fonts-noto-cjk
```

### Khởi chạy:
```bash
# Cách 1: Sử dụng script tự động (khuyến nghị)
./start_hdmi_chatbot.sh

# Cách 2: Chạy trực tiếp
python3 hdmi_chatbot_vietnamese.py --lang vi

# Cách 3: Với tùy chọn microphone cụ thể  
python3 hdmi_chatbot_vietnamese.py --lang vi --mic-target alsa_input.usb-0123456789ABCDEF-00.mono-fallback
```

---

## 🚀 Cài đặt và Chạy

**⚠️ LỰA CHỌN HIỂN THỊ:**
- **SPI LCD (1.28 inch)**: Sử dụng `bobchat_vietnamese.py` nếu bạn có màn hình LCD nhỏ
- **HDMI Monitor**: Sử dụng `hdmi_chatbot_vietnamese.py` cho màn hình HDMI thông thường ✅ **ĐƯỢC KHUYẾN NGHỊ**

### Tùy chọn A: Với màn hình HDMI thông thường 🖥️ (Dễ sử dụng)

```bash
# Khởi chạy chatbot với giao diện HDMI
./start_hdmi_chatbot.sh

# Hoặc chạy trực tiếp với tùy chọn
python3 hdmi_chatbot_vietnamese.py --lang vi
```

**Ưu điểm của phiên bản HDMI:**
- ✅ Không cần màn hình LCD đặc biệt
- ✅ Giao diện đẹp trên màn hình lớn
- ✅ Hiển thị lịch sử đàm thoại
- ✅ Trạng thái thời gian thực
- ✅ Dễ cài đặt hơn

---

### Tùy chọn B: Với màn hình SPI LCD (1.28 inch) 📱 (Nâng cao)

#### 1) Enable SPI & groups, reboot

~~~bash
# Enable SPI in raspi-config:
sudo raspi-config   # Interface Options → SPI → Enable

# Add your user to GPIO/SPI groups
sudo usermod -a -G gpio,spi $USER

# Reboot to apply
sudo reboot
~~~

> After reboot, log back in and continue.

---

#### 2) Display packages (Pi 4 optimized)

~~~bash
# For Raspberry Pi 4, install required packages without removing RPi.GPIO
sudo apt install -y python3-pip unzip wget git

# Pi 4 specific GPIO libraries (keep legacy RPi.GPIO for compatibility)
sudo apt install -y python3-rpi.gpio python3-gpiozero

# Optional: Install lgpio for newer compatibility (can coexist with RPi.GPIO)
sudo apt install -y python3-lgpio

# Install additional packages for LCD display
sudo apt install -y python3-spidev python3-dev
~~~

> **Note**: Pi 4 works best with the traditional `RPi.GPIO` library. We keep it installed for maximum compatibility.

---

### 3) Waveshare driver

~~~bash
cd ~
wget https://files.waveshare.com/upload/8/8d/LCD_Module_RPI_code.zip
unzip -o LCD_Module_RPI_code.zip
~~~

---

### 4) Use project venv

~~~bash
# Reuse the existing project venv (create only if it doesn't exist)
cd ~/voice-chatbot
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
~~~

---

### 5) Python deps for display (Pi 4)

~~~bash
# Install display-related Python packages into the project venv for Pi 4
pip install pillow numpy spidev gpiozero

# Pi 4 specific: Install RPi.GPIO for traditional GPIO control
pip install RPi.GPIO

# Optional: Install newer GPIO libraries for future compatibility
pip install rpi-lgpio lgpio

# For Pi 4, use the default pin factory (RPi.GPIO)
# No need to set GPIOZERO_PIN_FACTORY unless you want to use lgpio specifically
~~~

---

### 6) Test Waveshare demo

~~~bash
# From inside the venv
cd ~/LCD_Module_RPI_code/RaspberryPi/python/example
python3 1inch28_LCD_test.py
~~~

---

### 7) Create `bobchat.py`

~~~bash
cd ~/voice-chatbot

# Create the Bob chat script (paste in the bobchat.py script from the repo)
nano bobchat.py

# Save and exit
~~~

---

### 8) Link driver lib & sprites; run

~~~bash
# Link Waveshare Python lib into the project for imports
ln -s "$HOME/LCD_Module_RPI_code/RaspberryPi/python/lib" "$HOME/voice-chatbot/lib"

# Sprites/images for Bob UI (optional but recommended)
git clone https://github.com/OminousIndustries/Bob_Images.git ~/voice-chatbot/sprites

# Run Bob chat (replace with your mic Source ID)
MIC_TARGET=<source-id> python3 bobchat.py
~~~

---

## Quick Reference

~~~bash
# Devices & routing
wpctl status
wpctl set-default <sink-or-source-id>

# Audio tests
pw-play /usr/share/sounds/alsa/Front_Center.wav
pw-record --rate 44100 --channels 1 test.wav

# Bluetooth pairing (inside bluetoothctl)
power on
agent on
default-agent
scan on
pair XX:XX:XX:XX:XX:XX
trust XX:XX:XX:XX:XX:XX
connect XX:XX:XX:XX:XX:XX
exit

# Core services
sudo systemctl enable --now bluetooth
systemctl --user enable --now pipewire wireplumber pipewire-pulse
sudo loginctl enable-linger $USER

# Ollama
sudo systemctl enable --now ollama
ollama pull gemma3:270m
ollama run gemma3:270m "Say hello"
~~~

---

## Cấu hình bổ sung cho tiếng Việt trên Raspberry Pi 4

### 1) Cài đặt font tiếng Việt cho LCD

~~~bash
# Cài đặt font tiếng Việt
sudo apt install -y fonts-dejavu fonts-noto-cjk fonts-liberation
sudo apt install -y ttf-ancient-fonts fonts-vlgothic

# Cập nhật font cache
sudo fc-cache -fv
~~~

### 2) Tối ưu hóa bộ nhớ cho Pi 4 8GB

~~~bash
# Tăng GPU memory split cho xử lý đồ họa LCD tốt hơn
echo "gpu_mem=128" | sudo tee -a /boot/firmware/config.txt

# Tối ưu hóa swap cho AI models
echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf

# Khởi động lại để áp dụng thay đổi
sudo reboot
~~~

### 3) Cài đặt và test TTS tiếng Việt nâng cao

~~~bash
cd ~/voice-chatbot
source .venv/bin/activate

# Cài đặt Edge TTS cho giọng nói tiếng Việt chất lượng cao
pip install edge-tts

# Test các TTS engine có sẵn
python3 test_vietnamese_tts.py

# Cài đặt thêm các engine TTS offline
sudo apt install -y espeak-ng-vi festival-vi

# Test giọng đọc espeak tiếng Việt
espeak-ng -v vi "Xin chào, đây là test giọng nói tiếng Việt"

# Test Edge TTS (cần internet)
edge-tts --voice vi-VN-HoaiMyNeural --text "Xin chào, tôi là giọng nói tiếng Việt chất lượng cao" --write-media test.mp3 && mpv test.mp3
~~~

### 4) Chạy chatbot tiếng Việt

~~~bash
cd ~/voice-chatbot
source .venv/bin/activate

# Chạy phiên bản cơ bản với TTS nâng cao
MIC_TARGET=<source-id> python3 chatbot_vietnamese.py --lang vi

# Chạy phiên bản có LCD với hỗ trợ tiếng Việt
MIC_TARGET=<source-id> python3 bobchat_vietnamese.py --lang vi

# Chạy với tự động phát hiện ngôn ngữ (Việt/Anh)
MIC_TARGET=<source-id> python3 chatbot_vietnamese.py --lang auto

# Chạy với script khởi động tự động
./start_vietnamese_chatbot.sh
~~~

### 5) Kiểm tra hệ thống Pi 4

~~~bash
# Chạy script kiểm tra toàn diện cho Pi 4
./pi4_system_check.sh

# Script này sẽ kiểm tra:
# - Model Pi và RAM
# - GPIO/SPI support  
# - Audio system (PipeWire)
# - Bluetooth
# - TTS engines
# - AI models
# - Font tiếng Việt
# - Hiệu năng và nhiệt độ
~~~

### 6) Kiểm tra và debug chi tiết

~~~bash
# Test microphone
python3 chatbot_vietnamese.py --test

# Test toàn bộ các TTS engine
python3 test_vietnamese_tts.py

# Kiểm tra model Ollama
ollama list
ollama run qwen2:0.5b "Xin chào, bạn có khỏe không?"

# Kiểm tra từng TTS engine riêng lẻ

# 1. Test gTTS (Google TTS - cần internet)
python3 -c "
from gtts import gTTS
import pygame
pygame.mixer.init()
tts = gTTS('Xin chào, tôi là Tiến Minh', lang='vi')
tts.save('test_vi.mp3')
pygame.mixer.music.load('test_vi.mp3')
pygame.mixer.music.play()
import time; time.sleep(3)
"

# 2. Test Edge TTS (Microsoft - cần internet, chất lượng cao)
edge-tts --voice vi-VN-HoaiMyNeural --text "Xin chào, tôi là Tiến Minh với giọng nói chất lượng cao" --write-media test_edge.mp3
mpv test_edge.mp3

# 3. Test espeak-ng (offline, nhanh)
espeak-ng -v vi -s 150 "Xin chào, tôi là Bob với espeak tiếng Việt"

# 4. Test festival (offline, chất lượng trung bình)
echo "Xin chào từ Festival" | festival --tts --language vietnamese

# Benchmark tốc độ các TTS engine
python3 -c "
from vietnamese_tts import VietnameseTTS
import time
tts = VietnameseTTS()
for engine in tts.get_available_engines():
    print(f'Testing {engine}...')
    start = time.time()
    tts.speak('Test tốc độ TTS', engine=engine)
    print(f'{engine}: {time.time()-start:.2f}s')
"
~~~

## Notes

- **Thay thế các placeholder**: `<sink-id>`, `<source-id>`, và `XX:XX:XX:XX:XX:XX` bằng giá trị thực từ `wpctl status` và `bluetoothctl`.
- **Kích hoạt lại venv**: Trong shell mới: `source ~/voice-chatbot/.venv/bin/activate`.
- **Pi 4 optimization**: Sử dụng `lgpio`/`rpi-lgpio` thay vì legacy `RPi.GPIO`.
- **Vietnamese models**: Sử dụng model `small` cho Whisper để hỗ trợ tiếng Việt tốt hơn.
- **Memory management**: Pi 4 8GB đủ để chạy model `qwen2:0.5b` và `small` Whisper đồng thời.
- **Language switching**: Chatbot có thể tự động chuyển đổi giữa tiếng Việt và tiếng Anh.

## Troubleshooting cho Pi 4

### Lỗi GPIO/SPI trên Pi 4
~~~bash
# Kiểm tra SPI đã được kích hoạt
lsmod | grep spi
# Nếu không có kết quả, kích hoạt SPI
sudo raspi-config  # Interface Options → SPI → Enable

# Kiểm tra quyền truy cập GPIO
groups $USER  # Phải có gpio, spi trong danh sách
# Nếu không có:
sudo usermod -a -G gpio,spi $USER
sudo reboot

# Test GPIO cơ bản
python3 -c "
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
print('GPIO works!')
GPIO.cleanup()
"
~~~

### Lỗi LCD display không hoạt động
~~~bash
# Kiểm tra kết nối SPI
ls /dev/spi*  # Phải có /dev/spidev0.0, /dev/spidev0.1

# Test SPI basic
python3 -c "
import spidev
spi = spidev.SpiDev()
spi.open(0, 0)
print('SPI works!')
spi.close()
"

# Kiểm tra thư viện Waveshare
cd ~/LCD_Module_RPI_code/RaspberryPi/python/example
python3 1inch28_LCD_test.py
~~~

### Lỗi memory không đủ cho Pi 4
~~~bash
# Giảm kích thước model
ollama pull tinyllama:1.1b  # Model nhỏ hơn
# Hoặc sử dụng Whisper tiny thay vì small

# Tối ưu hóa Pi 4 memory
echo "gpu_mem=64" | sudo tee -a /boot/firmware/config.txt  # Giảm GPU mem nếu không dùng desktop
echo "arm_freq=1800" | sudo tee -a /boot/firmware/config.txt  # Tăng CPU frequency (nếu có tản nhiệt tốt)
sudo reboot

# Monitor memory usage
free -h
htop
~~~

### Lỗi âm thanh tiếng Việt
~~~bash
# Cài đặt espeak-ng Vietnamese
sudo apt install espeak-ng-vi
espeak-ng -v vi "Xin chào"

# Kiểm tra PipeWire status
systemctl --user status pipewire
wpctl status

# Test audio output
speaker-test -t wav -c 2
~~~

### Lỗi font LCD tiếng Việt
~~~bash
# Kiểm tra font tiếng Việt
fc-list :lang=vi
# Cài thêm font nếu cần
sudo apt install fonts-noto-color-emoji fonts-dejavu-extra

# Test font trong Python
python3 -c "
from PIL import Image, ImageDraw, ImageFont
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    print('Vietnamese font available!')
except:
    print('Font not found, using default')
"
~~~

### Lỗi GPIO pin factory cho Pi 4
~~~bash
# Nếu gặp lỗi với gpiozero, thử các factory khác nhau:

# Sử dụng RPi.GPIO (mặc định cho Pi 4)
export GPIOZERO_PIN_FACTORY=rpigpio
python3 your_script.py

# Hoặc thử lgpio (mới hơn)
export GPIOZERO_PIN_FACTORY=lgpio
python3 your_script.py

# Kiểm tra factory hiện tại
python3 -c "
from gpiozero.pins import pi
print(f'Current pin factory: {pi.pin_factory}')
"
~~~
