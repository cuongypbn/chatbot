#!/usr/bin/env python3
"""
Voice Chatbot with LCD Face Animation - Vietnamese Support
Shows resting face sprite when idle, animates speech sprites during TTS
Optimized for Raspberry Pi 4 Model B 8GB RAM with Vietnamese language support
"""

import sys
import os
import signal
import time
import subprocess
import wave
import numpy as np
from pathlib import Path
import ollama
from faster_whisper import WhisperModel
from gtts import gTTS
import pygame
import tempfile
import threading
import spidev as SPI
import re

# --- locate Waveshare driver relative to this script (fallback to your absolute path) ---
SCRIPT_DIR = Path(__file__).resolve().parent
WS_PATH_1 = SCRIPT_DIR / "LCD_Module_RPI_code" / "RaspberryPi" / "python"
WS_PATH_2 = Path("/home/voice-chatbot/LCD_Module_RPI_code/RaspberryPi/python")
if (WS_PATH_1 / "lib" / "LCD_1inch28.py").exists():
    sys.path.insert(0, str(WS_PATH_1))
elif (WS_PATH_2 / "lib" / "LCD_1inch28.py").exists():
    sys.path.insert(0, str(WS_PATH_2))

from lib import LCD_1inch28
from PIL import Image, ImageDraw, ImageFont

# Optional GPIO stop button (Pi 4 optimized)
try:
    from gpiozero import Button
    GPIO_AVAILABLE = True
    # For Pi 4, use default pin factory (RPi.GPIO)
    import os
    if not os.environ.get('GPIOZERO_PIN_FACTORY'):
        os.environ['GPIOZERO_PIN_FACTORY'] = 'rpigpio'
except ImportError:
    GPIO_AVAILABLE = False
    print("📝 GPIO not available - running without button support")

# ===== LCD Configuration =====
RST = 27
DC = 25
BL = 18
bus = 0
device = 0

# ===== Sprite paths (script-relative) =====
SPRITE_DIR = SCRIPT_DIR / "sprites"
RESTING_SPRITE = SPRITE_DIR / "image.png"
SPEECH_SPRITES = [
    SPRITE_DIR / "image1.png",
    SPRITE_DIR / "image2.png",
    SPRITE_DIR / "image3.png"
]

# ===== Configuration =====
STOP_BUTTON_PIN = 22

# Preferred capture settings (optimized for Pi 4)
PREF_SAMPLE_RATE = 16000
PREF_CHANNELS = 1

# VAD settings
FRAME_MS = 30
SILENCE_THRESHOLD = 120   # Base RMS
END_SILENCE_MS = 800
MIN_SPEECH_MS = 300
MAX_RECORDING_MS = 15000

# Models (optimized for Pi 4 8GB)
WHISPER_MODEL = "small"  # Better Vietnamese support
LLM_MODEL = "qwen2:0.5b"  # Lightweight model with better multilingual support
FALLBACK_LLM_MODEL = "tinyllama:1.1b"

# Language settings
DEFAULT_LANGUAGE = "vi"  # Vietnamese by default
SUPPORTED_LANGUAGES = ["vi", "en", "auto"]

# Conversation
AUTO_RESTART_DELAY = 1.5
VIETNAMESE_WAKE_WORDS = ["xin chào", "chào bạn", "hey trợ lý", "trợ lý ơi"]
ENGLISH_WAKE_WORDS = ["hey computer", "okay computer", "hey assistant"]

# Temp file
TEMP_WAV = Path("/tmp/recording.wav")

# Optional: force a specific PipeWire source (id or name)
MIC_TARGET = os.environ.get("MIC_TARGET")

# Global variables for LCD animation and language
lcd_disp = None
animation_thread = None
stop_animation = threading.Event()
current_language = DEFAULT_LANGUAGE

# ===== Pause/Resume Buttons =====
PAUSE_BUTTON_PIN = 23
RESUME_BUTTON_PIN = 24

# Global pause flag
paused = threading.Event()

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# ===== Language Detection =====
def detect_language(text):
    """Simple language detection based on Vietnamese characters"""
    vietnamese_chars = re.findall(r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', text.lower())
    if len(vietnamese_chars) > 0:
        return "vi"
    return "en"

# ===== LCD Functions =====
def init_lcd():
    """Initialize the LCD display"""
    global lcd_disp
    try:
        lcd_disp = LCD_1inch28.LCD_1inch28()
        lcd_disp.Init()
        lcd_disp.clear()
        lcd_disp.bl_DutyCycle(50)  # Set backlight to 50%
        print("📱 LCD display initialized")
        return True
    except Exception as e:
        print(f"⚠️ LCD initialization failed: {e}")
        return False

def show_sprite(sprite_path):
    """Display a single sprite on the LCD"""
    global lcd_disp
    if lcd_disp is None:
        return

    try:
        if sprite_path.exists():
            image = Image.open(str(sprite_path))
            # Resize if necessary to fit the display (240x240)
            image = image.resize((lcd_disp.width, lcd_disp.height), Image.Resampling.LANCZOS)
            lcd_disp.ShowImage(image)
        else:
            print(f"⚠️ Sprite not found: {sprite_path}")
            # Show a placeholder colored screen if sprite missing
            placeholder = Image.new("RGB", (lcd_disp.width, lcd_disp.height), "BLUE")
            lcd_disp.ShowImage(placeholder)
    except Exception as e:
        print(f"⚠️ Error showing sprite: {e}")

def show_vietnamese_text(text):
    """Show Vietnamese text on LCD when no sprites available"""
    global lcd_disp
    if lcd_disp is None:
        return
    
    try:
        img = Image.new("RGB", (lcd_disp.width, lcd_disp.height), "black")
        draw = ImageDraw.Draw(img)
        
        try:
            # Try to load a Vietnamese-compatible font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except Exception:
            font = ImageFont.load_default()
        
        # Word wrap for Vietnamese text
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            try:
                bbox = draw.textbbox((0, 0), test_line, font=font)
                tw = bbox[2] - bbox[0]
            except Exception:
                tw = len(test_line) * 8
            
            if tw <= lcd_disp.width - 20:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Draw lines
        y_start = (lcd_disp.height - len(lines) * 20) // 2
        for i, line in enumerate(lines[:10]):  # Max 10 lines
            draw.text((10, y_start + i * 20), line, fill=(0, 255, 0), font=font)
        
        lcd_disp.ShowImage(img)
    except Exception as e:
        print(f"⚠️ Error showing Vietnamese text: {e}")

def animate_speech():
    """Animate speech sprites in a loop until stopped"""
    sprite_index = 0
    while not stop_animation.is_set():
        if all(s.exists() for s in SPEECH_SPRITES):
            show_sprite(SPEECH_SPRITES[sprite_index])
            sprite_index = (sprite_index + 1) % len(SPEECH_SPRITES)
        else:
            # If sprites don't exist, show Vietnamese-friendly animation
            colors = ["RED", "GREEN", "YELLOW"]
            try:
                placeholder = Image.new("RGB", (lcd_disp.width, lcd_disp.height), colors[sprite_index])
                # Add speaking indicator in Vietnamese
                draw = ImageDraw.Draw(placeholder)
                draw.text((60, 110), "ĐANG NÓI...", fill="WHITE")
                lcd_disp.ShowImage(placeholder)
            except:
                pass
            sprite_index = (sprite_index + 1) % len(colors)

        # Animation frame rate (adjust as needed)
        time.sleep(0.2)

def start_speech_animation():
    """Start the speech animation in a separate thread"""
    global animation_thread, stop_animation
    stop_animation.clear()
    animation_thread = threading.Thread(target=animate_speech, daemon=True)
    animation_thread.start()

def stop_speech_animation():
    """Stop the speech animation and return to resting face"""
    global stop_animation, animation_thread
    stop_animation.set()
    if animation_thread:
        animation_thread.join(timeout=1)
    show_sprite(RESTING_SPRITE)

# ===== Pause/Resume helpers =====
def show_paused_screen():
    """Overlay a simple 'PAUSED' screen with Vietnamese text."""
    global lcd_disp
    if not lcd_disp:
        return
    img = Image.new("RGB", (lcd_disp.width, lcd_disp.height), "black")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except Exception:
        font = ImageFont.load_default()
    
    msg = "TẠM DỪNG" if current_language == "vi" else "PAUSED"
    try:
        bbox = draw.textbbox((0, 0), msg, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        tw, th = len(msg) * 10, 20
    
    draw.rectangle((0, 0, lcd_disp.width-1, lcd_disp.height-1), outline=(0, 255, 0), width=2)
    draw.text(((lcd_disp.width - tw)//2, (lcd_disp.height - th)//2), msg, fill=(0, 255, 0), font=font)
    lcd_disp.ShowImage(img)

def on_pause():
    paused.set()
    stop_speech_animation()
    show_paused_screen()
    if current_language == "vi":
        print("⏸️  Tạm dừng")
    else:
        print("⏸️  Paused")

def on_resume():
    paused.clear()
    show_sprite(RESTING_SPRITE)
    if current_language == "vi":
        print("▶️  Tiếp tục")
    else:
        print("▶️  Resumed")

def init_pause_resume_buttons():
    if not GPIO_AVAILABLE:
        return None, None
    try:
        pause_btn = Button(PAUSE_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        resume_btn = Button(RESUME_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        pause_btn.when_pressed = on_pause
        resume_btn.when_pressed = on_resume
        print(f"⏯️  Pause on GPIO {PAUSE_BUTTON_PIN}, Resume on GPIO {RESUME_BUTTON_PIN}")
        return pause_btn, resume_btn
    except Exception as e:
        print(f"⚠️  Could not init pause/resume buttons: {e}")
        return None, None

# ===== Init =====
def init_models():
    if current_language == "vi":
        print("🚀 Đang khởi động Chatbot Giọng nói với màn hình LCD...")
        print("📦 Đang tải các mô hình (có thể mất một chút thời gian lần đầu)...")
        print("  Đang tải Whisper cho tiếng Việt...")
    else:
        print("🚀 Starting Voice Chatbot with LCD Face...")
        print("📦 Loading models (this may take a moment the first time)...")
        print("  Loading Whisper for Vietnamese...")

    # Use small model for better Vietnamese support
    whisper = WhisperModel(
        WHISPER_MODEL,
        device="cpu",
        compute_type="int8",
        cpu_threads=6,  # Optimized for Pi 4
        download_root=str(Path.home() / ".cache" / "whisper")
    )

    if current_language == "vi":
        print("  Đang kiểm tra Ollama...")
    else:
        print("  Checking Ollama...")
    
    try:
        ollama.list()
    except Exception:
        if current_language == "vi":
            print("❌ Ollama chưa chạy! Khởi động với: sudo systemctl enable --now ollama")
        else:
            print("❌ Ollama not running! Start it with: sudo systemctl enable --now ollama")
        sys.exit(1)

    if current_language == "vi":
        print("✅ Tất cả mô hình đã tải thành công!\n")
    else:
        print("✅ All models loaded successfully!\n")
    return whisper

def init_button():
    if not GPIO_AVAILABLE:
        return None
    try:
        btn = Button(STOP_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        print("🔘 Stop button ready on GPIO 22")
        return btn
    except Exception:
        print("⚠️  GPIO pins not accessible")
        return None

# ===== Helpers =====
def check_stop(stop_button):
    return bool(stop_button and stop_button.is_pressed)

def _spawn_pw_cat_record(rate, channels, target):
    cmd = [
        "pw-cat", "--record", "-",
        "--format", "s16",
        "--rate", str(rate),
        "--channels", str(channels)
    ]
    if target:
        cmd += ["--target", str(target)]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def _select_record_pipeline(target):
    """
    Try a few (rate,channels) combos so we don't crash if the device
    refuses 16k mono. Returns (proc, rate, channels, first_chunk or None, err_text).
    """
    attempts = [
        (PREF_SAMPLE_RATE, PREF_CHANNELS),  # 16k / mono
        (PREF_SAMPLE_RATE, 2),              # 16k / stereo
        (48000, PREF_CHANNELS),             # 48k / mono
        (48000, 2),                         # 48k / stereo
    ]
    for rate, ch in attempts:
        proc = _spawn_pw_cat_record(rate, ch, target)
        bytes_per_sample = 2
        frame_bytes = int(rate * FRAME_MS / 1000) * bytes_per_sample * ch
        chunk = proc.stdout.read(frame_bytes)
        if chunk:
            return proc, rate, ch, chunk, ""
        err = (proc.stderr.read() or b"").decode("utf-8", errors="ignore")
        try:
            proc.terminate(); proc.wait(timeout=0.5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        if err.strip():
            print(f"   ⚠️  pw-cat refused {rate}Hz/{ch}ch: {err.strip()}")
        else:
            print(f"   ⚠️  pw-cat produced no data at {rate}Hz/{ch}ch, retrying...")
    return None, None, None, None, "No working pw-cat configuration found"

def record_with_vad(timeout_seconds=30, stop_button=None):
    """Record audio until silence is detected (VAD). Returns (bytes, rate, channels) or (None, None, None)."""
    if current_language == "vi":
        print("🎤 Đang lắng nghe... (hãy nói ngay)")
    else:
        print("🎤 Listening... (speak now)")
        
    if MIC_TARGET:
        print(f"   🎯 Using source target: {MIC_TARGET}")

    proc, rate, ch, first_chunk, err = _select_record_pipeline(MIC_TARGET)
    if not proc:
        print(f"❌ {err}")
        return None, None, None

    bytes_per_sample = 2
    frame_bytes = int(rate * FRAME_MS / 1000) * bytes_per_sample * ch
    audio_buffer = bytearray()

    try:
        # Quick calibration (~300ms)
        noise_samples = []
        if first_chunk:
            s = np.frombuffer(first_chunk, dtype=np.int16).astype(np.float32)
            noise_samples.append(float(np.sqrt(np.mean(s * s))))
        for _ in range(9):
            chunk = proc.stdout.read(frame_bytes)
            if chunk:
                s = np.frombuffer(chunk, dtype=np.int16).astype(np.float32)
                noise_samples.append(float(np.sqrt(np.mean(s * s))))
        noise_floor = float(np.median(noise_samples)) if noise_samples else 50.0
        threshold = max(SILENCE_THRESHOLD, noise_floor * 1.8)
        print(f"   📏 Noise floor: {noise_floor:.1f}  |  Threshold: {threshold:.1f}")

        is_speaking = False
        silence_ms = 0
        speech_ms = 0
        total_ms = 0
        start = time.time()

        if first_chunk is not None:
            samples = np.frombuffer(first_chunk, dtype=np.int16).astype(np.float32)
            rms = float(np.sqrt(np.mean(samples * samples)))
            level = int(rms / 100)
            print(f"\r  Level: {'▁'*min(level,20):<20} ", end="", flush=True)
            if rms > threshold:
                is_speaking = True
                speech_ms = FRAME_MS
                audio_buffer.extend(first_chunk)

        while True:
            if check_stop(stop_button):
                raise KeyboardInterrupt

            if (time.time() - start) > timeout_seconds:
                if not is_speaking:
                    return None, None, None
                break

            chunk = proc.stdout.read(frame_bytes)
            if not chunk:
                err = (proc.stderr.read() or b"").decode("utf-8", errors="ignore").strip()
                if err:
                    print(f"\n❗ pw-cat: {err}")
                break

            samples = np.frombuffer(chunk, dtype=np.int16).astype(np.float32)
            rms = float(np.sqrt(np.mean(samples * samples)))
            level = int(rms / 100)
            print(f"\r  Level: {'▁'*min(level,20):<20} ", end="", flush=True)

            if is_speaking:
                audio_buffer.extend(chunk)
                if rms < threshold:
                    silence_ms += FRAME_MS
                else:
                    silence_ms = 0
                    speech_ms += FRAME_MS

                if silence_ms >= END_SILENCE_MS and speech_ms >= MIN_SPEECH_MS:
                    dur_s = len(audio_buffer) / (rate * bytes_per_sample * ch)
                    print(f"\n  ✓ Recorded {dur_s:.1f}s")
                    break
                elif total_ms >= MAX_RECORDING_MS:
                    print("\n  ✓ Max recording length")
                    break
            else:
                if rms > threshold:
                    is_speaking = True
                    speech_ms = FRAME_MS
                    silence_ms = 0
                    audio_buffer.extend(chunk)
                    if current_language == "vi":
                        print("\n  💬 Phát hiện giọng nói!")
                    else:
                        print("\n  💬 Speech detected!")

            total_ms += FRAME_MS

    except KeyboardInterrupt:
        if current_language == "vi":
            print("\n  ⏹️  Đã dừng ghi âm")
        else:
            print("\n  ⏹️  Recording stopped")
        audio_buffer = None
    finally:
        try:
            proc.terminate(); proc.wait(timeout=0.8)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    if audio_buffer and len(audio_buffer) > 1000:
        return bytes(audio_buffer), rate, ch
    return None, None, None

def save_wav(audio_data, filepath, sample_rate, channels):
    with wave.open(str(filepath), 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data)

def transcribe_audio(whisper_model, audio_path):
    global current_language
    
    if current_language == "vi":
        print("🧠 Đang nhận diện giọng nói...")
    else:
        print("🧠 Transcribing...")
    
    try:
        # Auto-detect language if set to auto, otherwise use current language
        language = None if current_language == "auto" else current_language
        
        segments, info = whisper_model.transcribe(
            str(audio_path),
            language=language,
            beam_size=1,
            best_of=1,
            temperature=0.0,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=500,
                speech_pad_ms=200
            )
        )
        
        text = " ".join(seg.text.strip() for seg in segments)
        
        # Update current language based on detection if auto mode
        if current_language == "auto" and text:
            detected_lang = detect_language(text)
            print(f"   🌐 Detected language: {'Vietnamese' if detected_lang == 'vi' else 'English'}")
        
        return text.strip() if text else None
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return None

def generate_response(user_text):
    global current_language
    
    if current_language == "vi":
        print("💭 Đang suy nghĩ...")
    else:
        print("💭 Thinking...")
    
    try:
        # Prepare system message based on language
        if current_language == "vi" or detect_language(user_text) == "vi":
            system_msg = "Bạn là một trợ lý giọng nói hữu ích. Hãy trả lời ngắn gọn (tối đa 2 câu) và tự nhiên bằng tiếng Việt."
        else:
            system_msg = "You are a helpful voice assistant. Keep responses concise (max 2 sentences) and conversational in English."
        
        # Try primary model first
        try:
            resp = ollama.chat(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_text}
                ],
                options={"temperature": 0.7, "num_predict": 60, "top_p": 0.9}
            )
            return resp["message"]["content"].strip()
        except Exception:
            # Fallback to secondary model
            print(f"⚠️ Trying fallback model: {FALLBACK_LLM_MODEL}")
            resp = ollama.chat(
                model=FALLBACK_LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_text}
                ],
                options={"temperature": 0.7, "num_predict": 60, "top_p": 0.9}
            )
            return resp["message"]["content"].strip()
            
    except Exception as e:
        print(f"❌ LLM Error: {e}")
        if current_language == "vi":
            return "Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu đó."
        else:
            return "I'm sorry, I had trouble processing that."

def speak_text(text):
    """Vietnamese/English TTS using gTTS with LCD animation"""
    if current_language == "vi":
        print("🔊 Đang nói...")
    else:
        print("🔊 Speaking...")

    # Respect pause before starting
    if paused.is_set():
        if current_language == "vi":
            print("🔇 Bỏ qua TTS (đã tạm dừng)")
        else:
            print("🔇 Skipping TTS (paused)")
        return

    # Start the speech animation
    start_speech_animation()
    
    # Show text on LCD if no sprites available
    if not all(s.exists() for s in SPEECH_SPRITES):
        show_vietnamese_text(text)

    try:
        # Detect language for TTS
        tts_lang = detect_language(text)
        
        # Create TTS object
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            
            if paused.is_set():
                if current_language == "vi":
                    print("🔇 TTS bị gián đoạn (tạm dừng)")
                else:
                    print("🔇 TTS interrupted (paused)")
            else:
                # Play using pygame
                pygame.mixer.music.load(tmp_file.name)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy() and not paused.is_set():
                    time.sleep(0.1)
            
            # Clean up
            os.unlink(tmp_file.name)
            
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        # Fallback to espeak for Vietnamese
        try:
            if detect_language(text) == "vi":
                subprocess.run(["espeak-ng", "-v", "vi", "-s", "150", text], check=False)
            else:
                subprocess.run(["espeak-ng", "-v", "en", "-s", "150", text], check=False)
        except Exception as e2:
            print(f"❌ Fallback TTS Error: {e2}")
    finally:
        # Stop animation and return to resting face
        stop_speech_animation()

# ===== Main =====
def main():
    global MIC_TARGET, lcd_disp, current_language
    args = sys.argv[1:]
    
    # Parse command line arguments
    if "--mic-target" in args:
        try:
            MIC_TARGET = args[args.index("--mic-target") + 1]
        except Exception:
            print("⚠️  Usage: --mic-target <source-id-or-name>")
    
    if "--lang" in args:
        try:
            lang = args[args.index("--lang") + 1]
            if lang in SUPPORTED_LANGUAGES:
                current_language = lang
            else:
                print(f"⚠️  Unsupported language: {lang}. Using default: {current_language}")
        except Exception:
            print("⚠️  Usage: --lang <vi|en|auto>")

    def shutdown_handler(sig, frame):
        if current_language == "vi":
            print("\n\n👋 Đang tắt...")
        else:
            print("\n\n👋 Shutting down...")
        if lcd_disp:
            try:
                lcd_disp.clear()
                lcd_disp.module_exit()
            except:
                pass
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    if len(args) > 0:
        if args[0] == "--help":
            print("Voice Chatbot with LCD Face Animation - Vietnamese Support")
            print("\nUsage: python3 bobchat_vietnamese.py [options]")
            print("  --mic-target <id>   Force a specific PipeWire source")
            print("  --lang <vi|en|auto> Set language (vi=Vietnamese, en=English, auto=detect)")
            print("  --test              Record and play back test audio")
            sys.exit(0)

    # Initialize LCD
    init_lcd()

    # Show resting face initially
    show_sprite(RESTING_SPRITE)

    whisper_model = init_models()
    stop_button = init_button()
    pause_btn, resume_btn = init_pause_resume_buttons()  # keep refs in scope

    print("\n" + "="*60)
    if current_language == "vi":
        print("🤖 CHATBOT GIỌNG NÓI TIẾNG VIỆT VỚI MÀN HÌNH LCD SẴN SÀNG!")
    else:
        print("🤖 VIETNAMESE VOICE CHATBOT WITH LCD FACE READY!")
    print("="*60)
    print("Setup:")
    print("  • Microphone: USB (PipeWire default source)")
    print("  • Speaker: Bluetooth or 3.5mm (PipeWire default sink)")
    print("  • Display: LCD 1.28inch with Vietnamese face animation")
    print(f"  • Language: {'Vietnamese' if current_language == 'vi' else 'English' if current_language == 'en' else 'Auto-detect'}")
    print(f"  • Model: {LLM_MODEL}")
    print(f"  • Stop: {'GPIO 22 button or Ctrl+C' if stop_button else 'Press Ctrl+C'}")
    print(f"  • Pause: GPIO {PAUSE_BUTTON_PIN}  • Resume: GPIO {RESUME_BUTTON_PIN}")
    if MIC_TARGET:
        print(f"  • Mic target override: {MIC_TARGET}")
    print("\nSprites:")
    print(f"  • Resting: {RESTING_SPRITE}")
    print(f"  • Speech: {', '.join(str(s) for s in SPEECH_SPRITES)}")
    
    if current_language == "vi":
        print("\nBắt đầu lắng nghe...\n")
    else:
        print("\nListening for speech...\n")

    while True:
        try:
            # Honor paused state
            if paused.is_set():
                show_paused_screen()
                if check_stop(stop_button):
                    if current_language == "vi":
                        print("\n⏹️  Đã nhấn nút dừng")
                    else:
                        print("\n⏹️  Stop button pressed")
                    break
                time.sleep(0.2)
                continue

            if check_stop(stop_button):
                if current_language == "vi":
                    print("\n⏹️  Đã nhấn nút dừng")
                else:
                    print("\n⏹️  Stop button pressed")
                break

            audio_data, rate, ch = record_with_vad(timeout_seconds=30, stop_button=stop_button)

            if audio_data:
                save_wav(audio_data, TEMP_WAV, sample_rate=rate, channels=ch)
                user_text = transcribe_audio(whisper_model, TEMP_WAV)

                if user_text:
                    if current_language == "vi":
                        print(f"📝 Bạn nói: \"{user_text}\"")
                    else:
                        print(f"📝 You said: \"{user_text}\"")
                    
                    # Check for goodbye in both languages
                    goodbye_words_vi = ["tạm biệt", "chào nhé", "dừng lại", "tắt đi", "kết thúc"]
                    goodbye_words_en = ["goodbye", "bye", "stop", "exit", "quit", "shut down", "turn off"]
                    
                    user_lower = user_text.lower()
                    if (any(w in user_lower for w in goodbye_words_vi) or 
                        any(w in user_lower for w in goodbye_words_en)):
                        if current_language == "vi" or detect_language(user_text) == "vi":
                            speak_text("Tạm biệt!")
                        else:
                            speak_text("Goodbye!")
                        break

                    reply = generate_response(user_text)
                    if current_language == "vi":
                        print(f"🤖 Tiến Minh: \"{reply}\"\n")
                    else:
                        print(f"🤖 Assistant: \"{reply}\"\n")
                    speak_text(reply)

                    if current_language == "vi":
                        print(f"⏳ Sẵn sàng lại sau {AUTO_RESTART_DELAY}s...")
                    else:
                        print(f"⏳ Ready again in {AUTO_RESTART_DELAY}s...")
                    time.sleep(AUTO_RESTART_DELAY)
                    
                    if current_language == "vi":
                        print("🎤 Đang lắng nghe...\n")
                    else:
                        print("🎤 Listening...\n")
                else:
                    if current_language == "vi":
                        print("❓ Không phát hiện giọng nói trong âm thanh ghi được\n")
                    else:
                        print("❓ No speech detected in the captured audio\n")
            else:
                if current_language == "vi":
                    print("💤 Không phát hiện giọng nói, vẫn đang lắng nghe...\n")
                else:
                    print("💤 No speech detected, still listening...\n")
                time.sleep(0.5)

        except KeyboardInterrupt:
            if current_language == "vi":
                print("\n\n⌨️  Bị gián đoạn bởi người dùng")
            else:
                print("\n\n⌨️  Interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            if current_language == "vi":
                print("Khởi động lại sau 3 giây...\n")
            else:
                print("Restarting in 3 seconds...\n")
            time.sleep(3)

    # Clean shutdown
    if current_language == "vi":
        print("\n👋 Tạm biệt!")
    else:
        print("\n👋 Goodbye!")
    if lcd_disp:
        try:
            lcd_disp.clear()
            lcd_disp.module_exit()
        except:
            pass
    print("="*60)

if __name__ == "__main__":
    main()