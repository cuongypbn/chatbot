#!/bin/bash
# Simple script to run Vietnamese chatbot without display issues

# Go to chatbot directory
cd ~/voice-chatbot

# Activate virtual environment
source .venv/bin/activate

# Suppress EGL errors and run chatbot
export MESA_DEBUG=silent
export EGL_LOG_LEVEL=fatal

echo "🤖 Starting Vietnamese Voice Chatbot..."
echo "   If you see EGL errors, they will be suppressed automatically"
echo "   The chatbot will work fully via voice even without GUI"
echo ""

# Run the chatbot with headless fallback
python3 hdmi_chatbot_vietnamese.py --lang vi "$@" 2>/dev/null || {
    echo "GUI failed, running in audio-only mode..."
    python3 hdmi_chatbot_vietnamese.py --lang vi --headless "$@"
}
