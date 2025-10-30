# 🔧 FIX: Package Installation Errors on Pi OS

## ❌ Lỗi: libatlas-base-dev không có sẵn

### Nguyên nhân:
Package `libatlas-base-dev` đã **obsolete** (lỗi thời) trên Pi OS Bookworm (mới nhất từ 2023).

## ❌ Lỗi: language-pack-vi không có sẵn

### Nguyên nhân:
Package `language-pack-vi` là package của **Ubuntu/Debian desktop**, không có trên **Raspberry Pi OS**.

**Không cần cài đặt** - Pi OS đã hỗ trợ UTF-8 và tiếng Việt mặc định. Chỉ cần cài fonts:
```bash
sudo apt install -y fonts-noto-cjk fonts-noto-cjk-extra fonts-dejavu
```

### Thay thế:

#### Option 1: Dùng script tự động fix (KHUYẾN NGHỊ)
```bash
cd ~/voice-chatbot
chmod +x install_packages.sh
./install_packages.sh
```

Script này sẽ:
- Tự động phát hiện packages có sẵn
- Cài đặt alternatives nếu package gốc không có
- Verify tất cả installations

#### Option 2: Cài đặt thủ công với packages thay thế
```bash
# Update package list
sudo apt update

# Cài đặt math libraries (thay libatlas-base-dev)
sudo apt install -y libopenblas-dev libblas-dev liblapack-dev gfortran

# Core packages
sudo apt install -y \
  build-essential \
  cmake \
  git \
  python3-dev \
  python3-pip \
  python3-venv

# Audio
sudo apt install -y \
  libportaudio2 \
  portaudio19-dev \
  ffmpeg \
  libsndfile1 \
  flac \
  alsa-utils

# PipeWire (thay PulseAudio trên Pi OS mới)
sudo apt install -y \
  pipewire \
  pipewire-pulse \
  wireplumber

# Bluetooth
sudo apt install -y \
  bluez \
  bluez-tools

# TTS
sudo apt install -y \
  espeak-ng \
  festival

# Fonts
sudo apt install -y \
  fonts-noto-cjk \
  fonts-dejavu
```

#### Option 3: Chạy lại auto setup (đã fix)
```bash
cd ~/voice-chatbot
git pull  # Lấy bản update mới nhất
chmod +x pi4_auto_setup.sh
./pi4_auto_setup.sh
```

---

## 📋 Package Mapping (Old → New)

| Old Package (Buster) | New Package (Bookworm) | Purpose |
|---------------------|----------------------|---------|
| `libatlas-base-dev` | `libopenblas-dev` | BLAS library |
| (same) | `libblas-dev` | Basic BLAS |
| (same) | `liblapack-dev` | Linear algebra |
| `pulseaudio` | `pipewire` | Audio server |
| `pulseaudio-module-bluetooth` | `libspa-0.2-bluetooth` | BT audio |

---

## 🧪 Verify Installation

```bash
# Check packages đã cài
dpkg -l | grep -E "openblas|blas|lapack"
dpkg -l | grep -E "portaudio|ffmpeg|alsa"
dpkg -l | grep -E "pipewire|bluetooth"
dpkg -l | grep espeak

# Test Python packages
python3 --version
pip3 --version

# Test audio
aplay -l
arecord -l
```

---

## 🔄 Nếu vẫn lỗi

### 1. Kiểm tra Pi OS version:
```bash
cat /etc/os-release
```

Nếu thấy:
- **VERSION_ID="12"** → Bookworm (mới) ✅
- **VERSION_ID="11"** → Bullseye (cũ)
- **VERSION_ID="10"** → Buster (rất cũ)

### 2. Update Pi OS (nếu quá cũ):
```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

### 3. Enable all repositories:
```bash
sudo nano /etc/apt/sources.list
```

Đảm bảo có dòng:
```
deb http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware
```

Sau đó:
```bash
sudo apt update
```

### 4. Bỏ qua package và dùng pip:
Nếu không cài được system packages, có thể dùng Python packages:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install numpy scipy  # Thay cho libatlas/libblas
```

---

## 📊 Tương thích Pi OS versions

### Bookworm (12) - 2023+ (Khuyến nghị)
```bash
# Packages có sẵn
libopenblas-dev ✅
libblas-dev ✅
pipewire ✅
wireplumber ✅

# Packages không có
libatlas-base-dev ❌ (obsolete)
```

### Bullseye (11) - 2021-2023
```bash
# Packages có sẵn
libatlas-base-dev ✅
libopenblas-dev ✅
pulseaudio ✅

# Packages không có
wireplumber ❌ (chưa có)
```

### Buster (10) - 2019-2021 (Cũ)
```bash
# Nên upgrade lên Bookworm
sudo apt update
sudo apt full-upgrade
```

---

## ✅ Quick Fix Command

Copy/paste lệnh này để fix ngay:

```bash
# Fix all package issues
sudo apt update && \
sudo apt install -y \
  build-essential cmake git \
  python3-dev python3-pip python3-venv \
  libopenblas-dev libblas-dev liblapack-dev gfortran \
  libportaudio2 portaudio19-dev \
  ffmpeg libsndfile1 flac alsa-utils \
  pipewire pipewire-pulse wireplumber \
  bluez espeak-ng \
  fonts-noto-cjk fonts-dejavu && \
echo "✅ All packages installed!"
```

Nếu có lỗi `unable to locate package`, bỏ qua và tiếp tục.

---

## 🎯 Sau khi fix packages

```bash
# Tiếp tục với auto setup
cd ~/voice-chatbot
./pi4_auto_setup.sh

# Hoặc chạy manual
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 📞 Vẫn gặp lỗi?

### Chạy diagnostic script:
```bash
cd ~/voice-chatbot
chmod +x install_packages.sh
./install_packages.sh 2>&1 | tee install.log
```

Sau đó xem `install.log` để biết package nào fail.

### Hoặc skip system packages:
```bash
# Chỉ cài Python packages (không cần system packages)
python3 -m venv .venv
source .venv/bin/activate

# Numpy sẽ tự build nếu thiếu BLAS
pip install numpy --no-binary numpy

# Tiếp tục
pip install -r requirements.txt
```

⚠️ **Lưu ý:** Build từ source sẽ chậm hơn (10-30 phút) nhưng chắc chắn chạy được!

---

**TL;DR:** 
```bash
cd ~/voice-chatbot
chmod +x install_packages.sh
./install_packages.sh
```

✅ Done!

