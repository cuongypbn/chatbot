#!/usr/bin/env python3
"""
Voice Chatbot (USB Mic + Bluetooth/Analog Speaker) — Vietnamese Support for Raspberry Pi 4

Features:
- Vietnamese speech recognition using Whisper
- Vietnamese TTS using gTTS
- Optimized for Pi 4 8GB RAM
- Multi-language support (Vietnamese/English)
- Auto language detection

Run:
  python3 chatbot_vietnamese.py
  python3 chatbot_vietnamese.py --mic-target <source-id-or-name>
  MIC_TARGET=<source-id-or-name> python3 chatbot_vietnamese.py
  python3 chatbot_vietnamese.py --test
  python3 chatbot_vietnamese.py --lang vi  # Force Vietnamese
  python3 chatbot_vietnamese.py --lang en  # Force English
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
import re
from vietnamese_tts import VietnameseTTS

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
WHISPER_MODEL = "small"  # Better Vietnamese support than tiny
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

# Global language setting
current_language = DEFAULT_LANGUAGE

# Initialize Vietnamese TTS
vietnamese_tts = None

# ===== Init =====
def init_models():
    global vietnamese_tts
    print("🚀 Starting Vietnamese Voice Chatbot...")
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

    print("  Initializing Vietnamese TTS...")
    vietnamese_tts = VietnameseTTS(preferred_engine="edge")  # Try Edge TTS first for better quality

    print("  Checking Ollama...")
    try:
        ollama.list()
    except Exception:
        print("❌ Ollama not running! Start it with: sudo systemctl enable --now ollama")
        sys.exit(1)

    print("✅ All models loaded successfully!\n")
    print(f"  Available TTS engines: {vietnamese_tts.get_available_engines()}")
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

# ===== Language Detection =====
def detect_language(text):
    """Simple language detection based on Vietnamese characters"""
    vietnamese_chars = re.findall(r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', text.lower())
    if len(vietnamese_chars) > 0:
        return "vi"
    return "en"

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

def speak_text_vietnamese(text):
    """Advanced Vietnamese TTS using multiple engines"""
    global vietnamese_tts
    
    if current_language == "vi":
        print("🔊 Đang nói...")
    else:
        print("🔊 Speaking...")
    
    try:
        # Detect language for TTS
        tts_lang = detect_language(text)
        
        # Use advanced TTS module
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
        if tts_lang == "vi":
            subprocess.run(["espeak-ng", "-v", "vi", "-s", "150", "-p", "60", text], check=False)
        else:
            subprocess.run(["espeak-ng", "-v", "en", "-s", "160", "-p", "50", text], check=False)
            
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        # Last resort: basic espeak
        try:
            subprocess.run(["espeak-ng", "-s", "150", text], check=False)
        except Exception as e2:
            print(f"❌ All TTS methods failed: {e2}")

def record_fixed_seconds(seconds=3, stop_button=None):
    if current_language == "vi":
        print(f"🎙️  Đang ghi âm ~{seconds}s để test...")
    else:
        print(f"🎙️  Recording ~{seconds}s for test...")
    
    if MIC_TARGET:
        print(f"   🎯 Using source target: {MIC_TARGET}")

    proc, rate, ch, first_chunk, err = _select_record_pipeline(MIC_TARGET)
    if not proc:
        print(f"❌ {err}")
        return None, None, None

    bytes_per_sample = 2
    frame_bytes = int(rate * FRAME_MS / 1000) * bytes_per_sample * ch
    total_frames = int((seconds * 1000) / FRAME_MS)
    buf = bytearray()
    if first_chunk:
        buf.extend(first_chunk)

    try:
        for _ in range(total_frames - (1 if first_chunk else 0)):
            if check_stop(stop_button):
                break
            chunk = proc.stdout.read(frame_bytes)
            if not chunk:
                err = (proc.stderr.read() or b"").decode("utf-8", errors="ignore").strip()
                if err:
                    print(f"❗ pw-cat: {err}")
                break
            buf.extend(chunk)
    finally:
        try:
            proc.terminate(); proc.wait(timeout=0.8)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    return (bytes(buf), rate, ch) if buf else (None, None, None)

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
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    if len(args) > 0:
        if args[0] == "--help":
            print("Voice Chatbot - Vietnamese Support for Raspberry Pi 4")
            print("\nUsage: python3 chatbot_vietnamese.py [options]")
            print("  --mic-target <id>   Force a specific PipeWire source")
            print("  --lang <vi|en|auto> Set language (vi=Vietnamese, en=English, auto=detect)")
            print("  --test              Record and play back test audio")
            sys.exit(0)
        elif args[0] == "--test" or "--test" in args:
            stop_button = init_button()
            data, rate, ch = record_fixed_seconds(seconds=3, stop_button=stop_button)
            if not data:
                print("❌ No audio captured during test.")
                sys.exit(1)
            out = Path("/tmp/test.wav")
            save_wav(data, out, sample_rate=rate, channels=ch)
            print("▶️  Playing back test recording...")
            subprocess.run(["aplay", str(out)], check=False)
            if current_language == "vi":
                print("✅ Test âm thanh hoàn thành!")
            else:
                print("✅ Audio test complete!")
            sys.exit(0)

    whisper_model = init_models()
    stop_button = init_button()

    print("\n" + "="*60)
    if current_language == "vi":
        print("🤖 CHATBOT GIỌNG NÓI TIẾNG VIỆT SẴN SÀNG!")
    else:
        print("🤖 VIETNAMESE VOICE CHATBOT READY!")
    print("="*60)
    print("Setup:")
    print("  • Microphone: USB (PipeWire default source)")
    print("  • Speaker: Bluetooth or 3.5mm (PipeWire default sink)")
    print(f"  • Language: {'Vietnamese' if current_language == 'vi' else 'English' if current_language == 'en' else 'Auto-detect'}")
    print(f"  • Model: {LLM_MODEL}")
    print(f"  • Stop: {'GPIO 22 button or Ctrl+C' if stop_button else 'Press Ctrl+C'}")
    if MIC_TARGET:
        print(f"  • Mic target override: {MIC_TARGET}")
    
    if current_language == "vi":
        print("\nBắt đầu lắng nghe...\n")
    else:
        print("\nListening for speech...\n")

    while True:
        try:
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
                            speak_text_vietnamese("Tạm biệt!")
                        else:
                            speak_text_vietnamese("Goodbye!")
                        break

                    reply = generate_response(user_text)
                    if current_language == "vi":
                        print(f"🤖 Trợ lý: \"{reply}\"\n")
                    else:
                        print(f"🤖 Assistant: \"{reply}\"\n")
                    speak_text_vietnamese(reply)

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

    if current_language == "vi":
        print("\n👋 Tạm biệt!")
    else:
        print("\n👋 Goodbye!")
    print("="*60)

if __name__ == "__main__":
    main()