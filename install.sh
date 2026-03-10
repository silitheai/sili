#!/bin/bash

# SILI One-Line Installer
# Usage: curl -sSL https://raw.githubusercontent.com/user/sili/master/install.sh | bash

set -e

echo "🚀 Initiating SILI: The Infinite Mind Upgrade..."

# 1. Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed. Please install it first."
    exit 1
fi

# 2. Setup Virtual Environment
echo "📦 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 3. Install Dependencies
echo "📥 Installing core dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Install Playwright Browsers
echo "🌐 Installing browser binaries (Playwright)..."
playwright install chromium

# 5. Launch Onboarding Wizard
echo "🧠 Launching Onboarding Wizard..."
python3 setup.py

echo "✨ Installation complete. Run 'python3 main.py' to start Sili."
