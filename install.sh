echo "🚀 Initiating SILI: The Infinite Mind Upgrade..."

# 1. Clone or Update Repository
if [ -d ".git" ] || [ -f "main.py" ]; then
    echo "🔄 Sili directory detected. Updating to latest version..."
    git pull origin main || echo "⚠️ Could not pull latest changes. Proceeding with local files."
elif [ -d "Sili" ]; then
    cd Sili
    echo "🔄 Updating Sili to latest version..."
    git pull origin main
else
    echo "🛸 Cloning Sili Repository..."
    git clone https://github.com/silitheai/sili.git
    cd sili
fi

# 2. Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed. Please install it first."
    exit 1
fi

# 3. Setup Virtual Environment
echo "📦 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate || source venv/Scripts/activate

# 4. Install Dependencies
echo "📥 Installing core dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. Install Playwright Browsers
echo "🌐 Installing browser binaries (Playwright)..."
playwright install chromium

# 6. Launch Onboarding Wizard
echo "🧠 Launching Onboarding Wizard..."
python3 setup.py

# 7. Register Global Commands
echo "🛠 Registering global CLI commands..."
ABS_PATH=$(pwd)
echo "alias start-sili='cd $ABS_PATH && source venv/bin/activate && python3 telegram_bot.py'" >> ~/.zshrc
echo "alias sili-setup='cd $ABS_PATH && source venv/bin/activate && python3 setup.py'" >> ~/.zshrc
echo "alias sili-cli='cd $ABS_PATH && source venv/bin/activate && python3 main.py'" >> ~/.zshrc

echo "✨ Installation complete. Please run 'source ~/.zshrc' to enable commands."
echo "🚀 Run 'start-sili' to begin."
