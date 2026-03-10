#!/bin/bash

# Sili One-Click Installer
echo "=========================================="
echo "    Installing Sili (V3 Supreme)      "
echo "=========================================="

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "[!] Python3 could not be found. Please install Python 3.10+ and try again."
    exit 1
fi

# 2. Setup Virtual Environment
echo "[*] Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 3. Install Dependencies
echo "[*] Installing required packages (this may take a minute due to ChromaDB)..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "[!] requirements.txt not found! Ensure you are running this from the Sili root directory."
    exit 1
fi

# 4. Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "[!] Ollama is not installed. Sili relies on Ollama for local inference."
    echo "    Please install Ollama from https://ollama.com before continuing."
else
    echo "[*] Verifying recommended models exist..."
    # Fire off pull requests in the background so the user doesn't wait forever, 
    # but the models become available eventually.
    ollama pull llama3.1 &>/dev/null &
    ollama pull llama3.2-vision &>/dev/null &
    ollama pull nomic-embed-text &>/dev/null &
fi

echo "=========================================="
echo "   Installation Complete! Starting Setup  "
echo "=========================================="

# 5. Run Onboarding
python3 setup.py

echo ""
echo "You can now run your agent:"
echo "CLI Mode:      source venv/bin/activate && python3 main.py '<your goal>'"
echo "Telegram Mode: source venv/bin/activate && python3 telegram_bot.py"
