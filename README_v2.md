# 🎵 RP4 Kids Audio Player & Alarm Clock v2.0

A standalone, child-friendly MP3 player and alarm clock system for Raspberry Pi 4 with a 3.5" touchscreen display.

**NEW in v2.0:** SSH-based media management - No USB drives needed!

![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%204-red)
![OS](https://img.shields.io/badge/OS-Raspberry%20Pi%20OS%2064--bit-green)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Storage](https://img.shields.io/badge/storage-Internal%20%2B%20SSH-orange)

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

### 🌐 SSH Media Management (NEW!)
- Upload media files from any computer on your network
- No USB drives needed!
- Automatic file detection within 60 seconds
- Remote administration via SCP/SFTP
- Secure, administrator-controlled

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
| **Network** | WiFi or Ethernet (for media uploads) |

---

## 🚀 Quick Start

### 1. Flash Raspberry Pi OS

Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to flash **Raspberry Pi OS (64-bit)** to your microSD card.

**Important:** Enable SSH in the advanced settings (⚙️ gear icon)

### 2. Clone and Install

```bash
cd /home/pi
git clone https://github.com/yourusername/rp4layer.git
cd rp4layer
chmod +x setup.sh
./setup.sh
```

### 3. Upload Media Files

From your computer:

```bash
# Upload a bedtime story
scp my-story.mp3 pi@rp4player.local:/home/pi/rp4player/media/stories/

# Upload an alarm sound
scp alarm-sound.mp3 pi@rp4player.local:/home/pi/rp4player/media/alarms/
```

### 4. Start Using!

Files appear in the app within 60 seconds. No restart needed!

---

## 📱 Adding Media Files

### Command Line (Recommended)

```bash
# Single file
scp story.mp3 pi@rp4player.local:/home/pi/rp4player/media/stories/

# Multiple files
scp *.mp3 pi@rp4player.local:/home/pi/rp4player/media/stories/

# Sync entire folder
rsync -av ~/my-stories/ pi@rp4player.local:/home/pi/rp4player/media/stories/
```

### GUI Clients

- **Windows:** [WinSCP](https://winscp.net/)
- **Mac:** [Cyberduck](https://cyberduck.io/)
- **All Platforms:** [FileZilla](https://filezilla-project.org/)

**Connection Details:**
- Host: `rp4player.local`
- Port: 22 (SFTP/SSH)
- Username: `pi`
- Password: [your password]
- Path: `/home/pi/rp4player/media/`

See [MEDIA_MANAGEMENT.md](MEDIA_MANAGEMENT.md) for complete guide.

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
│  Media Scanner    │  State Manager      │
│  (watchdog)       │  (Event Bus)        │
├─────────────────────────────────────────┤
│          JSON Storage Layer             │
│  (alarms, media, settings, playback)    │
├─────────────────────────────────────────┤
│     Raspberry Pi OS (64-bit)            │
│     ALSA Audio → 3.5mm Jack             │
│     SSH Server → Media Uploads          │
└─────────────────────────────────────────┘
```

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
│   ├── media/               # Media scanner & file watcher (NEW!)
│   ├── ui/                  # Kivy UI components
│   └── main.py              # Application entry point
│
├── config/                  # Configuration files
├── data/                    # Data storage (JSON)
├── media/                   # Media files (SSH upload target)
│   ├── alarms/             # Alarm sound files
│   └── stories/            # Story MP3 files
├── mockups/                # UI mockups (HTML)
│
├── ARCHITECTURE.md          # Architecture documentation
├── TECHNICAL_SPECIFICATION_v2.md  # Technical specs (v2.0 SSH)
├── MEDIA_MANAGEMENT.md     # Media upload guide
├── CHANGES_v2.md           # Changes from v1.0
├── setup.sh                # Installation script
└── README_v2.md            # This file
```

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
  },
  "media": {
    "auto_scan": true,
    "scan_interval_seconds": 60
  }
}
```

---

## 🔧 Management Commands

```bash
# Start application
cd /home/pi/rp4player
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
```

---

## 🎨 UI Mockups

Interactive HTML mockups are available in the `mockups/` directory:

```bash
# Open in browser
firefox mockups/index.html
```

Screens included:
- Home Screen - Live clock and navigation
- Alarm List - View and toggle alarms
- Alarm Editor - Create/edit with time picker
- Story Player - Playback controls and library
- Alarm Trigger - Full-screen notification
- Settings - System configuration

---

## 🧪 Testing

```bash
# Run unit tests
cd /home/pi/rp4player
source venv/bin/activate
pytest tests/

# Test audio output
aplay /usr/share/sounds/alsa/Front_Center.wav

# Test SSH upload
scp test.mp3 pi@rp4player.local:/home/pi/rp4player/media/stories/
```

---

## 🐛 Troubleshooting

### Can't Upload Files

```bash
# Check SSH is running
ssh pi@rp4player.local "systemctl status ssh"

# Test connection
ssh pi@rp4player.local

# Check network
ping rp4player.local
```

### Files Not Appearing

1. Wait 60 seconds for automatic scan
2. Check file is .mp3 format
3. Verify upload succeeded:
   ```bash
   ssh pi@rp4player.local "ls -l /home/pi/rp4player/media/stories/"
   ```
4. Check logs:
   ```bash
   ssh pi@rp4player.local "tail -f /home/pi/rp4player/logs/app.log"
   ```
5. Restart app:
   ```bash
   ssh pi@rp4player.local "sudo systemctl restart rp4player"
   ```

### No Audio Output

```bash
# Force 3.5mm output
ssh pi@rp4player.local "amixer cset numid=3 1"

# Test audio
ssh pi@rp4player.local "speaker-test -t wav -c 2"
```

---

## 📚 Documentation

- [Installation Guide](INSTALL_v2.md) - Step-by-step setup
- [Architecture Document](ARCHITECTURE.md) - System design
- [Technical Specification](TECHNICAL_SPECIFICATION_v2.md) - Detailed specs (v2.0)
- [Media Management Guide](MEDIA_MANAGEMENT.md) - Complete upload guide
- [Changes from v1.0](CHANGES_v2.md) - What's new in v2.0
- [UI Mockups](mockups/index.html) - Interactive previews

---

## 🛠️ Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **OS** | Raspberry Pi OS | 64-bit |
| **Language** | Python | 3.9+ |
| **UI Framework** | Kivy | 2.2.1 |
| **Audio** | pygame | 2.5.2 |
| **Scheduling** | APScheduler | 3.10.4 |
| **File Monitoring** | watchdog | 3.0.0 |
| **Metadata** | mutagen | 1.47.0 |
| **Storage** | JSON | Native |
| **Media Transfer** | SSH/SCP | OpenSSH |

---

## 🆕 What's New in v2.0

### Major Changes

✅ **SSH-based media management**
- Upload files from any computer on network
- No USB drives required
- Automatic file detection within 60 seconds
- Remote administration

✅ **File system monitoring**
- Real-time detection of new files
- Automatic library updates
- No manual refresh needed

✅ **Simplified architecture**
- Removed USB hardware dependencies
- Removed USB software stack (pyudev)
- More reliable file management
- Easier maintenance

✅ **Better security**
- Administrator-controlled uploads only
- SSH authentication required
- No physical media for kids to lose

### What Stayed the Same

- All UI features identical
- Kids interact exactly the same way
- Same alarm and story functionality
- Same touchscreen interface
- Same audio quality and performance

See [CHANGES_v2.md](CHANGES_v2.md) for complete details.

---

## 🎯 Roadmap

### Version 2.0 (Current)
- ✅ SSH-based media management
- ✅ Automatic file detection
- ✅ File system monitoring
- ✅ Simplified architecture

### Version 2.1 (Planned)
- [ ] Web-based upload interface
- [ ] Multiple user profiles
- [ ] Volume fade-in for alarms
- [ ] Playlist management

### Version 3.0 (Future)
- [ ] Voice recording feature
- [ ] Parental controls dashboard
- [ ] Cloud story library integration
- [ ] Bluetooth speaker support

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍👩‍👧‍👦 Credits

Designed for kids to manage their own bedtime routines and morning wake-ups independently.

Made with ❤️ for family use.

---

## 📞 Support

For issues and questions:

1. Check [MEDIA_MANAGEMENT.md](MEDIA_MANAGEMENT.md) for upload help
2. Review logs: `ssh pi@rp4player.local "tail -f /home/pi/rp4player/logs/app.log"`
3. See [Troubleshooting](#-troubleshooting) section above
4. Check [CHANGES_v2.md](CHANGES_v2.md) for migration info

---

**Version:** 2.0 (SSH Edition)
**Platform:** Raspberry Pi 4
**Display:** 3.5" Touchscreen (480×320)
**Audio:** 3.5mm Jack Output
**Media:** SSH/SCP Upload (Internal Storage)
