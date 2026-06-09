#!/bin/bash

echo "🤖 Telegram Announcement Bot Setup"
echo "==================================="

# Python check
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 nahi mila. Install karein:"
    echo "   sudo apt update && sudo apt install python3 python3-pip -y"
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Install dependencies
echo ""
echo "📦 Dependencies install ho rahi hain..."
pip3 install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "⚙️  Ab config.py mein apna BOT_TOKEN aur ADMIN_ID daalo"
echo ""
echo "▶️  Bot start karne ke liye:"
echo "   python3 bot.py"
echo ""
echo "📌 Background mein run karne ke liye:"
echo "   nohup python3 bot.py &"
echo "   ya"
echo "   screen -S bot python3 bot.py"
