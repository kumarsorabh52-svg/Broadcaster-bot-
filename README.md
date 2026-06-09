# 🤖 Telegram Announcement Bot

Yah bot groups mein announcements bhejne aur schedule karne ke liye hai.

---

## ✨ Features

- 📢 **Multi-Group Announcement** — Ek baar mein sabhi groups mein bhejo
- ⏰ **Schedule Messages** — Date/time set karke schedule karo
- 🔘 **Inline Buttons** — Custom buttons add karo (URL ke saath)
- ✅ **Group Selection** — Checkbox style se groups chunno
- 🗑 **Cancel Scheduled** — Scheduled messages cancel karo

---

## ⚙️ Setup (Step by Step)

### Step 1 — Bot Token Lena
1. Telegram mein `@BotFather` search karo
2. `/newbot` command do
3. Bot ka naam aur username set karo
4. **Token copy kar lo**

### Step 2 — Apna User ID Lena
1. `@userinfobot` ko message karo
2. Woh aapka User ID batayega (jaise: `123456789`)

### Step 3 — Config Setup
`config.py` file kholein aur yah lines update karein:

```python
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ"   # Apna token
ADMIN_IDS = [123456789]                                   # Apna user ID
TIMEZONE = "Asia/Kolkata"                                 # India timezone
```

### Step 4 — Dependencies Install
```bash
chmod +x setup.sh
./setup.sh
```
Ya directly:
```bash
pip3 install -r requirements.txt
```

### Step 5 — Bot Start Karo
```bash
python3 bot.py
```

---

## 👥 Groups Mein Bot Add Karna

1. Bot ko group mein add karo (Admin banao)
2. Group mein koi bhi message aane par bot automatically register ho jaayega
3. Bot ke saath `/start` karein private chat mein

---

## 🚀 VPS / Server Par Run Karna

**Background mein run (nohup):**
```bash
nohup python3 bot.py > bot.log 2>&1 &
```

**Screen ke saath:**
```bash
screen -S telebot
python3 bot.py
# Ctrl+A, D se detach karo
```

**Systemd Service (best tarika):**
```bash
sudo nano /etc/systemd/system/telebot.service
```
Content:
```ini
[Unit]
Description=Telegram Announcement Bot
After=network.target

[Service]
User=root
WorkingDirectory=/path/to/telegram-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable telebot
sudo systemctl start telebot
sudo systemctl status telebot
```

---

## 📱 Bot Use Karna

1. `/start` — Bot start karo (private chat mein)
2. **📢 New Announcement** — Naya announcement banao
   - Groups select karo (✅/⬜)
   - Message likhо
   - Inline buttons add karo (optional)
   - Abhi bhejo ya schedule karo
3. **⏰ Scheduled Messages** — Scheduled messages dekho/cancel karo
4. **👥 Registered Groups** — Registered groups list dekho

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| Bot respond nahi kar raha | Token check karo config.py mein |
| Group mein nahi bhej pa raha | Bot ko group admin banao |
| Scheduled message nahi gaya | Server ka time check karo, TIMEZONE setting dekho |
| "Aap admin nahi hain" | ADMIN_IDS mein apna user ID add karo |

---

## 📁 Files

```
telegram-bot/
├── bot.py          # Main bot code
├── config.py       # Configuration (token, admin IDs)
├── requirements.txt # Dependencies
├── setup.sh        # Setup script
├── data.json       # Groups & scheduled data (auto-create)
└── README.md       # Yah file
```
