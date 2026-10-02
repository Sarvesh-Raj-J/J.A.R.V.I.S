#!/bin/bash
# Jarvis Launcher Script for Linux/Mac
# Run: chmod +x start_jarvis.sh && ./start_jarvis.sh

echo "========================================"
echo "      Starting Jarvis Assistant"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if config.json exists
if [ ! -f config.json ]; then
    echo "Configuration file not found!"
    echo "Running setup wizard..."
    echo ""
    python3 setup_wizard.py
    echo ""
    echo "Setup complete! Starting Jarvis..."
    echo ""
fi

# Start Jarvis
python3 jarvis_main.py

# Check exit status
if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "  Jarvis encountered an error"
    echo "  Check jarvis.log for details"
    echo "========================================"
    read -p "Press Enter to exit..."
fi
