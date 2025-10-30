#!/bin/bash
# Ultra Simple Fix - Just install ollama and run

# Go to the right directory
cd ~/voice-chatbot

# Use explicit venv paths to avoid "externally managed" error
.venv/bin/pip install ollama faster-whisper gtts opencv-python pygame sounddevice requests python-dotenv

# Test the import
.venv/bin/python3 -c "import ollama; print('✅ ollama ready!')"

# Run chatbot
export DISPLAY=:0
.venv/bin/python3 hdmi_chatbot_vietnamese.py --lang vi
