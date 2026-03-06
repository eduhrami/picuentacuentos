# Launching X Apps Remotely on the LCD

The Pi runs X server on DISPLAY=:0 mapped to /dev/fb1 (the 3.5" LCD).
Any X app launched with DISPLAY=:0 will appear on the physical screen.

---

## Basic Pattern

```bash
ssh pi@192.168.100.150 'DISPLAY=:0 <app> &'
```

---

## Common Apps

```bash
# Xeyes - follows mouse/touch
ssh pi@192.168.100.150 'DISPLAY=:0 xeyes -geometry 480x320+0+0 &'

# Xclock - analog clock
ssh pi@192.168.100.150 'DISPLAY=:0 xclock -geometry 480x320+0+0 &'

# Xclock - digital clock
ssh pi@192.168.100.150 'DISPLAY=:0 xclock -digital -geometry 480x20+0+0 &'

# Xterm - terminal on the LCD
ssh pi@192.168.100.150 'DISPLAY=:0 xterm -geometry 80x24+0+0 &'

# Solid color background (useful to confirm X is alive)
ssh pi@192.168.100.150 'DISPLAY=:0 xsetroot -solid blue'
ssh pi@192.168.100.150 'DISPLAY=:0 xsetroot -solid black'
ssh pi@192.168.100.150 'DISPLAY=:0 xsetroot -solid white'

# Touchscreen calibration
ssh pi@192.168.100.150 'DISPLAY=:0 xinput_calibrator > /tmp/calib.log 2>&1 &'
```

---

## Kill Apps

```bash
# Kill a specific app
ssh pi@192.168.100.150 'pkill xeyes'
ssh pi@192.168.100.150 'pkill xclock'
ssh pi@192.168.100.150 'pkill xterm'

# Kill all X client apps (leaves X server running)
ssh pi@192.168.100.150 'DISPLAY=:0 xkill -all 2>/dev/null; pkill xeyes xclock xterm'

# Restart the full kiosk session (kills X, autologin restarts it)
ssh pi@192.168.100.150 'sudo systemctl restart getty@tty1'
```

---

## Switch Kiosk App Without Rebooting

```bash
# Edit kiosk.conf remotely
ssh pi@192.168.100.150 'nano ~/kiosk.conf'

# Or set it inline (example: switch to xclock)
ssh pi@192.168.100.150 "sed -i 's|^KIOSK_APP=.*|KIOSK_APP=\"xclock -geometry 480x320+0+0\"|' ~/kiosk.conf"

# Then restart the session to apply
ssh pi@192.168.100.150 'sudo systemctl restart getty@tty1'
```

---

## Check What's on Screen

```bash
# List all X clients currently connected to :0
ssh pi@192.168.100.150 'DISPLAY=:0 xlsclients'

# Show root window info (size, position)
ssh pi@192.168.100.150 'DISPLAY=:0 xwininfo -root'

# List X input devices (touchscreen etc.)
ssh pi@192.168.100.150 'DISPLAY=:0 xinput list'
```

---

## X Server Management

```bash
# Check X is running
ssh pi@192.168.100.150 'ps aux | grep Xorg | grep -v grep'

# Check X startup log
ssh pi@192.168.100.150 'cat /tmp/x_startup.log'

# Check Xorg detail log
ssh pi@192.168.100.150 'cat ~/.local/share/xorg/Xorg.0.log | grep -E "EE|fb1"'
```
