# Media Management Guide - SSH Edition

Quick reference for uploading and managing media files on your RP4 Kids Audio Player.

---

## Quick Start

### Find Your Pi's Address

```bash
# Method 1: Use hostname
ping picuentacuentos.local

# Method 2: Check on the Pi itself
# (Connect keyboard/monitor temporarily)
hostname -I
```

### Upload Your First File

```bash
# From your computer's terminal
scp my-story.mp3 pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/
```

**That's it!** The file will appear in the app within 60 seconds.

---

## Directory Structure

```
/home/pi/picuentacuentos/media/
├── alarms/          ← Upload alarm sounds here (15-60 seconds)
└── stories/         ← Upload bedtime stories here (5-30 minutes)
```

---

## Upload Methods

### 📟 Command Line

#### Linux / Mac

```bash
# Single file
scp story.mp3 pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/

# Multiple files from current directory
scp *.mp3 pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/

# Entire folder (preserves structure)
scp -r my-stories/ pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/

# Sync with rsync (recommended for large libraries)
rsync -av --progress ~/Music/Stories/ pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/
```

#### Windows (PowerShell)

```powershell
# Install OpenSSH client (Windows 10+)
# Already included in modern Windows

# Upload file
scp story.mp3 pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/

# Or use PSCP (PuTTY)
pscp story.mp3 pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/
```

### 🖱️ GUI Clients

#### Windows: WinSCP

1. **Download:** https://winscp.net/
2. **Configure:**
   - File protocol: SFTP
   - Host name: `picuentacuentos.local`
   - Port: 22
   - User name: `pi`
   - Password: [your pi password]
3. **Connect** and drag-drop files

#### Mac: Cyberduck

1. **Download:** https://cyberduck.io/
2. **Open Connection:**
   - Protocol: SFTP
   - Server: `picuentacuentos.local`
   - Port: 22
   - Username: `pi`
   - Password: [your pi password]
3. Drag and drop files

#### All Platforms: FileZilla

1. **Download:** https://filezilla-project.org/
2. **Quick Connect:**
   - Host: `sftp://picuentacuentos.local`
   - Username: `pi`
   - Password: [your pi password]
   - Port: 22
3. Transfer files

### 🤖 Automation Script

Create `~/bin/upload-stories.sh`:

```bash
#!/bin/bash
# Quick media upload script

PI_HOST="pi@picuentacuentos.local"

# Usage: ./upload-stories.sh <directory-path> <type>
# Example: ./upload-stories.sh ~/Downloads/new-stories stories

if [ $# -ne 2 ]; then
    echo "Usage: $0 <local-path> <alarms|stories>"
    exit 1
fi

LOCAL_PATH="$1"
MEDIA_TYPE="$2"

if [[ "$MEDIA_TYPE" != "alarms" && "$MEDIA_TYPE" != "stories" ]]; then
    echo "Error: Media type must be 'alarms' or 'stories'"
    exit 1
fi

REMOTE_PATH="/home/pi/picuentacuentos/media/$MEDIA_TYPE/"

echo "📤 Uploading $LOCAL_PATH to $PI_HOST:$REMOTE_PATH"
rsync -av --progress "$LOCAL_PATH/" "$PI_HOST:$REMOTE_PATH"

echo "✅ Upload complete! Files will appear in app within 60 seconds."
```

Make it executable:
```bash
chmod +x ~/bin/upload-stories.sh
```

Use it:
```bash
upload-stories.sh ~/Desktop/new-stories stories
upload-stories.sh ~/Desktop/alarm-sounds alarms
```

---

## File Guidelines

### Supported Format

- **Only MP3 files** are supported
- Other formats (WAV, OGG, M4A) will be ignored

### Recommended Specifications

| Type | Duration | Bitrate | Sample Rate |
|------|----------|---------|-------------|
| **Alarm Sounds** | 15-60 seconds | 128kbps | 44.1kHz |
| **Stories** | 5-30 minutes | 128kbps | 44.1kHz |

### Naming Conventions

✅ **Good names:**
- `three-little-pigs.mp3`
- `morning_rooster.mp3`
- `goldilocks-and-bears.mp3`

❌ **Avoid:**
- `story 1.mp3` (spaces)
- `3Little.Pigs!.mp3` (special characters)
- `New Recording 02.mp3` (unclear)

### ID3 Tags (Optional but Recommended)

Add metadata for better display names:

```bash
# Install eyeD3 (on your computer or the Pi)
sudo apt-get install eyed3  # Linux/Pi
brew install eye-d3          # Mac

# Add tags
eyeD3 --title "The Three Little Pigs" \
      --artist "Jane Smith" \
      --album "Classic Bedtime Stories" \
      three-little-pigs.mp3
```

The app will display:
- **Title** as the story name (if available)
- **File name** as fallback (formatted nicely)
- **Artist** in the details view

---

## Common Tasks

### Upload New Story

```bash
scp "Jack and the Beanstalk.mp3" pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/
```

### Upload New Alarm Sound

```bash
scp rooster-crowing.mp3 pi@picuentacuentos.local:/home/pi/picuentacuentos/media/alarms/
```

### Batch Upload Multiple Stories

```bash
cd ~/Downloads/stories
scp *.mp3 pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/
```

### Replace Existing File

```bash
# Just upload with same name - it will auto-update
scp three-little-pigs-new-version.mp3 pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/three-little-pigs.mp3
```

### Delete File

```bash
# SSH into Pi and delete
ssh pi@picuentacuentos.local
rm /home/pi/picuentacuentos/media/stories/old-story.mp3
exit
# App will detect deletion within 60 seconds
```

### List Current Files

```bash
# List all stories
ssh pi@picuentacuentos.local "ls -lh /home/pi/picuentacuentos/media/stories/"

# List all alarms
ssh pi@picuentacuentos.local "ls -lh /home/pi/picuentacuentos/media/alarms/"

# Count files
ssh pi@picuentacuentos.local "ls /home/pi/picuentacuentos/media/stories/ | wc -l"
```

### Backup Media Library

```bash
# Download all media to your computer
rsync -av pi@picuentacuentos.local:/home/pi/picuentacuentos/media/ ~/picuentacuentos-backup/

# Backup just stories
rsync -av pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/ ~/picuentacuentos-backup/stories/
```

### Restore Media Library

```bash
# Upload your backup
rsync -av ~/picuentacuentos-backup/ pi@picuentacuentos.local:/home/pi/picuentacuentos/media/
```

### Sync Folders (Keep Updated)

```bash
# Keep local and remote in sync
rsync -av --delete ~/Music/Kids-Stories/ pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/
```

The `--delete` flag removes files from Pi that don't exist locally.

---

## Troubleshooting

### Can't Connect via SSH

```bash
# Check if Pi is online
ping picuentacuentos.local

# Check if SSH is running on Pi
ssh pi@picuentacuentos.local "systemctl status ssh"

# Try IP address instead of hostname
ssh pi@192.168.1.100
```

### "Permission Denied" Error

```bash
# Check directory permissions on Pi
ssh pi@picuentacuentos.local "ls -la /home/pi/picuentacuentos/media/"

# Fix if needed
ssh pi@picuentacuentos.local "chmod 755 /home/pi/picuentacuentos/media/{alarms,stories}"
```

### Files Not Appearing in App

1. **Wait 60 seconds** - Automatic scan runs every minute
2. **Check file format** - Must be .mp3
3. **Check file location** - Must be in correct folder
4. **Verify upload** - SSH in and check:
   ```bash
   ssh pi@picuentacuentos.local "ls -lh /home/pi/picuentacuentos/media/stories/"
   ```
5. **Check logs**:
   ```bash
   ssh pi@picuentacuentos.local "tail -50 /home/pi/picuentacuentos/logs/app.log"
   ```
6. **Manual scan** - Restart app:
   ```bash
   ssh pi@picuentacuentos.local "sudo systemctl restart getty@tty1"
   ```

### Hostname Not Resolving

If `picuentacuentos.local` doesn't work:

1. Find IP address:
   ```bash
   # Check router DHCP list, or:
   nmap -sn 192.168.1.0/24 | grep -i raspberry
   ```

2. Use IP address directly:
   ```bash
   scp story.mp3 pi@192.168.1.100:/home/pi/picuentacuentos/media/stories/
   ```

3. Add to `/etc/hosts` (optional):
   ```bash
   # Add line:
   192.168.1.100  picuentacuentos.local
   ```

---

## Advanced Tips

### Set Up SSH Key (No Password)

```bash
# On your computer
ssh-keygen -t ed25519 -C "picuentacuentos-access"

# Copy key to Pi
ssh-copy-id pi@picuentacuentos.local

# Test
ssh pi@picuentacuentos.local  # Should login without password
```

### Create Alias for Quick Access

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Quick aliases
alias rp4-ssh="ssh pi@picuentacuentos.local"
alias rp4-stories="rsync -av --progress"
alias rp4-backup="rsync -av pi@picuentacuentos.local:/home/pi/picuentacuentos/media/ ~/rp4-backup/"

# Functions
upload-story() {
    scp "$1" pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/
}

upload-alarm() {
    scp "$1" pi@picuentacuentos.local:/home/pi/picuentacuentos/media/alarms/
}
```

Usage after adding aliases:
```bash
upload-story ~/Downloads/new-story.mp3
upload-alarm ~/Downloads/rooster.mp3
rp4-backup
```

### Automated Nightly Sync

Create cron job on your computer:

```bash
crontab -e

# Add line (syncs at 2 AM daily):
0 2 * * * rsync -av ~/Music/Kids-Stories/ pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/ >> ~/rp4-sync.log 2>&1
```

---

## Security Best Practices

1. **Use strong password** for pi user
2. **Change default SSH port** (optional):
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Change: Port 22 → Port 2222
   sudo systemctl restart ssh
   ```

3. **Disable password auth** (after setting up SSH key):
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Set: PasswordAuthentication no
   sudo systemctl restart ssh
   ```

4. **Firewall rules** (if needed):
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```

5. **Local network only** - Don't expose SSH to internet

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│         PiCuentaCuentos - Media Upload Cheat Sheet    │
├─────────────────────────────────────────────────┤
│ Upload Story:                                    │
│ scp story.mp3 pi@picuentacuentos.local:/home/pi/\    │
│     picuentacuentos/media/stories/                     │
│                                                  │
│ Upload Alarm:                                    │
│ scp alarm.mp3 pi@picuentacuentos.local:/home/pi/\    │
│     picuentacuentos/media/alarms/                      │
│                                                  │
│ Batch Upload:                                    │
│ scp *.mp3 pi@picuentacuentos.local:/home/pi/\        │
│     picuentacuentos/media/stories/                     │
│                                                  │
│ Sync Directory:                                  │
│ rsync -av ~/stories/ pi@picuentacuentos.local:\       │
│     /home/pi/picuentacuentos/media/stories/            │
│                                                  │
│ Backup:                                          │
│ rsync -av pi@picuentacuentos.local:/home/pi/\        │
│     picuentacuentos/media/ ~/backup/                   │
│                                                  │
│ Files appear in app: < 60 seconds               │
└─────────────────────────────────────────────────┘
```

---

**Need Help?**
- Check logs: `ssh pi@picuentacuentos.local "tail -f /home/pi/picuentacuentos/logs/app.log"`
- Restart kiosk: `ssh pi@picuentacuentos.local "sudo systemctl restart getty@tty1"`
- Full documentation: See `INSTALL.md` and `TECHNICAL_SPECIFICATION.md`
