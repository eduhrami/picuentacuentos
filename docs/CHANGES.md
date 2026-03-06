# RP4 Kids Audio Player - Version 2.0 Changes

**Date:** 2026-03-05
**Change Type:** Architecture Update
**From:** USB-based media updates → **To:** SSH-based media management

---

## Summary

The system has been redesigned to use **SSH/SCP for media file uploads** instead of USB drives. All media is stored internally on the Raspberry Pi's microSD card, and administrators upload files remotely via SSH.

---

## Key Changes

### 1. **Removed Components**

❌ **USB Hardware Support**
- No longer need USB ports for media updates
- Removed USB mounting/unmounting logic

❌ **USB Detection Software**
- Removed: `pyudev` dependency
- Removed: `usb_manager.py` module
- Removed: `file_sync.py` module
- Removed: USB-related event types

❌ **User-facing USB UI**
- No USB sync progress screens
- No "Insert USB" notifications
- No "USB sync complete" messages

### 2. **Added Components**

✅ **SSH Server**
- OpenSSH server (pre-installed on Pi OS)
- Secure remote access for administrators
- Port 22 (standard SSH)

✅ **File System Monitoring**
- Added: `watchdog` Python library
- Monitors `/home/pi/rp4player/media/` for changes
- Automatic detection of new/modified/deleted files

✅ **Media Scanner**
- New: `media_scanner.py` module
- New: `file_watcher.py` module
- Scans media directories periodically (60s interval)
- Updates media library JSON automatically

✅ **Event Types**
- `MEDIA_SCAN_STARTED`
- `MEDIA_SCAN_COMPLETE`
- `MEDIA_FILE_ADDED`
- `MEDIA_FILE_REMOVED`
- `MEDIA_FILE_UPDATED`

### 3. **Updated Settings**

**Old (USB-based):**
```json
{
  "usb": {
    "auto_sync": true,
    "media_path": "/home/pi/rp4player/media"
  }
}
```

**New (SSH-based):**
```json
{
  "media": {
    "auto_scan": true,
    "scan_interval_seconds": 60,
    "media_path": "/home/pi/rp4player/media"
  }
}
```

### 4. **Architecture Changes**

**Before:**
```
User → Insert USB → Auto-detect → Copy files → Update library → Remove USB
```

**After:**
```
Admin → SCP/SFTP upload → File watcher detects → Scan directory → Update library
```

---

## Benefits of SSH-based Approach

### ✅ Advantages

1. **Simpler Hardware**
   - No USB ports needed
   - Fewer physical interactions
   - No USB drive management

2. **Remote Management**
   - Upload from any computer on network
   - No physical access required
   - Batch uploads easier

3. **Safer for Kids**
   - Children cannot accidentally remove USB during sync
   - No USB drives for kids to lose/damage
   - Administrator-controlled updates only

4. **More Reliable**
   - No USB mounting issues
   - No filesystem corruption from improper ejection
   - Network-based = more stable

5. **Better for Automation**
   - Can script uploads easily
   - rsync for incremental syncs
   - Can schedule automated backups

### ⚠️ Requirements

1. **Network Connection Required**
   - WiFi or Ethernet must be configured
   - Need IP address or hostname (rp4player.local)
   - Port 22 must be accessible

2. **Administrator Knowledge**
   - Must know how to use SCP/SFTP
   - Basic command line or GUI client knowledge
   - Need to manage SSH credentials

3. **Security Considerations**
   - SSH password/key management
   - Firewall configuration
   - Network security

---

## Migration Guide

### If You Have Existing System (v1.0 USB-based)

1. **Backup current media:**
   ```bash
   rsync -av pi@rp4player.local:/home/pi/rp4player/media/ ./backup-media/
   ```

2. **Update Python dependencies:**
   ```bash
   cd /home/pi/rp4player
   source venv/bin/activate
   pip uninstall pyudev
   pip install watchdog==3.0.0
   ```

3. **Update application code:**
   - Replace `usb_manager.py` with `media_scanner.py`
   - Replace `file_sync.py` with `file_watcher.py`
   - Update `settings.json` to use "media" instead of "usb"
   - Update event subscriptions

4. **Enable SSH (if not already):**
   ```bash
   sudo systemctl enable ssh
   sudo systemctl start ssh
   ```

5. **Test media upload:**
   ```bash
   scp test.mp3 pi@rp4player.local:/home/pi/rp4player/media/stories/
   ```

### For New Installation

Simply follow the updated `INSTALL_v2.md` guide. The `setup_v2.sh` script handles everything automatically.

---

## Uploading Media Files

### Method 1: Command Line (Linux/Mac)

```bash
# Upload single file
scp story.mp3 pi@rp4player.local:/home/pi/rp4player/media/stories/

# Upload multiple files
scp *.mp3 pi@rp4player.local:/home/pi/rp4player/media/alarms/

# Upload directory
rsync -av ./my-stories/ pi@rp4player.local:/home/pi/rp4player/media/stories/
```

### Method 2: GUI Client (Windows/Mac/Linux)

**WinSCP (Windows):**
1. Download from https://winscp.net/
2. New Session:
   - Host: rp4player.local
   - Port: 22
   - Username: pi
   - Password: [your password]
3. Connect and drag/drop files

**FileZilla (All platforms):**
1. Download from https://filezilla-project.org/
2. Site Manager → New Site:
   - Protocol: SFTP
   - Host: rp4player.local
   - Port: 22
   - User: pi
3. Connect and transfer files

**Cyberduck (Mac):**
1. Download from https://cyberduck.io/
2. Open Connection:
   - SFTP (SSH File Transfer Protocol)
   - Server: rp4player.local
   - Username: pi
3. Drag and drop files

### Method 3: Automated Script

Save as `upload-media.sh`:

```bash
#!/bin/bash
rsync -av --progress "$1/" pi@rp4player.local:/home/pi/rp4player/media/$2/
echo "Upload complete! Files will appear within 60 seconds."
```

Usage:
```bash
chmod +x upload-media.sh
./upload-media.sh ~/Desktop/new-stories stories
./upload-media.sh ~/Desktop/alarm-sounds alarms
```

---

## Technical Details

### File Detection Flow

```
1. Admin uploads file via SCP/SFTP
   ↓
2. File lands in /home/pi/rp4player/media/[alarms|stories]/
   ↓
3. Watchdog detects filesystem event (within 1-2 seconds)
   ↓
4. MediaScanner triggers scan (with 2s debounce)
   ↓
5. Scan reads MP3 metadata
   ↓
6. Updates media.json library
   ↓
7. Publishes MEDIA_FILE_ADDED event
   ↓
8. UI refreshes story/alarm lists
   ↓
9. File appears in app (total time: < 60 seconds)
```

### Fallback Mechanisms

1. **Watchdog fails** → Periodic scan every 60 seconds
2. **Scan fails** → Retry on next interval
3. **Invalid MP3** → Skip file, log error
4. **Duplicate file** → Update existing entry

### Security

**SSH Configuration:**
- Use strong passwords or SSH keys
- Consider disabling password auth (key-only)
- Use firewall to restrict SSH access
- Change default SSH port if on public network

**File Permissions:**
```bash
# Recommended permissions
chmod 755 /home/pi/rp4player/media
chmod 755 /home/pi/rp4player/media/alarms
chmod 755 /home/pi/rp4player/media/stories
chmod 644 /home/pi/rp4player/media/*/*.mp3
```

---

## Updated File Structure

```
rp4layer/
├── ARCHITECTURE.md              # ✏️ Updated
├── TECHNICAL_SPECIFICATION.md   # 🆕 v2.0
├── requirements.txt             # ✏️ Updated (removed pyudev, added watchdog)
├── setup.sh                     # ✏️ Updated (SSH setup)
├── INSTALL.md                   # ✏️ Updated (SSH instructions)
├── README.md                    # ✏️ Updated (features list)
├── CHANGES_v2.md                # 🆕 This document
│
├── app/
│   ├── usb/                     # ❌ Removed
│   ├── media/                   # 🆕 Added
│   │   ├── media_scanner.py    # 🆕 New
│   │   └── file_watcher.py     # 🆕 New
```

---

## FAQ

### Q: Do I need internet for the player to work?

**A:** No! Once media is uploaded, the player works completely offline. Network is only needed for uploading new media files.

### Q: Can kids still use it normally?

**A:** Yes! Children interact with the device exactly the same way. They don't see any difference. Only the admin method for adding media has changed.

### Q: What if my network goes down?

**A:** The player continues working normally with existing media. You just can't upload new files until network is restored.

### Q: Can I still use USB drives?

**A:** No, USB support has been completely removed. However, you can:
1. Copy from USB to your computer
2. Then SCP from computer to Pi

### Q: Is it secure?

**A:** Yes, if configured properly:
- Use strong SSH passwords or key-based auth
- Keep SSH within private network
- Don't expose port 22 to internet without VPN

### Q: How do I find the Pi's IP address?

```bash
# On the Pi:
hostname -I

# From another computer:
ping rp4player.local
# Or check your router's DHCP list
```

### Q: Can I upload while kids are using it?

**A:** Yes! File uploads don't interrupt playback. New files appear in the library within 60 seconds without any disruption.

---

## Rollback Plan

If you need to revert to USB-based approach:

1. Reinstall old code (v1.0)
2. `pip install pyudev==0.24.0`
3. `pip uninstall watchdog`
4. Restore old `settings.json` with "usb" section
5. Reboot

---

## Support

For issues or questions about the SSH-based approach:

1. Check SSH is enabled: `sudo systemctl status ssh`
2. Test SSH connection: `ssh pi@rp4player.local`
3. Check logs: `tail -f /home/pi/rp4player/logs/app.log`
4. Verify watchdog is running: `ps aux | grep python`

---

**End of Changes Document**

For full implementation details, see:
- `TECHNICAL_SPECIFICATION_v2.md` - Complete technical specification
- `INSTALL_v2.md` - Installation guide with SSH setup
- `README_v2.md` - Updated project overview
