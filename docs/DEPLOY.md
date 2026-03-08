# PiCuentaCuentos - Deployment Guide

**Target device:** `cuentacuentos` — Raspberry Pi 4, IP `192.168.100.150`
**SSH user:** `pi`
**App path on Pi:** `/home/pi/src/rp4layer/`
**Dev machine source:** `/home/tozanni/src/rp4layer/`

All commands below run from the **dev machine** unless otherwise noted.

---

## Prerequisites

The Pi must already have the kiosk stack configured (LCD driver, X server,
autologin, `.bash_profile`, `.xinitrc`). If starting from a fresh SD card,
run the `pi-first-setup` skill first, then return here.

Verify the Pi is ready:

```bash
ssh pi@192.168.100.150 'ls /dev/fb1 && ps aux | grep Xorg | grep -v grep'
```

Expected: `/dev/fb1` listed and an Xorg process running on `:0`.

---

## First-Time Deployment

### 1. Create the directory on the Pi

```bash
ssh pi@192.168.100.150 'mkdir -p /home/pi/src/rp4layer'
```

### 2. Sync all project files to the Pi

```bash
rsync -avz --exclude='venv/' --exclude='data/' --exclude='.git/' \
    /home/tozanni/src/rp4layer/ \
    pi@192.168.100.150:/home/pi/src/rp4layer/
```

### 3. Install system dependencies (on the Pi)

```bash
ssh pi@192.168.100.150 'sudo apt-get update && sudo apt-get install -y \
    python3-dev python3-pip python3-venv \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libasound2-dev alsa-utils'
```

### 4. Create the Python virtual environment (on the Pi)

```bash
ssh pi@192.168.100.150 '
    cd /home/pi/src/rp4layer
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
'
```

> Kivy with Cython takes 10–20 minutes to compile on the Pi. This is normal.

### 5. Install system config files

These files are already synced in step 2 under `config/`. Copy them into place:

```bash
ssh pi@192.168.100.150 '
    # X server: use /dev/fb1 at 480x320 16-bit
    sudo cp /home/pi/src/rp4layer/config/etc/X11/xorg.conf.d/99-fbdev.conf \
            /etc/X11/xorg.conf.d/99-fbdev.conf

    # ALSA: route audio to 3.5mm analog jack (card 1)
    sudo cp /home/pi/src/rp4layer/config/etc/asound.conf /etc/asound.conf

    # Autologin for user pi on tty1
    sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
    sudo cp /home/pi/src/rp4layer/config/etc/systemd/system/getty@tty1.service.d/autologin.conf \
            /etc/systemd/system/getty@tty1.service.d/autologin.conf

    # Shell startup: auto-launch X on tty1
    cp /home/pi/src/rp4layer/config/home/pi/.bash_profile /home/pi/.bash_profile
    cp /home/pi/src/rp4layer/config/home/pi/.xinitrc      /home/pi/.xinitrc
'
```

### 6. Create runtime directories and initialise data files

```bash
ssh pi@192.168.100.150 '
    cd /home/pi/src/rp4layer
    mkdir -p data/backups logs media/animal_sounds media/stories

    # Default alarm store (only if it does not already exist)
    [ -f data/alarms.json ] || echo "{\"alarms\": []}" > data/alarms.json

    # Default settings (only if it does not already exist)
    if [ ! -f config/settings.json ]; then
        cat > config/settings.json <<EOF
{
  "audio": { "default_volume": 0.7, "alarm_volume": 0.8, "max_volume": 1.0 },
  "display": { "brightness": 80, "auto_dim_timeout": 30 },
  "alarms": { "snooze_duration_minutes": 5, "auto_dismiss_minutes": 10, "max_alarms": 5 },
  "stories": { "default_sleep_timer_minutes": 30, "resume_playback": true },
  "media": {
    "sounds_config": "/home/pi/src/rp4layer/media/animal_sounds/sounds.json",
    "stories_config": "/home/pi/src/rp4layer/media/stories/stories.json"
  },
  "system": { "log_level": "INFO", "log_file": "/home/pi/src/rp4layer/logs/app.log" }
}
EOF
    fi
'
```

### 7. Point the kiosk at the app

```bash
ssh pi@192.168.100.150 "cat > /home/pi/kiosk.conf <<'EOF'
KIOSK_APP=\"/home/pi/src/rp4layer/venv/bin/python /home/pi/src/rp4layer/app/main.py\"
KIOSK_DISPLAY=\":0\"
EOF"
```

### 8. Restart the kiosk session

```bash
ssh pi@192.168.100.150 'sudo systemctl restart getty@tty1'
```

The app should appear on the LCD within a few seconds.

---

## Routine Deployment (code update)

Use the `deploy-to-pi` skill for the standard workflow, or run manually:

```bash
# 1. Sync updated code (excludes venv, media, and user data)
rsync -avz --exclude='venv/' --exclude='media/' --exclude='data/' --exclude='.git/' \
    /home/tozanni/src/rp4layer/ \
    pi@192.168.100.150:/home/pi/src/rp4layer/

# 2. Update Python dependencies if requirements.txt changed
ssh pi@192.168.100.150 '
    cd /home/pi/src/rp4layer
    source venv/bin/activate
    pip install -q -r requirements.txt
'

# 3. Restart the kiosk to pick up the new code
ssh pi@192.168.100.150 'sudo systemctl restart getty@tty1'
```

---

## Deploying Media Files

Media is managed via JSON catalogue files.
See `docs/MEDIA_MANAGEMENT.md` for the full catalogue format.

### Copy new files to the Pi

```bash
# A new story (MP3 required, PNG icon optional)
scp my-story.mp3 pi@192.168.100.150:/home/pi/src/rp4layer/media/stories/
scp my-story-icon.png pi@192.168.100.150:/home/pi/src/rp4layer/media/stories/

# A new animal sound (both MP3 and PNG required)
scp frog.mp3 frog.png pi@192.168.100.150:/home/pi/src/rp4layer/media/animal_sounds/
```

### Update the catalogue on the Pi

```bash
ssh pi@192.168.100.150 'nano /home/pi/src/rp4layer/media/stories/stories.json'
# or
ssh pi@192.168.100.150 'nano /home/pi/src/rp4layer/media/animal_sounds/sounds.json'
```

### Restart to reload

```bash
ssh pi@192.168.100.150 'sudo systemctl restart getty@tty1'
```

---

## Verification

```bash
# App process is alive
ssh pi@192.168.100.150 'ps aux | grep main.py | grep -v grep'

# X server is running
ssh pi@192.168.100.150 'ps aux | grep Xorg | grep -v grep'

# Tail the application log
ssh pi@192.168.100.150 'tail -f /home/pi/src/rp4layer/logs/app.log'

# Test audio output
ssh pi@192.168.100.150 'aplay /usr/share/sounds/alsa/Front_Center.wav'
```

The LCD should show the home screen with the current time and three navigation
buttons (Stories, Alarms, Settings).

---

## Rollback

To restore the previous version of a file or revert a bad deploy,
re-sync from a known good state on the dev machine:

```bash
# Hard-reset dev working tree to last commit, then re-deploy
git -C /home/tozanni/src/rp4layer checkout .
rsync -avz --exclude='venv/' --exclude='media/' --exclude='data/' --exclude='.git/' \
    /home/tozanni/src/rp4layer/ \
    pi@192.168.100.150:/home/pi/src/rp4layer/
ssh pi@192.168.100.150 'sudo systemctl restart getty@tty1'
```

To fall back to `xeyes` on the LCD while diagnosing a broken app:

```bash
ssh pi@192.168.100.150 "
    sed -i 's|^KIOSK_APP=.*|KIOSK_APP=\"xeyes -geometry 480x320+0+0\"|' /home/pi/kiosk.conf
    sudo systemctl restart getty@tty1
"
```

---

## Troubleshooting

| Symptom | Command |
|---------|---------|
| Black LCD after restart | `ssh pi@192.168.100.150 'cat /tmp/x_startup.log'` |
| App not appearing on LCD | `ssh pi@192.168.100.150 'cat ~/kiosk.conf'` — verify KIOSK_APP path |
| Python import errors | `ssh pi@192.168.100.150 'cd /home/pi/src/rp4layer && source venv/bin/activate && python app/main.py'` |
| No audio | `ssh pi@192.168.100.150 'aplay -l'` — card 1 (Headphones) must be listed |
| Touch not responding | `ssh pi@192.168.100.150 'ls /dev/input/event4'` — ADS7846 must be present |

For a full kiosk stack diagnostic run the `pi-kiosk-debug` skill.
