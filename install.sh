echo "🚀 Initiating SILI: The Infinite Mind Upgrade..."

# 1. Clone or Update Repository
if [ ! -d "Sili" ] && [ ! -f "main.py" ]; then
    echo "🛸 Cloning Sili Repository..."
    git clone https://github.com/silitheai/sili.git
    cd sili
elif [ -d "Sili" ]; then
    cd Sili
    echo "🔄 Updating Sili to latest version..."
    git pull origin main
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

echo "✨ Installation complete. Run 'python3 main.py' to start Sili."
