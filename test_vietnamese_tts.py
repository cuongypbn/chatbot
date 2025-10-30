#!/usr/bin/env python3
"""
Test script for Vietnamese TTS engines on Raspberry Pi 4
Tests all available TTS engines with Vietnamese text samples
"""

import sys
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from vietnamese_tts import VietnameseTTS, demo_vietnamese_tts, get_available_voices
except ImportError as e:
    print(f"❌ Cannot import vietnamese_tts module: {e}")
    print("Please make sure vietnamese_tts.py is in the same directory")
    sys.exit(1)

def test_vietnamese_tts_comprehensive():
    """Comprehensive test of Vietnamese TTS functionality"""
    
    print("🎤 Vietnamese TTS Comprehensive Test for Raspberry Pi 4")
    print("=" * 60)
    
    # Test sentences in Vietnamese
    test_sentences = [
        "Xin chào, tôi là trợ lý giọng nói tiếng Việt của bạn.",
        "Hôm nay thời tiết thế nào?",
        "Tôi có thể giúp gì cho bạn?",
        "Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi.",
        "Tạm biệt và hẹn gặp lại!"
    ]
    
    # Initialize TTS
    print("🚀 Initializing Vietnamese TTS...")
    tts = VietnameseTTS()
    
    available_engines = tts.get_available_engines()
    if not available_engines:
        print("❌ No TTS engines available!")
        return False
    
    print(f"✅ Available engines: {available_engines}")
    print(f"📢 Available voices: {get_available_voices()}")
    print()
    
    # Test each engine
    for engine in available_engines:
        print(f"🔊 Testing {engine.upper()} engine...")
        print("-" * 40)
        
        for i, sentence in enumerate(test_sentences, 1):
            print(f"  Test {i}: {sentence[:50]}...")
            
            success = False
            try:
                if engine == "edge":
                    # Test both Vietnamese voices
                    success = tts.speak(sentence, engine="edge", voice="vi-VN-HoaiMyNeural")
                    if not success:
                        success = tts.speak(sentence, engine="edge", voice="vi-VN-NamMinhNeural")
                elif engine == "gtts":
                    success = tts.speak(sentence, engine="gtts", lang="vi")
                elif engine == "espeak":
                    success = tts.speak(sentence, engine="espeak", voice="vi", speed=150, pitch=60)
                elif engine == "festival":
                    success = tts.speak(sentence, engine="festival")
                else:
                    success = tts.speak(sentence, engine=engine)
                
                if success:
                    print(f"    ✅ Success")
                else:
                    print(f"    ❌ Failed")
                    
            except Exception as e:
                print(f"    ❌ Error: {e}")
            
            # Pause between tests
            time.sleep(1)
        
        print()
        
        # Ask user for feedback
        try:
            feedback = input(f"How was the {engine} quality? (good/ok/bad/skip): ").lower()
            if feedback in ['good', 'ok']:
                print(f"  👍 {engine} marked as working")
            elif feedback == 'bad':
                print(f"  👎 {engine} marked as poor quality")
            elif feedback == 'skip':
                print("  ⏭️  Skipping to next engine")
                continue
        except KeyboardInterrupt:
            print("\n⏹️  Test interrupted by user")
            break
        
        print()
    
    print("🏁 TTS testing complete!")
    return True

def test_specific_engine():
    """Test a specific TTS engine interactively"""
    
    tts = VietnameseTTS()
    available_engines = tts.get_available_engines()
    
    if not available_engines:
        print("❌ No TTS engines available!")
        return
    
    print("Available engines:")
    for i, engine in enumerate(available_engines, 1):
        print(f"  {i}. {engine}")
    
    try:
        choice = int(input("\nSelect engine (number): ")) - 1
        if 0 <= choice < len(available_engines):
            selected_engine = available_engines[choice]
        else:
            print("❌ Invalid choice")
            return
    except (ValueError, KeyboardInterrupt):
        print("\n⏹️  Cancelled")
        return
    
    print(f"\n🔊 Testing {selected_engine} engine")
    print("Type Vietnamese text to test (press Enter twice to finish):")
    
    while True:
        try:
            text = input("Text: ").strip()
            if not text:
                break
            
            print(f"🎤 Speaking with {selected_engine}...")
            success = tts.speak(text, engine=selected_engine)
            
            if success:
                print("✅ Success")
            else:
                print("❌ Failed")
                
        except KeyboardInterrupt:
            print("\n⏹️  Stopped")
            break

def benchmark_engines():
    """Benchmark TTS engines for speed and quality"""
    
    print("🏃 Benchmarking TTS engines...")
    
    tts = VietnameseTTS()
    test_text = "Đây là một câu test để đo tốc độ của các engine TTS tiếng Việt."
    
    results = {}
    
    for engine in tts.get_available_engines():
        print(f"\n⏱️  Benchmarking {engine}...")
        
        start_time = time.time()
        success = tts.speak(test_text, engine=engine)
        end_time = time.time()
        
        duration = end_time - start_time
        results[engine] = {
            'duration': duration,
            'success': success
        }
        
        print(f"  Time: {duration:.2f}s, Success: {success}")
    
    print("\n📊 Benchmark Results:")
    print("-" * 30)
    sorted_results = sorted(results.items(), key=lambda x: x[1]['duration'])
    
    for engine, result in sorted_results:
        status = "✅" if result['success'] else "❌"
        print(f"{engine:10} | {result['duration']:6.2f}s | {status}")

def main():
    """Main test menu"""
    
    print("🎛️  Vietnamese TTS Test Menu")
    print("1. Comprehensive test (all engines, multiple sentences)")
    print("2. Test specific engine")
    print("3. Quick demo")
    print("4. Benchmark engines")
    print("5. Exit")
    
    try:
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            test_vietnamese_tts_comprehensive()
        elif choice == "2":
            test_specific_engine()
        elif choice == "3":
            demo_vietnamese_tts()
        elif choice == "4":
            benchmark_engines()
        elif choice == "5":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")

if __name__ == "__main__":
    main()