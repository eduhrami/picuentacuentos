# LCD Display & Kiosk Setup

**Device:** cuentacuentos — Raspberry Pi 4, 192.168.100.150 (user: pi)
**Display:** 3.5" ILI9486 TFT LCD, 480x320, 16-bit RGB565, SPI interface
**Framebuffer:** /dev/fb1 — Touchscreen: ADS7846 at /dev/input/event4

---

## Hardware

| Property | Value |
|----------|-------|
| Driver | fb_ili9486 |
| Framebuffer | /dev/fb1 (crw-rw---- root:video) |
| Resolution | 480x320 px, 16-bit (RGB565) |
| Orientation | 90° rotation via dtoverlay |
| Touch input | /dev/input/event4, /dev/input/mouse1 |

Boot config (`/boot/firmware/config.txt`):
```
dtoverlay=tft35a:rotate=90
```

---

## Permanent Kiosk Configuration

All five files below must be in place. Local copies are in `config/` mirroring
their paths on the Pi.

### 1. `/boot/firmware/cmdline.txt`
Append `consoleblank=0` to disable LCD blanking at kernel level.
```
console=serial0,115200 console=tty1 root=PARTUUID=d8eb06cf-02 rootfstype=ext4 fsck.repair=yes rootwait cfg80211.ieee80211_regdom=MX consoleblank=0
```

### 2. `/etc/X11/xorg.conf.d/99-fbdev.conf`
Directs X server to use the LCD framebuffer at 480x320, 16-bit color.
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

### 3. `/etc/systemd/system/getty@tty1.service.d/autologin.conf`
Auto-logs in user pi on tty1 at boot, which triggers .bash_profile.
```ini
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin pi --noclear %I $TERM
```

### 4. `/home/pi/.bash_profile`
Starts X on tty1. Loops so X restarts automatically after a crash.
```bash
export FRAMEBUFFER=/dev/fb1

if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    while true; do
        startx -- :0 vt1 -nolisten tcp 2>&1 | tee /tmp/x_startup.log
        sleep 3
    done
fi
```

### 5. `/home/pi/.xinitrc`
Disables screen blanking in X, then sources kiosk.conf and runs the kiosk
app in a loop. Do not change the app command here — edit kiosk.conf instead.
```bash
#!/bin/bash
xset s off
xset -dpms
xset s noblank

KIOSK_CONF="$HOME/kiosk.conf"
if [ -f "$KIOSK_CONF" ]; then
    source "$KIOSK_CONF"
else
    KIOSK_APP="xeyes -geometry 480x320+0+0"
    KIOSK_DISPLAY=":0"
fi

export DISPLAY="${KIOSK_DISPLAY}"

while true; do
    $KIOSK_APP
    sleep 1
done
```

### 6. `/home/pi/kiosk.conf`  ← edit this to change the app
```bash
KIOSK_APP="xeyes -geometry 480x320+0+0"
KIOSK_DISPLAY=":0"
```
To switch to the PiCuentaCuentos:
```bash
KIOSK_APP="python3 /home/pi/picuentacuentos/main.py"
```
Apply without rebooting:
```bash
sudo systemctl restart getty@tty1
```

---

## Boot Sequence

1. systemd autologins pi on tty1 (autologin.conf)
2. `.bash_profile` runs → launches `startx` in a restart loop
3. Xorg starts on /dev/fb1 (99-fbdev.conf)
4. `.xinitrc` runs → sources kiosk.conf → launches KIOSK_APP in a restart loop
5. App appears on LCD

---

## Verification

```bash
# X and kiosk app running
ps aux | grep -E "Xorg|startx|xeyes" | grep -v grep

# X display info
DISPLAY=:0 xdpyinfo | grep dimensions   # → 480x320

# Console blanking off
cat /sys/module/kernel/parameters/consoleblank   # → 0

# X log (check for "using /dev/fb1")
cat ~/.local/share/xorg/Xorg.0.log | grep fb1

# X startup log
cat /tmp/x_startup.log
```

---

## Known Non-Working Approaches

- **nodm display manager** — failed to start, abandoned
- **systemd service running startx as user pi** — vt permission denied
- **Writing to /sys/class/graphics/fb1/blank** — read-only, ignore it

---

## Kivy / PiCuentaCuentos Notes

When running the Python app under X, set these before importing Kivy:
```python
import os
os.environ['DISPLAY'] = ':0'
os.environ['SDL_FBDEV'] = '/dev/fb1'
os.environ['SDL_VIDEO_ALLOW_SCREENSAVER'] = '0'
```
And in Kivy config:
```python
from kivy.config import Config
Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '320')
Config.set('graphics', 'fullscreen', '0')
Config.set('kivy', 'exit_on_escape', '0')
```

---

**Last verified:** 2026-03-06 — full reboot test passed, xeyes auto-starts on LCD
