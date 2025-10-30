#!/usr/bin/env python3
"""
Voice Chatbot with HDMI Display - Vietnamese Support
Shows chatbot interface on HDMI monitor instead of SPI LCD
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
import re

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
try:
    from vietnamese_tts import VietnameseTTS
except ImportError:
    print("⚠️ vietnamese_tts module not found, using basic TTS")
    VietnameseTTS = None

# Optional GPIO stop button (no SPI display needed)
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

# ===== Configuration =====
STOP_BUTTON_PIN = 22

# Display settings for HDMI
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (20, 20, 40)  # Dark blue
TEXT_COLOR = (0, 255, 100)       # Green
ACCENT_COLOR = (255, 200, 0)     # Orange
ERROR_COLOR = (255, 100, 100)    # Red

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

# Global variables for display and language
screen = None
font_large = None
font_medium = None
font_small = None
current_language = DEFAULT_LANGUAGE
vietnamese_tts = None
display_thread = None
display_messages = []
display_lock = threading.Lock()
is_speaking = False

# ===== Pause/Resume Buttons =====
PAUSE_BUTTON_PIN = 23
RESUME_BUTTON_PIN = 24

# Global pause flag
paused = threading.Event()

# ===== Language Detection =====
def detect_language(text):
    """Simple language detection based on Vietnamese characters"""
    vietnamese_chars = re.findall(r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', text.lower())
    if len(vietnamese_chars) > 0:
        return "vi"
    return "en"

# ===== HDMI Display Functions =====
def init_pygame_display():
    """Initialize pygame display for HDMI output"""
    global screen, font_large, font_medium, font_small
    
    try:
        # Initialize pygame
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
        
        # Set up display
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Bob - Vietnamese Voice Chatbot")
        
        # Load fonts (Vietnamese compatible)
        try:
            font_large = pygame.font.Font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            font_medium = pygame.font.Font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            font_small = pygame.font.Font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except Exception:
            # Fallback to default fonts
            font_large = pygame.font.Font(None, 48)
            font_medium = pygame.font.Font(None, 24)
            font_small = pygame.font.Font(None, 16)
        
        print("📺 HDMI display initialized")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize display: {e}")
        return False

def add_display_message(message, message_type="info"):
    """Add message to display queue"""
    global display_messages
    with display_lock:
        timestamp = time.strftime("%H:%M:%S")
        display_messages.append({
            'text': message,
            'type': message_type,
            'timestamp': timestamp
        })
        # Keep only last 10 messages
        display_messages = display_messages[-10:]

def draw_status_bar():
    """Draw top status bar"""
    if not screen:
        return
    
    # Status bar background
    pygame.draw.rect(screen, (40, 40, 60), (0, 0, SCREEN_WIDTH, 60))
    
    # Title
    title_text = "TienMinh - Trợ lý Giọng nói Tiếng Việt" if current_language == "vi" else "TienMinh - Vietnamese Voice Assistant"
    title_surface = font_medium.render(title_text, True, ACCENT_COLOR)
    screen.blit(title_surface, (20, 15))
    
    # Status indicators
    status_x = SCREEN_WIDTH - 200
    
    # Language indicator
    lang_text = f"Ngôn ngữ: {current_language.upper()}" if current_language == "vi" else f"Language: {current_language.upper()}"
    lang_surface = font_small.render(lang_text, True, TEXT_COLOR)
    screen.blit(lang_surface, (status_x, 10))
    
    # Speaking indicator
    if is_speaking:
        speaking_text = "🔊 Đang nói..." if current_language == "vi" else "🔊 Speaking..."
        speaking_surface = font_small.render(speaking_text, True, ACCENT_COLOR)
        screen.blit(speaking_surface, (status_x, 30))
    elif paused.is_set():
        paused_text = "⏸️ Tạm dừng" if current_language == "vi" else "⏸️ Paused"
        paused_surface = font_small.render(paused_text, True, ERROR_COLOR)
        screen.blit(paused_surface, (status_x, 30))
    else:
        listening_text = "🎤 Lắng nghe..." if current_language == "vi" else "🎤 Listening..."
        listening_surface = font_small.render(listening_text, True, TEXT_COLOR)
        screen.blit(listening_surface, (status_x, 30))

def draw_main_face():
    """Draw TienMinh's face in the center"""
    if not screen:
        return
    
    center_x = SCREEN_WIDTH // 2
    center_y = 200
    
    # Face circle
    face_color = ACCENT_COLOR if is_speaking else TEXT_COLOR
    pygame.draw.circle(screen, face_color, (center_x, center_y), 80, 3)
    
    # Eyes
    eye_color = face_color
    pygame.draw.circle(screen, eye_color, (center_x - 25, center_y - 15), 8)
    pygame.draw.circle(screen, eye_color, (center_x + 25, center_y - 15), 8)
    
    # Mouth (changes based on speaking state)
    if is_speaking:
        # Open mouth (oval)
        mouth_rect = pygame.Rect(center_x - 15, center_y + 10, 30, 20)
        pygame.draw.ellipse(screen, face_color, mouth_rect, 3)
    else:
        # Closed mouth (line)
        pygame.draw.line(screen, face_color, (center_x - 15, center_y + 20), (center_x + 15, center_y + 20), 3)

def draw_messages():
    """Draw conversation messages"""
    if not screen or not display_messages:
        return
    
    start_y = 320
    line_height = 35
    
    with display_lock:
        for i, msg in enumerate(display_messages[-8:]):  # Show last 8 messages
            y = start_y + (i * line_height)
            
            # Message background
            if msg['type'] == 'user':
                bg_color = (0, 50, 100)
                text_color = (200, 200, 255)
            elif msg['type'] == 'assistant':
                bg_color = (0, 100, 50)
                text_color = (200, 255, 200)
            elif msg['type'] == 'error':
                bg_color = (100, 0, 0)
                text_color = (255, 200, 200)
            else:
                bg_color = (50, 50, 50)
                text_color = TEXT_COLOR
            
            # Draw message background
            pygame.draw.rect(screen, bg_color, (20, y - 5, SCREEN_WIDTH - 40, line_height - 5))
            
            # Draw timestamp
            time_surface = font_small.render(msg['timestamp'], True, (150, 150, 150))
            screen.blit(time_surface, (30, y))
            
            # Draw message text (truncate if too long)
            text = msg['text']
            if len(text) > 70:
                text = text[:67] + "..."
            
            text_surface = font_small.render(text, True, text_color)
            screen.blit(text_surface, (100, y))

def draw_instructions():
    """Draw usage instructions at bottom"""
    if not screen:
        return
    
    instructions = [
        "Hướng dẫn sử dụng:" if current_language == "vi" else "Usage Instructions:",
        "• Nói 'Xin chào' để bắt đầu" if current_language == "vi" else "• Say 'Hello' to start",
        "• GPIO 22: Dừng | GPIO 23: Tạm dừng | GPIO 24: Tiếp tục" if current_language == "vi" else "• GPIO 22: Stop | GPIO 23: Pause | GPIO 24: Resume",
        "• Nói 'Tạm biệt' để kết thúc" if current_language == "vi" else "• Say 'Goodbye' to exit"
    ]
    
    start_y = SCREEN_HEIGHT - 80
    for i, instruction in enumerate(instructions):
        color = ACCENT_COLOR if i == 0 else (150, 150, 150)
        font = font_small if i == 0 else font_small
        text_surface = font.render(instruction, True, color)
        screen.blit(text_surface, (20, start_y + (i * 15)))

def update_display():
    """Main display update function"""
    if not screen:
        return
    
    # Clear screen
    screen.fill(BACKGROUND_COLOR)
    
    # Draw all components
    draw_status_bar()
    draw_main_face()
    draw_messages()
    draw_instructions()
    
    # Update display
    pygame.display.flip()

def display_loop():
    """Display update loop running in separate thread"""
    clock = pygame.time.Clock()
    
    while True:
        try:
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
            
            update_display()
            clock.tick(30)  # 30 FPS
            
        except Exception as e:
            print(f"Display error: {e}")
            time.sleep(0.1)

def start_display():
    """Start display thread"""
    global display_thread
    if init_pygame_display():
        display_thread = threading.Thread(target=display_loop, daemon=True)
        display_thread.start()
        add_display_message("Display initialized", "info")
        return True
    return False

# ===== Pause/Resume helpers =====
def on_pause():
    global paused
    paused.set()
    add_display_message("Tạm dừng" if current_language == "vi" else "Paused", "info")
    print("⏸️  Paused" if current_language == "en" else "⏸️  Tạm dừng")

def on_resume():
    global paused
    paused.clear()
    add_display_message("Tiếp tục" if current_language == "vi" else "Resumed", "info")
    print("▶️  Resumed" if current_language == "en" else "▶️  Tiếp tục")

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
    global vietnamese_tts
    if current_language == "vi":
        add_display_message("🚀 Đang khởi động Chatbot Giọng nói...", "info")
        add_display_message("📦 Đang tải các mô hình...", "info")
        print("🚀 Đang khởi động Chatbot Giọng nói với màn hình HDMI...")
        print("📦 Đang tải các mô hình (có thể mất một chút thời gian lần đầu)...")
        print("  Đang tải Whisper cho tiếng Việt...")
    else:
        add_display_message("🚀 Starting Voice Chatbot...", "info")
        add_display_message("📦 Loading models...", "info")
        print("🚀 Starting Voice Chatbot with HDMI Display...")
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
        print("  Đang khởi tạo Vietnamese TTS...")
        add_display_message("Đang khởi tạo TTS tiếng Việt...", "info")
    else:
        print("  Initializing Vietnamese TTS...")
        add_display_message("Initializing Vietnamese TTS...", "info")
    
    if VietnameseTTS:
        vietnamese_tts = VietnameseTTS(preferred_engine="edge")  # Try Edge TTS first for better quality

    if current_language == "vi":
        print("  Đang kiểm tra Ollama...")
        add_display_message("Đang kiểm tra Ollama...", "info")
    else:
        print("  Checking Ollama...")
        add_display_message("Checking Ollama...", "info")
    
    try:
        ollama.list()
    except Exception:
        error_msg = "❌ Ollama chưa chạy! Khởi động với: sudo systemctl enable --now ollama" if current_language == "vi" else "❌ Ollama not running! Start it with: sudo systemctl enable --now ollama"
        print(error_msg)
        add_display_message(error_msg, "error")
        sys.exit(1)

    if current_language == "vi":
        success_msg = "✅ Tất cả mô hình đã tải thành công!"
        print(success_msg)
        add_display_message(success_msg, "info")
        if vietnamese_tts:
            add_display_message(f"TTS engines: {vietnamese_tts.get_available_engines()}", "info")
    else:
        success_msg = "✅ All models loaded successfully!"
        print(success_msg)
        add_display_message(success_msg, "info")
        if vietnamese_tts:
            add_display_message(f"TTS engines: {vietnamese_tts.get_available_engines()}", "info")
    
    return whisper

def init_button():
    if not GPIO_AVAILABLE:
        return None
    try:
        btn = Button(STOP_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        print("🔘 Stop button ready on GPIO 22")
        add_display_message("Stop button ready on GPIO 22", "info")
        return btn
    except Exception:
        print("⚠️  GPIO pins not accessible")
        add_display_message("GPIO pins not accessible", "error")
        return None

# ===== Audio Processing (same as before) =====
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
        msg = "🎤 Đang lắng nghe... (hãy nói ngay)"
        add_display_message("Đang lắng nghe...", "info")
    else:
        msg = "🎤 Listening... (speak now)"
        add_display_message("Listening...", "info")
    
    print(msg)
        
    if MIC_TARGET:
        print(f"   🎯 Using source target: {MIC_TARGET}")

    proc, rate, ch, first_chunk, err = _select_record_pipeline(MIC_TARGET)
    if not proc:
        print(f"❌ {err}")
        add_display_message(f"Microphone error: {err}", "error")
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

        is_speaking_audio = False
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
                is_speaking_audio = True
                speech_ms = FRAME_MS
                audio_buffer.extend(first_chunk)

        while True:
            if check_stop(stop_button):
                raise KeyboardInterrupt

            if (time.time() - start) > timeout_seconds:
                if not is_speaking_audio:
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

            if is_speaking_audio:
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
                    is_speaking_audio = True
                    speech_ms = FRAME_MS
                    silence_ms = 0
                    audio_buffer.extend(chunk)
                    if current_language == "vi":
                        print("\n  💬 Phát hiện giọng nói!")
                        add_display_message("Phát hiện giọng nói!", "info")
                    else:
                        print("\n  💬 Speech detected!")
                        add_display_message("Speech detected!", "info")

            total_ms += FRAME_MS

    except KeyboardInterrupt:
        if current_language == "vi":
            print("\n  ⏹️  Đã dừng ghi âm")
            add_display_message("Đã dừng ghi âm", "info")
        else:
            print("\n  ⏹️  Recording stopped")
            add_display_message("Recording stopped", "info")
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
        add_display_message("Đang nhận diện giọng nói...", "info")
    else:
        print("🧠 Transcribing...")
        add_display_message("Transcribing...", "info")
    
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
        error_msg = f"❌ Transcription error: {e}"
        print(error_msg)
        add_display_message(error_msg, "error")
        return None

def generate_response(user_text):
    global current_language
    
    if current_language == "vi":
        print("💭 Đang suy nghĩ...")
        add_display_message("Đang suy nghĩ...", "info")
    else:
        print("💭 Thinking...")
        add_display_message("Thinking...", "info")
    
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
        error_msg = f"❌ LLM Error: {e}"
        print(error_msg)
        add_display_message(error_msg, "error")
        if current_language == "vi":
            return "Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu đó."
        else:
            return "I'm sorry, I had trouble processing that."

def speak_text(text):
    """Vietnamese/English TTS with display updates"""
    global is_speaking, vietnamese_tts
    
    if current_language == "vi":
        print("🔊 Đang nói...")
        add_display_message("Đang nói...", "info")
    else:
        print("🔊 Speaking...")
        add_display_message("Speaking...", "info")

    # Respect pause before starting
    if paused.is_set():
        if current_language == "vi":
            print("🔇 Bỏ qua TTS (đã tạm dừng)")
            add_display_message("Bỏ qua TTS (đã tạm dừng)", "info")
        else:
            print("🔇 Skipping TTS (paused)")
            add_display_message("Skipping TTS (paused)", "info")
        return

    # Update speaking status for display
    is_speaking = True

    try:
        # Detect language for TTS
        tts_lang = detect_language(text)
        
        # Use advanced TTS module if available
        if vietnamese_tts:
            if tts_lang == "vi":
                # Try different Vietnamese voices
                success = vietnamese_tts.speak(text, engine="edge", voice="vi-VN-HoaiMyNeural")
                if not success:
                    success = vietnamese_tts.speak(text, engine="gtts", lang="vi")
                if not success:
                    success = vietnamese_tts.speak(text, engine="espeak", voice="vi", speed=150)
            else:
                # English fallback
                success = vietnamese_tts.speak(text, engine="gtts", lang="en")
                if not success:
                    success = vietnamese_tts.speak(text, engine="espeak", voice="en", speed=160)
            
            if success:
                return
        
        # Manual fallback if TTS module fails
        print("⚠️ Using fallback TTS...")
        add_display_message("Using fallback TTS...", "info")
        if tts_lang == "vi":
            subprocess.run(["espeak-ng", "-v", "vi", "-s", "150", "-p", "60", text], check=False)
        else:
            subprocess.run(["espeak-ng", "-v", "en", "-s", "160", "-p", "50", text], check=False)
            
    except Exception as e:
        error_msg = f"❌ TTS Error: {e}"
        print(error_msg)
        add_display_message(error_msg, "error")
        # Last resort: basic espeak
        try:
            subprocess.run(["espeak-ng", "-s", "150", text], check=False)
        except Exception as e2:
            print(f"❌ All TTS methods failed: {e2}")
    finally:
        # Update speaking status
        is_speaking = False

# ===== Main =====
def main():
    global MIC_TARGET, current_language
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
        pygame.quit()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    if len(args) > 0 and args[0] == "--help":
        print("Voice Chatbot with HDMI Display - Vietnamese Support")
        print("\nUsage: python3 hdmi_chatbot_vietnamese.py [options]")
        print("  --mic-target <id>   Force a specific PipeWire source")
        print("  --lang <vi|en|auto> Set language (vi=Vietnamese, en=English, auto=detect)")
        print("  --test              Record and play back test audio")
        sys.exit(0)

    # Start display
    if not start_display():
        print("❌ Could not initialize display, continuing without visual interface")

    whisper_model = init_models()
    stop_button = init_button()
    pause_btn, resume_btn = init_pause_resume_buttons()  # keep refs in scope

    print("\n" + "="*60)
    if current_language == "vi":
        print("🤖 CHATBOT GIỌNG NÓI TIẾNG VIỆT VỚI MÀN HÌNH HDMI SẴN SÀNG!")
        add_display_message("Chatbot sẵn sàng!", "info")
    else:
        print("🤖 VIETNAMESE VOICE CHATBOT WITH HDMI DISPLAY READY!")
        add_display_message("Chatbot ready!", "info")
    print("="*60)
    print("Setup:")
    print("  • Microphone: USB (PipeWire default source)")
    print("  • Speaker: Bluetooth or 3.5mm (PipeWire default sink)")
    print("  • Display: HDMI monitor with GUI interface")
    print(f"  • Language: {'Vietnamese' if current_language == 'vi' else 'English' if current_language == 'en' else 'Auto-detect'}")
    print(f"  • Model: {LLM_MODEL}")
    print(f"  • Stop: {'GPIO 22 button or Ctrl+C' if stop_button else 'Press Ctrl+C'}")
    print(f"  • Pause: GPIO {PAUSE_BUTTON_PIN}  • Resume: GPIO {RESUME_BUTTON_PIN}")
    if MIC_TARGET:
        print(f"  • Mic target override: {MIC_TARGET}")
    
    if current_language == "vi":
        print("\nBắt đầu lắng nghe...\n")
        add_display_message("Bắt đầu lắng nghe...", "info")
    else:
        print("\nListening for speech...\n")
        add_display_message("Listening for speech...", "info")

    while True:
        try:
            # Honor paused state
            if paused.is_set():
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
                    
                    add_display_message(f"Bạn: {user_text}" if current_language == "vi" else f"You: {user_text}", "user")
                    
                    # Check for goodbye in both languages
                    goodbye_words_vi = ["tạm biệt", "chào nhé", "dừng lại", "tắt đi", "kết thúc"]
                    goodbye_words_en = ["goodbye", "bye", "stop", "exit", "quit", "shut down", "turn off"]
                    
                    user_lower = user_text.lower()
                    if (any(w in user_lower for w in goodbye_words_vi) or 
                        any(w in user_lower for w in goodbye_words_en)):
                        if current_language == "vi" or detect_language(user_text) == "vi":
                            reply = "Tạm biệt!"
                        else:
                            reply = "Goodbye!"
                        
                        add_display_message(f"TienMinh: {reply}", "assistant")
                        speak_text(reply)
                        break

                    reply = generate_response(user_text)
                    if current_language == "vi":
                        print(f"🤖 Trợ lý: \"{reply}\"\n")
                    else:
                        print(f"🤖 Assistant: \"{reply}\"\n")
                    
                    add_display_message(f"TienMinh: {reply}", "assistant")
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
                        msg = "❓ Không phát hiện giọng nói trong âm thanh ghi được"
                        print(msg + "\n")
                        add_display_message(msg, "error")
                    else:
                        msg = "❓ No speech detected in the captured audio"
                        print(msg + "\n")
                        add_display_message(msg, "error")
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
            error_msg = f"\n❌ Error: {e}"
            print(error_msg)
            add_display_message(f"Error: {e}", "error")
            if current_language == "vi":
                print("Khởi động lại sau 3 giây...\n")
            else:
                print("Restarting in 3 seconds...\n")
            time.sleep(3)

    # Clean shutdown
    if current_language == "vi":
        print("\n👋 Tạm biệt!")
        add_display_message("Tạm biệt!", "info")
    else:
        print("\n👋 Goodbye!")
        add_display_message("Goodbye!", "info")
    
    time.sleep(2)  # Let user see goodbye message
    pygame.quit()
    print("="*60)

if __name__ == "__main__":
    main()
