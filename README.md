# Bob — The Sentient Washing Machine (Raspberry Pi Voice Chatbot - Vietnamese Version)

## Hướng dẫn cài đặt cho Raspberry Pi 4 Model B 8GB RAM với hỗ trợ tiếng Việt

> **Thông tin quan trọng**
>
> Phiên bản này được tối ưu hóa cho Raspberry Pi 4 Model B 8GB RAM với khả năng nhận diện và phát giọng nói tiếng Việt.
> Bao gồm tích hợp Whisper model hỗ trợ tiếng Việt và TTS engine cho tiếng Việt.

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
- [Step 2 — SPI Display (Waveshare) & “Bob” Chat](#step-2--spi-display-waveshare--bob-chat)
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

## Step 2 — SPI Display (Waveshare) & “Bob” Chat

### 1) Enable SPI & groups, reboot

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

### 2) Display packages (Pi 5 note)

~~~bash
# On a Raspberry Pi 5, remove legacy RPi.GPIO first:
sudo apt purge -y python3-rpi.gpio
sudo apt autoremove -y

# Install required packages
sudo apt install -y python3-pip unzip wget git python3-lgpio
~~~

> If you are **not** on a Pi 5, you can skip the purge step.

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

### 5) Python deps for display

~~~bash
# Install display-related Python packages into the project venv
pip install pillow numpy spidev gpiozero rpi-lgpio lgpio

# (Optional) Use lgpio pin factory for gpiozero
export GPIOZERO_PIN_FACTORY=lgpio
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

### 5) Kiểm tra và debug

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
tts = gTTS('Xin chào, tôi là Bob', lang='vi')
tts.save('test_vi.mp3')
pygame.mixer.music.load('test_vi.mp3')
pygame.mixer.music.play()
import time; time.sleep(3)
"

# 2. Test Edge TTS (Microsoft - cần internet, chất lượng cao)
edge-tts --voice vi-VN-HoaiMyNeural --text "Xin chào, tôi là Bob với giọng nói chất lượng cao" --write-media test_edge.mp3
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

### Lỗi memory không đủ
~~~bash
# Giảm kích thước model
ollama pull tinyllama:1.1b  # Model nhỏ hơn
# Hoặc sử dụng Whisper tiny thay vì small
~~~

### Lỗi âm thanh tiếng Việt
~~~bash
# Cài đặt espeak-ng Vietnamese
sudo apt install espeak-ng-vi
espeak-ng -v vi "Xin chào"
~~~

### Lỗi font LCD
~~~bash
# Kiểm tra font tiếng Việt
fc-list :lang=vi
# Cài thêm font nếu cần
sudo apt install fonts-noto-color-emoji
~~~
