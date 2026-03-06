# 🎵 RP4 Kids Audio Player & Alarm Clock

A standalone, child-friendly MP3 player and alarm clock system for Raspberry Pi 4 with a 3.5" touchscreen display.

![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%204-red)
![OS](https://img.shields.io/badge/OS-Raspberry%20Pi%20OS%2064--bit-green)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-yellow)

---

## 🎯 Features

### 🔔 Alarm Management
- Set multiple alarms with custom schedules
- Choose different alarm sounds for each alarm
- Repeat patterns: weekdays, weekends, daily, custom days
- Snooze and auto-dismiss functionality
- Large, kid-friendly interface

### 📖 Bedtime Story Player
- Browse and play MP3 story files
- Sleep timer with auto-stop
- Resume playback from last position
- Simple playback controls (play, pause, skip)
- Playlist support

### 💾 USB Media Updates
- Plug-and-play media updates
- Automatic file synchronization
- No WiFi or computer needed after setup
- Supports unlimited stories and alarm sounds

### 🎨 Child-Friendly Design
- Large touch targets (80×80 pixels minimum)
- High-contrast, colorful interface
- Simple navigation (2-3 levels max)
- Emoji icons for easy recognition
- 480×320 pixel display optimized

---

## 📋 Hardware Requirements

| Component | Specification |
|-----------|--------------|
| **Board** | Raspberry Pi 4 (2GB+ RAM) |
| **Display** | 3.5" touchscreen (SPI/HDMI) |
| **Storage** | 64GB microSD card (16GB minimum) |
| **Audio** | 3.5mm speakers or headphones |
| **Power** | 5V 3A USB-C adapter |
| **Media** | USB flash drive for updates |

---

## 🚀 Quick Start

### 1. Flash Raspberry Pi OS

Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to flash **Raspberry Pi OS (64-bit)** to your microSD card.

### 2. Clone and Install

```bash
cd /home/pi
git clone https://github.com/yourusername/rp4layer.git
cd rp4layer
chmod +x setup.sh
./setup.sh
```

### 3. Add Media Files

```bash
# Add alarm sounds
cp *.mp3 /home/pi/rp4player/media/alarms/

# Add stories
cp *.mp3 /home/pi/rp4player/media/stories/
```

### 4. Start the App

```bash
cd /home/pi/rp4player
./start.sh
```

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Kivy UI Framework               │
│  (Touchscreen Interface - 480×320)      │
├─────────────────────────────────────────┤
│  Alarm Scheduler  │  Audio Engine       │
│  (APScheduler)    │  (pygame)           │
├─────────────────────────────────────────┤
│  USB Monitor      │  State Manager      │
│  (pyudev)         │  (Event Bus)        │
├─────────────────────────────────────────┤
│          JSON Storage Layer             │
│  (alarms, media, settings, playback)    │
├─────────────────────────────────────────┤
│     Raspberry Pi OS (64-bit)            │
│     ALSA Audio → 3.5mm Jack             │
└─────────────────────────────────────────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

---

## 📁 Project Structure

```
rp4layer/
├── app/                      # Application source code
│   ├── core/                # Core components (event bus, state)
│   ├── models/              # Data models
│   ├── storage/             # JSON storage layer
│   ├── audio/               # Audio playback engine
│   ├── scheduling/          # Alarm scheduler
│   ├── usb/                 # USB detection & sync
│   ├── ui/                  # Kivy UI components
│   │   ├── screens/        # Screen definitions
│   │   └── widgets/        # Custom widgets
│   └── main.py             # Application entry point
│
├── config/                  # Configuration files
│   └── settings.json       # Application settings
│
├── data/                    # Data storage
│   ├── alarms.json         # Alarm definitions
│   ├── media.json          # Media library
│   └── playback.json       # Playback state
│
├── media/                   # Media files
│   ├── alarms/             # Alarm sound files
│   └── stories/            # Story MP3 files
│
├── assets/                  # UI assets
│   ├── fonts/              # Fonts
│   ├── icons/              # Icons
│   └── kv/                 # Kivy layout files
│
├── mockups/                 # UI mockups (HTML)
├── logs/                    # Application logs
├── tests/                   # Unit tests
│
├── setup.sh                 # Installation script
├── requirements.txt         # Python dependencies
├── INSTALL.md              # Installation guide
├── ARCHITECTURE.md         # Architecture documentation
├── TECHNICAL_SPECIFICATION.md  # Technical specs
└── README.md               # This file
```

---

## 🎨 UI Mockups

Interactive HTML mockups are available in the `mockups/` directory:

```bash
# Open in browser
firefox mockups/index.html
```

Or view online: [UI Mockups Gallery](mockups/index.html)

Screens included:
- Home Screen
- Alarm List
- Alarm Editor
- Story Player
- Alarm Trigger
- Settings

---

## ⚙️ Configuration

Edit `/home/pi/rp4player/config/settings.json`:

```json
{
  "audio": {
    "default_volume": 0.7,
    "alarm_volume": 0.8,
    "max_volume": 0.85
  },
  "display": {
    "brightness": 80,
    "auto_dim_timeout": 30
  },
  "alarms": {
    "snooze_duration_minutes": 5,
    "auto_dismiss_minutes": 10
  },
  "stories": {
    "default_sleep_timer_minutes": 30,
    "resume_playback": true
  }
}
```

---

## 🔧 Management Commands

```bash
# Start application
./start.sh

# Stop application
./stop.sh

# Backup configuration
./backup.sh

# View logs
tail -f logs/app.log

# System service management
sudo systemctl status rp4player
sudo systemctl restart rp4player
sudo systemctl stop rp4player
```

---

## 📱 USB Media Updates

To add media files without computer access:

1. **Prepare USB drive:**
   ```
   USB_DRIVE/
   ├── alarms/
   │   └── new-alarm.mp3
   └── stories/
       └── new-story.mp3
   ```

2. **Insert USB** into Raspberry Pi

3. **Wait for sync notification**

4. **Remove USB** safely

New files automatically appear in the app!

---

## 🧪 Testing

```bash
# Run unit tests
cd /home/pi/rp4player
source venv/bin/activate
pytest tests/

# Test audio output
aplay /usr/share/sounds/alsa/Front_Center.wav

# Test touchscreen
evtest /dev/input/event0
```

---

## 🐛 Troubleshooting

### No Audio Output
```bash
# Force 3.5mm output
amixer cset numid=3 1

# Test audio
speaker-test -t wav -c 2
```

### Touchscreen Not Responding
```bash
# Check input devices
ls /dev/input/

# Calibrate touchscreen
DISPLAY=:0.0 xinput_calibrator
```

### App Won't Start
```bash
# Check logs
tail -f /home/pi/rp4player/logs/app.log

# Check service status
sudo systemctl status rp4player

# Reinstall dependencies
cd /home/pi/rp4player
source venv/bin/activate
pip install -r requirements.txt
```

See [INSTALL.md](INSTALL.md) for more troubleshooting tips.

---

## 📚 Documentation

- [Installation Guide](INSTALL.md) - Step-by-step setup instructions
- [Architecture Document](ARCHITECTURE.md) - System design and architecture
- [Technical Specification](TECHNICAL_SPECIFICATION.md) - Detailed technical specs
- [UI Mockups](mockups/index.html) - Interactive interface previews

---

## 🛠️ Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **OS** | Raspberry Pi OS | 64-bit |
| **Language** | Python | 3.9+ |
| **UI Framework** | Kivy | 2.2.1 |
| **Audio** | pygame | 2.5.2 |
| **Scheduling** | APScheduler | 3.10.4 |
| **USB** | pyudev | 0.24.1 |
| **Metadata** | mutagen | 1.47.0 |
| **Storage** | JSON | Native |

---

## 🎯 Roadmap

### Version 1.0 (Current)
- ✅ Basic alarm management
- ✅ Story playback with sleep timer
- ✅ USB media sync
- ✅ Touch interface

### Version 1.1 (Planned)
- [ ] Multiple user profiles
- [ ] Volume fade-in for alarms
- [ ] Voice recording feature
- [ ] Parental controls

### Version 2.0 (Future)
- [ ] WiFi remote control
- [ ] Nightlight feature
- [ ] Bluetooth speaker support
- [ ] Cloud story library

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 👨‍👩‍👧‍👦 Credits

Designed for kids to manage their own bedtime routines and morning wake-ups independently.

Made with ❤️ for family use.

---

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check [INSTALL.md](INSTALL.md) for troubleshooting
- Review logs: `/home/pi/rp4player/logs/app.log`

---

**Version:** 1.0
**Platform:** Raspberry Pi 4
**Display:** 3.5" Touchscreen (480×320)
**Audio:** 3.5mm Jack Output
