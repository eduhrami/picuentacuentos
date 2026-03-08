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
- Simple playback controls (play/pause toggle, skip)

### 🌐 SSH Media Management (NEW!)
- Upload media files from any computer on your network
- No USB drives needed!
- Media catalogs loaded at startup (edit JSON + restart)
- Updates handled via PC commands; device use remains child-only
- Secure, administrator-controlled

### 🎨 Child-Friendly Design
- Large touch targets (80×80 pixels minimum)
- High-contrast, colorful interface
- Simple navigation (2-3 levels max)
- Emoji icons for easy recognition
- 480×320 pixel display optimized
- Fixed wallpaper from `/home/pi/picuentacuentos/media/wallpapers/default.png`

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
git clone https://github.com/eduhrami/picuentacuentos.git
cd picuentacuentos
chmod +x setup.sh
./setup.sh
```

### 3. Upload Media Files

From your computer:

```bash
# Upload a bedtime story
scp my-story.mp3 pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/

# Upload an alarm sound + image
scp alarm-sound.mp3 alarm-sound.png \
  pi@picuentacuentos.local:/home/pi/picuentacuentos/media/animal_sounds/
```

### 4. Start Using!

Files appear in the app after editing the JSON catalogs and restarting the app.

---

## 📱 Adding Media Files

### Command Line (Recommended)

```bash
# Single file
scp story.mp3 pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/

# Multiple files
scp *.mp3 pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/

# Sync entire folder
rsync -av ~/my-stories/ pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/
```

### GUI Clients

- **Windows:** [WinSCP](https://winscp.net/)
- **Mac:** [Cyberduck](https://cyberduck.io/)
- **All Platforms:** [FileZilla](https://filezilla-project.org/)

**Connection Details:**
- Host: `picuentacuentos.local`
- Port: 22 (SFTP/SSH)
- Username: `pi`
- Password: [your password]
- Path: `/home/pi/picuentacuentos/media/`

If `picuentacuentos.local` does not resolve, add it to your hosts file:
- Linux/macOS:
  ```bash
  sudo sh -c 'printf "\n192.168.x.x picuentacuentos.local\n" >> /etc/hosts'
  ```
- Windows: add `192.168.x.x picuentacuentos.local` to
  `C:\Windows\System32\drivers\etc\hosts`

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
│  Media Loader     │  State Manager      │
│  (JSON catalogs)  │  (Event Bus)        │
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
picuentacuentos/
├── app/                      # Application source code
│   ├── core/                # Core components (event bus, state)
│   ├── models/              # Data models
│   ├── storage/             # JSON storage layer
│   ├── audio/               # Audio playback engine
│   ├── scheduling/          # Alarm scheduler
│   ├── media/               # Media catalogs (JSON)
│   ├── ui/                  # Kivy UI components
│   └── main.py              # Application entry point
│
├── config/                  # Pi configuration files (mirrored from device)
├── data/                    # Data storage (JSON)
├── docs/                    # Project documentation
├── media/                   # Media files (SSH upload target)
│   ├── animal_sounds/      # Alarm sounds + images
│   │   └── sounds.json     # Alarm catalog
│   └── stories/            # Story MP3 files + icons
│       └── stories.json    # Story catalog
├── mockups/                # UI mockups (HTML)
└── setup.sh                # Installation script
```

---

## ⚙️ Configuration

Edit `/home/pi/picuentacuentos/config/settings.json`:

```json
{
  "audio": {
    "output_device": "hw:0,0"
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
    "sounds_config": "/home/pi/picuentacuentos/media/animal_sounds/sounds.json",
    "stories_config": "/home/pi/picuentacuentos/media/stories/stories.json"
  }
}
```

---

## 🔧 Management Commands

```bash
# Start application (kiosk restarts automatically — use this to apply kiosk.conf changes)
sudo systemctl restart getty@tty1

# View logs
tail -f /home/pi/picuentacuentos/logs/app.log

# Backup configuration
cd /home/pi/picuentacuentos && ./backup.sh

# Check what is running on the display
ps aux | grep -E "Xorg|startx|main.py" | grep -v grep
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
- Alarm Time - Set time and days
- Alarm Sound - Pick alarm sound
- Story Player - Playback controls and library
- Alarm Trigger - Full-screen notification
- Settings - System configuration

---

## 🧪 Testing

```bash
# Run unit tests
cd /home/pi/picuentacuentos
source venv/bin/activate
pytest tests/

# Test audio output
aplay /usr/share/sounds/alsa/Front_Center.wav

# Test SSH upload
scp test.mp3 pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/
```

---

## 🐛 Troubleshooting

### Can't Upload Files

```bash
# Check SSH is running
ssh pi@picuentacuentos.local "systemctl status ssh"

# Test connection
ssh pi@picuentacuentos.local

# Check network
ping picuentacuentos.local

# If hostname doesn't resolve, add to hosts file
sudo sh -c 'printf "\n192.168.x.x picuentacuentos.local\n" >> /etc/hosts'
```

### Files Not Appearing

1. Confirm the JSON catalogs were updated
2. Check file is .mp3 format
3. Verify upload succeeded:
   ```bash
   ssh pi@picuentacuentos.local "ls -l /home/pi/picuentacuentos/media/stories/"
   ```
4. Check logs:
   ```bash
   ssh pi@picuentacuentos.local "tail -f /home/pi/picuentacuentos/logs/app.log"
   ```
5. Restart app:
   ```bash
   ssh pi@picuentacuentos.local "sudo systemctl restart getty@tty1"
   ```

### No Audio Output

Audio is permanently routed to the 3.5mm jack via `/etc/asound.conf` (card 1 = bcm2835 Headphones).

```bash
# Check ALSA default device
ssh pi@picuentacuentos.local "aplay -l"

# Test audio output (no -D flag needed — asound.conf routes to jack)
ssh pi@picuentacuentos.local "aplay /usr/share/sounds/alsa/Front_Center.wav"

# Select audio output device (card 1)
ssh pi@picuentacuentos.local "amixer -c 1 sset PCM 85%"
```

---

## 📚 Documentation

- [Installation Guide](INSTALL.md) - Step-by-step setup
- [Architecture Document](ARCHITECTURE.md) - System design
- [Technical Specification](TECHNICAL_SPECIFICATION.md) - Detailed specs
- [Media Management Guide](MEDIA_MANAGEMENT.md) - Complete upload guide
- [Display & Kiosk Setup](DISPLAY_SETUP.md) - LCD and X server configuration
- [UI Mockups](../mockups/index.html) - Interactive previews

---

## 🛠️ Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **OS** | Raspberry Pi OS | 64-bit |
| **Language** | Python | 3.9+ |
| **UI Framework** | Kivy | 2.2.1 |
| **Audio** | pygame | 2.5.2 |
| **Scheduling** | APScheduler | 3.10.4 |
| **Media Catalogs** | JSON | Native |
| **Storage** | JSON | Native |
| **Media Transfer** | SSH/SCP | OpenSSH |

---

## 🆕 What's New in v2.0

### Major Changes

✅ **SSH-based media management**
- Upload files from any computer on network
- No USB drives required
- JSON-based media catalogs loaded at startup
- Remote administration

✅ **Media catalogs**
- Explicit JSON catalogs for alarm sounds and stories
- Predictable media lists
- No background scanning or file watching

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

See [TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md) for implementation details.

---

## 🎯 Roadmap

### Version 2.0 (Current)
- ✅ SSH-based media management
- ✅ JSON media catalogs loaded at startup
- ✅ Media catalogs (no background scanning)
- ✅ Simplified architecture

### Version 2.1 (Planned)
- [ ] Web-based upload interface
- [ ] Multiple user profiles
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
2. Review logs: `ssh pi@picuentacuentos.local "tail -f /home/pi/picuentacuentos/logs/app.log"`
3. See [Troubleshooting](#-troubleshooting) section above
4. Check [TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md) for migration info

---

**Version:** 2.0 (SSH Edition)
**Platform:** Raspberry Pi 4
**Display:** 3.5" Touchscreen (480×320)
**Audio:** 3.5mm Jack Output
**Media:** SSH/SCP Upload (Internal Storage)
