# RP4 Kids Audio Player - Installation Guide

This guide walks you through installing the RP4 Kids Audio Player on a Raspberry Pi 4
with a 3.5" SPI LCD touchscreen in kiosk mode (no desktop environment required).

## Prerequisites

### Hardware Requirements
- Raspberry Pi 4 (2GB+ RAM recommended)
- 3.5" SPI touchscreen display (ILI9486, 480x320)
- MicroSD card (16GB minimum, 32GB+ recommended)
- 3.5mm speakers or headphones
- USB-C power supply (5V 3A)
- Network access (for SSH media updates)

### Software Requirements
- Raspberry Pi OS Lite (64-bit) — no desktop environment needed
- Internet connection (for initial setup only)

---

## Step 1: Flash Raspberry Pi OS

### Using Raspberry Pi Imager:

1. **Download Raspberry Pi Imager:**
   - https://www.raspberrypi.com/software/

2. **Flash the OS:**
   - Insert microSD card into your computer
   - Open Raspberry Pi Imager
   - Click "Choose OS" → **Raspberry Pi OS (other)** → **Raspberry Pi OS Lite (64-bit)**
   - Click "Choose Storage" and select your microSD card

3. **Configure Settings (⚙️ gear icon):**
   - Set hostname: `picuentacuentos` (advertises as `picuentacuentos.local`)
   - Enable SSH: ✓ (required for setup and troubleshooting)
   - Set username: `pi`
   - Set password: (your choice)
   - Configure WiFi: ✓ (needed for initial package installation)
   - Set locale: Your timezone and keyboard layout
   - Click "Save"

4. **Write:**
   - Click "Write", wait for completion (~5 minutes)
   - Safely eject microSD card

---

## Step 2: First Boot & Display Setup

1. **Insert microSD** into Raspberry Pi and connect power (do not connect a monitor —
   the 3.5" LCD is the only display).

2. **SSH into the Pi** once it appears on the network:
   ```bash
   ssh pi@picuentacuentos.local
   ```
   If `picuentacuentos.local` does not resolve, add it on your PC:
   - Linux/macOS:
     ```bash
     sudo sh -c 'printf "\n192.168.x.x picuentacuentos.local\n" >> /etc/hosts'
     ```
   - Windows: add `192.168.x.x picuentacuentos.local` to
     `C:\Windows\System32\drivers\etc\hosts`

3. **Enable the LCD display driver** by editing the boot config:
   ```bash
   sudo nano /boot/firmware/config.txt
   ```
   Add at the end:
   ```
   dtoverlay=tft35a:rotate=90
   ```

4. **Disable console screen blanking** — edit the kernel command line:
   ```bash
   sudo nano /boot/firmware/cmdline.txt
   ```
   Append `consoleblank=0` to the single line (do not add a new line):
   ```
   ... rootwait cfg80211.ieee80211_regdom=MX consoleblank=0
   ```

5. **Reboot** to activate the LCD driver:
   ```bash
   sudo reboot
   ```
   After reboot, SSH back in and verify the LCD framebuffer exists:
   ```bash
   ls /dev/fb1          # should exist
   cat /sys/class/graphics/fb1/name   # should print: fb_ili9486
   ```

---

## Step 3: Configure X Server for the LCD

The app runs under X server, which renders directly to the LCD framebuffer.
No desktop environment is installed — X is started automatically on boot.

### 3a. Install required packages

```bash
sudo apt-get update
sudo apt-get install -y \
    xserver-xorg-core \
    xserver-xorg-video-fbdev \
    xinit \
    x11-apps \
    python3-pip \
    python3-venv
```

### 3b. Configure X to use the LCD

```bash
sudo mkdir -p /etc/X11/xorg.conf.d
sudo cp /home/pi/picuentacuentos/config/etc/X11/xorg.conf.d/99-fbdev.conf \
        /etc/X11/xorg.conf.d/99-fbdev.conf
```

Or create it manually:
```bash
sudo nano /etc/X11/xorg.conf.d/99-fbdev.conf
```
```
Section "Device"
  Identifier "LCD"
  Driver "fbdev"
  Option "fbdev" "/dev/fb1"
EndSection

Section "Monitor"
  Identifier "LCD Monitor"
EndSection

Section "Screen"
  Identifier "LCD Screen"
  Device "LCD"
  Monitor "LCD Monitor"
  DefaultDepth 16
  SubSection "Display"
    Depth 16
    Modes "480x320"
  EndSubSection
EndSection

Section "ServerLayout"
  Identifier "LCD Layout"
  Screen "LCD Screen"
EndSection
```

### 3c. Enable auto-login on tty1

```bash
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
sudo cp /home/pi/picuentacuentos/config/etc/systemd/system/getty@tty1.service.d/autologin.conf \
        /etc/systemd/system/getty@tty1.service.d/autologin.conf
```

Or create it manually:
```bash
sudo nano /etc/systemd/system/getty@tty1.service.d/autologin.conf
```
```ini
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin pi --noclear %I $TERM
```

### 3d. Configure auto-start of X on login

```bash
cp /home/pi/picuentacuentos/config/home/pi/.bash_profile /home/pi/.bash_profile
cp /home/pi/picuentacuentos/config/home/pi/.xinitrc      /home/pi/.xinitrc
cp /home/pi/picuentacuentos/config/home/pi/kiosk.conf    /home/pi/kiosk.conf
```

Boot sequence after this:
1. systemd auto-logs in `pi` on tty1
2. `.bash_profile` starts X in a restart loop
3. X starts on `/dev/fb1` using the fbdev driver
4. `.xinitrc` reads `kiosk.conf` and launches the app in a restart loop

### 3e. Test X is working

Reboot and verify:
```bash
sudo reboot
# after reboot, SSH back in:
ps aux | grep Xorg | grep -v grep    # should show Xorg running
DISPLAY=:0 xeyes &                   # xeyes should appear on the LCD
```

### 3f. Disable unnecessary services (boot time optimisation)

Raspberry Pi OS ships with several services that serve no purpose on a dedicated
kiosk and add 60–90 seconds to boot time. Disable them:

```bash
# cloud-init: for cloud VM provisioning — useless on a Pi, costs ~60s on the
# critical chain (blocks plymouth-quit-wait until all cloud tasks time out)
sudo touch /etc/cloud/cloud-init.disabled
sudo systemctl disable cloud-init cloud-init-local cloud-init-network \
    cloud-config cloud-final cloud-init-hotplugd.socket

# LightDM: display manager that conflicts with the custom startx kiosk setup
sudo systemctl disable lightdm.service

# CUPS: print scheduler — not needed on an audio player
sudo systemctl disable cups.service cups-browsed.service cups.path cups.socket

# WayVNC: Wayland VNC server — not used (kiosk runs X11, not Wayland)
sudo systemctl disable wayvnc-control.service
```

After applying, reboot and verify boot time with:
```bash
systemd-analyze time
systemd-analyze blame --no-pager | head -20
```

Expected total boot time after these changes: **under 20 seconds**.

---

## Step 4: Install PiCuentaCuentos

```bash
# Clone or copy the project
cd /home/pi
git clone https://github.com/eduhrami/picuentacuentos.git
cd /home/pi/picuentacuentos

# Create Python virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install kivy
```

---

## Step 5: Add Media Files

### Directory structure:

```
/home/pi/picuentacuentos/media/
└── stories/
    ├── stories.json
    ├── three-little-pigs.mp3
    └── goldilocks.mp3

/home/pi/picuentacuentos/assets/
├── animal_sounds/
│   ├── sounds.json
│   ├── rooster.mp3
│   └── rooster.png
└── icons/
    ├── book.png        # Home Stories icon (128px)
    ├── bell.png        # Home Alarms icon (128px)
    ├── back.png        # Back arrow for sub-screens
    └── home.png        # Home icon for list screens
```

### Copy files:

```bash
rsync -av your-alarm.mp3 your-alarm.png \
    pi@picuentacuentos.local:/home/pi/picuentacuentos/assets/animal_sounds/
rsync -av your-story.mp3 \
    pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/
```

**Recommended MP3 format:** 128kbps+, 44.1kHz stereo
**Alarm sounds:** 2–30 seconds | **Stories:** 5–30 minutes

---

## Step 6: Configure the Kiosk App

Edit `~/kiosk.conf` on the Pi to point to the PiCuentaCuentos:

```bash
nano /home/pi/kiosk.conf
```

Change `KIOSK_APP` to:
```bash
KIOSK_APP="/home/pi/picuentacuentos/venv/bin/python /home/pi/picuentacuentos/app/main.py"
KIOSK_DISPLAY=":0"
```

Apply without rebooting:
```bash
sudo systemctl restart getty@tty1
```

The app will appear on the LCD within a few seconds.

---

## Step 7: Test the Application

### Manual test (SSH):

```bash
# Verify the app process is running
ps aux | grep main.py | grep -v grep

# Watch application logs
tail -f /home/pi/picuentacuentos/logs/app.log
```

### On the LCD you should see:
- Home screen with current time
- Alarms button
- Stories button
- Settings button

**Test checklist:**
- [ ] Touchscreen responds to touch
- [ ] Audio plays through 3.5mm jack
- [ ] Can navigate between screens
- [ ] Can set an alarm
- [ ] Can play a story

---

## Step 8: Final Configuration

### Audio output:

```bash
# Force audio to 3.5mm jack
amixer cset numid=3 1

# Test audio
speaker-test -t wav -c 2

# Adjust volume using your external speaker controls
```

### Touchscreen calibration (if touches seem off):

```bash
sudo apt-get install xinput-calibrator
DISPLAY=:0 xinput_calibrator
```

### Reboot and verify kiosk starts automatically:

```bash
sudo reboot
# After ~30 seconds the app should appear on the LCD without any intervention
```

---

## Updating Media

Media updates are handled from a PC via SSH commands; device operation remains
child-only. See `docs/MEDIA_MANAGEMENT.md` for the full catalog format and
update workflow.

---

## Routine Deployment (code update)

Use the `deploy-to-pi` skill for the standard workflow, or run manually from the
dev machine:

```bash
# 1. Sync updated code (excludes venv and data, includes media)
rsync -avz --exclude='venv/' --exclude='data/' --exclude='.git/' \
    /home/tozanni/src/picuentacuentos/ \
    pi@picuentacuentos.local:/home/pi/picuentacuentos/

# 2. Update Python dependencies if needed
ssh pi@picuentacuentos.local '
    cd /home/pi/picuentacuentos
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
    pip install kivy
'

# 3. Restart the kiosk to pick up the new code
ssh pi@picuentacuentos.local 'sudo systemctl restart getty@tty1'
```

---

## Troubleshooting

### LCD shows nothing after boot

```bash
# Verify framebuffer device exists
ls /dev/fb1

# Check LCD driver loaded
dmesg | grep -i ili9486

# Check boot config has the overlay
grep tft35a /boot/firmware/config.txt
```

### X server not starting

```bash
# Check if Xorg process is running
ps aux | grep Xorg | grep -v grep

# Check X startup log
cat /tmp/x_startup.log

# Check detailed Xorg log
cat ~/.local/share/xorg/Xorg.0.log | grep -E "EE|WW|fb1"

# Manually trigger a restart
sudo systemctl restart getty@tty1
```

### App not appearing on LCD

```bash
# Check kiosk.conf has the correct command
cat ~/kiosk.conf

# Check the app process
ps aux | grep main.py | grep -v grep

# Test manually on the X display
DISPLAY=:0 /home/pi/picuentacuentos/venv/bin/python /home/pi/picuentacuentos/app/main.py

# Revert to xeyes to confirm X itself is working
nano ~/kiosk.conf   # set KIOSK_APP="xeyes -geometry 480x320+0+0"
sudo systemctl restart getty@tty1
```

### No audio output

```bash
aplay -l                        # list audio devices
amixer cset numid=3 1           # force 3.5mm output
aplay /usr/share/sounds/alsa/Front_Center.wav   # test
```

### Python package errors

```bash
cd /home/pi/picuentacuentos
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install kivy
```

### Reset to default settings

```bash
rm /home/pi/picuentacuentos/data/alarms.json
rm /home/pi/picuentacuentos/config/settings.json
sudo systemctl restart getty@tty1
# files will be recreated with defaults on next start
```

---

## Rollback

To restore the previous version of a file or revert a bad deploy, re-sync from a
known good state on the dev machine:

```bash
# Hard-reset dev working tree to last commit, then re-deploy
git -C /home/tozanni/src/picuentacuentos checkout .
rsync -avz --exclude='venv/' --exclude='data/' --exclude='.git/' \
    /home/tozanni/src/picuentacuentos/ \
    pi@picuentacuentos.local:/home/pi/picuentacuentos/
ssh pi@picuentacuentos.local 'sudo systemctl restart getty@tty1'
```

To fall back to `xeyes` on the LCD while diagnosing a broken app:

```bash
ssh pi@picuentacuentos.local "
    sed -i 's|^KIOSK_APP=.*|KIOSK_APP=\"xeyes -geometry 480x320+0+0\"|' /home/pi/kiosk.conf
    sudo systemctl restart getty@tty1
"
```

---

## Helper Scripts

| Script | Purpose |
|--------|---------|
| `start.sh` | Launch the app manually for testing (sets DISPLAY=:0) |
| `stop.sh` | Kill the running app (kiosk loop will restart it after 1s) |
| `backup.sh` | Backup configuration and data |
| `update.sh` | Pull latest code from git |

---

## Advanced Configuration

### Audio output

Volume is controlled by the external speaker hardware.

### Change sleep timer default

```json
{
  "stories": {
    "default_sleep_timer_minutes": 30
  }
}
```

### Configure media catalogs

```json
{
  "media": {
    "sounds_config": "/home/pi/picuentacuentos/assets/animal_sounds/sounds.json",
    "stories_config": "/home/pi/picuentacuentos/media/stories/stories.json"
  }
}
```

### Wallpaper

Wallpaper is fixed at `/home/pi/picuentacuentos/media/wallpapers/default.png`.

---

## System Information

### View status:

```bash
# Is the app running?
ps aux | grep main.py | grep -v grep

# Is X running?
ps aux | grep Xorg | grep -v grep

# System resources
htop

# Disk space
df -h

# Audio devices
aplay -l
```

### View logs:

```bash
# Application log
tail -f /home/pi/picuentacuentos/logs/app.log

# X server startup log
cat /tmp/x_startup.log

# Xorg detail log
cat ~/.local/share/xorg/Xorg.0.log
```

---

**Version:** 2.0
**Last Updated:** 2026-03-06
**Compatible with:** Raspberry Pi OS Lite (64-bit) on Raspberry Pi 4
**Display:** 3.5" ILI9486 SPI LCD, 480x320, kiosk mode via X server on /dev/fb1
