# RaspberryPi Kids' Audio Player - Technical Specification

**Document Version:** 2.0
**Date:** 2026-03-05
**Project:** RP4 Kids' MP3 Player & Alarm Clock
**UI Framework:** Kivy
**Storage:** JSON (Internal Only)
**Media Management:** SSH/SCP

---

## Table of Contents
1. [Technology Stack](#1-technology-stack)
2. [Application Structure](#2-application-structure)
3. [Data Models & JSON Schema](#3-data-models--json-schema)
4. [API Specifications](#4-api-specifications)
5. [Kivy UI Implementation](#5-kivy-ui-implementation)
6. [Audio System Implementation](#6-audio-system-implementation)
7. [Event System](#7-event-system)
8. [Configuration Management](#8-configuration-management)
9. [Media Management via SSH](#9-media-management-via-ssh)
10. [Error Handling](#10-error-handling)
11. [Performance Requirements](#11-performance-requirements)

---

## 1. Technology Stack

### 1.1 Core Dependencies

```txt
# requirements.txt
kivy==2.2.1
pygame==2.5.2
APScheduler==3.10.4
mutagen==1.47.0
python-dateutil==2.8.2
watchdog==3.0.0
```

### 1.2 System Requirements

```bash
# Debian/Raspberry Pi OS packages
python3.9+
python3-dev
python3-pip
libsdl2-dev
libsdl2-image-dev
libsdl2-mixer-dev
libsdl2-ttf-dev
libasound2-dev
alsa-utils
openssh-server
```

### 1.3 Python Version
- Minimum: Python 3.9
- Recommended: Python 3.11

---

## 2. Application Structure

### 2.1 Directory Layout

```
/home/pi/rp4player/
├── app/
│   ├── __init__.py
│   ├── main.py                      # Application entry point
│   ├── constants.py                 # Global constants
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── event_bus.py            # Event system
│   │   ├── state_manager.py        # Application state
│   │   └── config_manager.py       # Configuration loader
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── alarm.py                # Alarm data model
│   │   ├── media.py                # Media file model
│   │   └── settings.py             # Settings model
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── json_storage.py         # JSON file I/O
│   │   ├── alarm_repository.py     # Alarm CRUD
│   │   └── media_repository.py     # Media CRUD
│   │
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── audio_engine.py         # pygame audio wrapper
│   │   ├── playlist.py             # Playlist management
│   │   └── metadata.py             # MP3 metadata reader
│   │
│   ├── scheduling/
│   │   ├── __init__.py
│   │   ├── alarm_scheduler.py      # APScheduler wrapper
│   │   └── sleep_timer.py          # Sleep timer logic
│   │
│   ├── media/
│   │   ├── __init__.py
│   │   ├── media_scanner.py        # Directory scanning
│   │   └── file_watcher.py         # File system monitoring
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── app.py                  # Kivy App class
│   │   ├── screen_manager.py       # Screen navigation
│   │   │
│   │   ├── screens/
│   │   │   ├── __init__.py
│   │   │   ├── home.py             # Home screen
│   │   │   ├── alarm_list.py       # Alarm list screen
│   │   │   ├── alarm_edit.py       # Alarm editor
│   │   │   ├── story_player.py     # Story player screen
│   │   │   ├── alarm_trigger.py    # Active alarm screen
│   │   │   └── settings.py         # Settings screen
│   │   │
│   │   └── widgets/
│   │       ├── __init__.py
│   │       ├── alarm_card.py       # Alarm list item
│   │       ├── story_card.py       # Story list item
│   │       ├── time_picker.py      # Time selection widget
│   │       ├── day_selector.py     # Day of week selector
│   │       └── volume_slider.py    # Volume control
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py               # Logging setup
│       ├── time_utils.py           # Time helpers
│       └── file_utils.py           # File operations
│
├── data/
│   ├── alarms.json                 # Alarm storage
│   ├── media.json                  # Media library
│   ├── playback.json               # Playback state
│   └── backups/                    # Backup files
│
├── config/
│   └── settings.json               # Application settings
│
├── media/                          # ** SSH upload target **
│   ├── alarms/                     # Alarm sound files
│   └── stories/                    # Story MP3 files
│
├── assets/
│   ├── fonts/
│   │   └── Roboto-Regular.ttf
│   ├── icons/
│   │   ├── alarm.png
│   │   ├── story.png
│   │   └── settings.png
│   └── kv/
│       ├── home.kv                 # Kivy layout files
│       ├── alarm_list.kv
│       ├── alarm_edit.kv
│       ├── story_player.kv
│       └── widgets.kv
│
├── logs/
│   └── app.log
│
└── tests/
    ├── test_audio.py
    ├── test_alarms.py
    ├── test_storage.py
    └── test_media.py
```

### 2.2 Module Dependencies

```
main.py
  ├── ui.app.RP4PlayerApp
  │   ├── ui.screen_manager.ScreenManager
  │   │   └── ui.screens.*
  │   └── ui.widgets.*
  │
  ├── audio.audio_engine.AudioEngine
  │   └── pygame.mixer
  │
  ├── scheduling.alarm_scheduler.AlarmScheduler
  │   ├── APScheduler
  │   └── storage.alarm_repository
  │
  ├── media.media_scanner.MediaScanner
  │   ├── watchdog
  │   └── media.file_watcher
  │
  ├── core.event_bus.EventBus
  ├── core.state_manager.StateManager
  └── core.config_manager.ConfigManager
```

---

## 3. Data Models & JSON Schema

[Content same as before for Alarm and MediaFile models...]

### 3.4 Settings Model

**File:** `app/models/settings.py`

```python
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class AudioSettings:
    output_device: str = "hw:0,0"
    default_volume: float = 0.7
    alarm_volume: float = 0.8
    max_volume: float = 1.0

@dataclass
class DisplaySettings:
    brightness: int = 80
    auto_dim_timeout: int = 30
    dim_brightness: int = 20
    orientation: int = 0

@dataclass
class AlarmSettings:
    snooze_duration_minutes: int = 5
    auto_dismiss_minutes: int = 10
    max_alarms: int = 5

@dataclass
class StorySettings:
    default_sleep_timer_minutes: int = 30
    resume_playback: bool = True

@dataclass
class MediaSettings:
    auto_scan: bool = True
    scan_interval_seconds: int = 60
    media_path: str = "/home/pi/rp4player/media"

@dataclass
class SystemSettings:
    log_level: str = "INFO"
    log_file: str = "/home/pi/rp4player/logs/app.log"

@dataclass
class Settings:
    """Application settings model"""
    audio: AudioSettings
    display: DisplaySettings
    alarms: AlarmSettings
    stories: StorySettings
    media: MediaSettings
    system: SystemSettings

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "audio": asdict(self.audio),
            "display": asdict(self.display),
            "alarms": asdict(self.alarms),
            "stories": asdict(self.stories),
            "media": asdict(self.media),
            "system": asdict(self.system)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Settings':
        """Create Settings from dictionary"""
        return cls(
            audio=AudioSettings(**data.get("audio", {})),
            display=DisplaySettings(**data.get("display", {})),
            alarms=AlarmSettings(**data.get("alarms", {})),
            stories=StorySettings(**data.get("stories", {})),
            media=MediaSettings(**data.get("media", {})),
            system=SystemSettings(**data.get("system", {}))
        )
```

**JSON Schema:** `config/settings.json`

```json
{
  "audio": {
    "output_device": "hw:0,0",
    "default_volume": 0.7,
    "alarm_volume": 0.8,
    "max_volume": 1.0
  },
  "display": {
    "brightness": 80,
    "auto_dim_timeout": 30,
    "dim_brightness": 20,
    "orientation": 0
  },
  "alarms": {
    "snooze_duration_minutes": 5,
    "auto_dismiss_minutes": 10,
    "max_alarms": 5
  },
  "stories": {
    "default_sleep_timer_minutes": 30,
    "resume_playback": true
  },
  "media": {
    "auto_scan": true,
    "scan_interval_seconds": 60,
    "media_path": "/home/pi/rp4player/media"
  },
  "system": {
    "log_level": "INFO",
    "log_file": "/home/pi/rp4player/logs/app.log"
  }
}
```

---

## 4. API Specifications

[Alarm Repository and Media Repository sections remain the same...]

### 4.4 Media Scanner API

**File:** `app/media/media_scanner.py`

```python
import os
from typing import List, Optional
from datetime import datetime
from pathlib import Path
from app.models.media import MediaFile
from app.storage.media_repository import MediaRepository
from app.audio.metadata import MP3Metadata
from app.core.event_bus import EventBus, EventType

class MediaScanner:
    """Scan media directories and update library"""

    def __init__(self, media_repo: MediaRepository, event_bus: EventBus, media_path: str):
        self.media_repo = media_repo
        self.event_bus = event_bus
        self.media_path = media_path
        self.alarms_path = os.path.join(media_path, "alarms")
        self.stories_path = os.path.join(media_path, "stories")

    def scan_all(self) -> dict:
        """Scan all media directories"""
        self.event_bus.publish(EventType.MEDIA_SCAN_STARTED)

        result = {
            "files_added": 0,
            "files_removed": 0,
            "files_updated": 0,
            "errors": []
        }

        try:
            # Scan alarms
            result_alarms = self.scan_directory(self.alarms_path, "alarm")
            result["files_added"] += result_alarms["added"]
            result["files_updated"] += result_alarms["updated"]

            # Scan stories
            result_stories = self.scan_directory(self.stories_path, "story")
            result["files_added"] += result_stories["added"]
            result["files_updated"] += result_stories["updated"]

            # Clean up orphaned entries
            removed = self.media_repo.cleanup_missing()
            result["files_removed"] = removed

            self.event_bus.publish(EventType.MEDIA_SCAN_COMPLETE, result)

        except Exception as e:
            result["errors"].append(str(e))

        return result

    def scan_directory(self, directory: str, file_type: str) -> dict:
        """Scan a specific directory for MP3 files"""
        result = {"added": 0, "updated": 0}

        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            return result

        for filename in os.listdir(directory):
            if not filename.lower().endswith('.mp3'):
                continue

            file_path = os.path.join(directory, filename)

            if not os.path.isfile(file_path):
                continue

            # Check if file already exists in library
            existing = self.media_repo.get_by_path(file_path)

            if existing:
                # Update if file has been modified
                file_mtime = os.path.getmtime(file_path)
                if file_mtime > datetime.fromisoformat(existing.added_at).timestamp():
                    self._update_media_file(existing, file_path, file_type)
                    result["updated"] += 1
            else:
                # Add new file
                self._add_media_file(file_path, filename, file_type)
                result["added"] += 1

        return result

    def _add_media_file(self, file_path: str, filename: str, file_type: str) -> None:
        """Add new media file to library"""
        try:
            # Get metadata
            duration = MP3Metadata.get_duration(file_path)
            title, artist = MP3Metadata.get_tags(file_path)
            file_size = os.path.getsize(file_path)

            # Create media file object
            media = MediaFile(
                id=0,  # Will be assigned by repository
                file_path=file_path,
                file_name=filename,
                file_type=file_type,
                duration_seconds=duration,
                file_size_bytes=file_size,
                title=title,
                artist=artist,
                added_at=""  # Will be set by repository
            )

            # Add to repository
            media_id = self.media_repo.add(media)

            self.event_bus.publish(EventType.MEDIA_FILE_ADDED, {
                "id": media_id,
                "filename": filename,
                "type": file_type
            })

        except Exception as e:
            print(f"Error adding media file {filename}: {e}")

    def _update_media_file(self, media: MediaFile, file_path: str, file_type: str) -> None:
        """Update existing media file"""
        try:
            # Update metadata
            duration = MP3Metadata.get_duration(file_path)
            title, artist = MP3Metadata.get_tags(file_path)
            file_size = os.path.getsize(file_path)

            media.duration_seconds = duration
            media.file_size_bytes = file_size
            media.title = title
            media.artist = artist

            self.media_repo.update(media)

        except Exception as e:
            print(f"Error updating media file {media.file_name}: {e}")
```

### 4.5 File Watcher API

**File:** `app/media/file_watcher.py`

```python
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from app.media.media_scanner import MediaScanner
from threading import Thread

class MediaFileHandler(FileSystemEventHandler):
    """Handle file system events for media directories"""

    def __init__(self, scanner: MediaScanner):
        self.scanner = scanner
        self.debounce_time = 2  # seconds
        self.last_scan = 0

    def on_created(self, event: FileSystemEvent):
        """Handle file creation"""
        if not event.is_directory and event.src_path.endswith('.mp3'):
            self._trigger_scan()

    def on_modified(self, event: FileSystemEvent):
        """Handle file modification"""
        if not event.is_directory and event.src_path.endswith('.mp3'):
            self._trigger_scan()

    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion"""
        if not event.is_directory and event.src_path.endswith('.mp3'):
            self._trigger_scan()

    def _trigger_scan(self):
        """Trigger media scan with debouncing"""
        current_time = time.time()
        if current_time - self.last_scan > self.debounce_time:
            self.last_scan = current_time
            # Run scan in background thread
            Thread(target=self.scanner.scan_all, daemon=True).start()

class FileWatcher:
    """Watch media directories for changes"""

    def __init__(self, scanner: MediaScanner, media_path: str):
        self.scanner = scanner
        self.media_path = media_path
        self.observer = Observer()
        self.handler = MediaFileHandler(scanner)

    def start(self):
        """Start watching media directories"""
        self.observer.schedule(self.handler, self.media_path, recursive=True)
        self.observer.start()

    def stop(self):
        """Stop watching"""
        self.observer.stop()
        self.observer.join()
```

[Continue with remaining sections...Audio Engine, Alarm Scheduler, etc. remain the same]

---

## 7. Event System

### 7.1 Event Bus Implementation

[Same as before, but update Event Types:]

```python
# Event type constants
class EventType:
    # Alarm events
    ALARM_TRIGGERED = "alarm.triggered"
    ALARM_SNOOZED = "alarm.snoozed"
    ALARM_DISMISSED = "alarm.dismissed"
    ALARM_ADDED = "alarm.added"
    ALARM_UPDATED = "alarm.updated"
    ALARM_DELETED = "alarm.deleted"

    # Audio events
    AUDIO_STARTED = "audio.started"
    AUDIO_STOPPED = "audio.stopped"
    AUDIO_PAUSED = "audio.paused"
    AUDIO_RESUMED = "audio.resumed"
    AUDIO_COMPLETE = "audio.complete"

    # Media events
    MEDIA_SCAN_STARTED = "media.scan_started"
    MEDIA_SCAN_COMPLETE = "media.scan_complete"
    MEDIA_FILE_ADDED = "media.file_added"
    MEDIA_FILE_REMOVED = "media.file_removed"
    MEDIA_FILE_UPDATED = "media.file_updated"

    # System events
    SLEEP_TIMER_STARTED = "system.sleep_timer_started"
    SLEEP_TIMER_EXPIRED = "system.sleep_timer_expired"
    VOLUME_CHANGED = "system.volume_changed"
```

---

## 9. Media Management via SSH

### 9.1 SSH Server Configuration

**Enable SSH on Raspberry Pi:**

```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

**Security Configuration:**

Edit `/etc/ssh/sshd_config`:

```bash
# Recommended settings for security
PermitRootLogin no
PasswordAuthentication yes  # Or use key-based auth
PubkeyAuthentication yes
Port 22
```

### 9.2 Uploading Media Files

**From Linux/Mac:**

```bash
# Single file
scp alarm-sound.mp3 pi@rp4player.local:/home/pi/rp4player/media/alarms/

# Multiple files
scp *.mp3 pi@rp4player.local:/home/pi/rp4player/media/stories/

# Entire directory
scp -r my-stories/ pi@rp4player.local:/home/pi/rp4player/media/stories/
```

**From Windows:**

Using WinSCP or FileZilla:
- Host: rp4player.local (or IP address)
- Port: 22
- Username: pi
- Password: [your password]
- Remote path: /home/pi/rp4player/media/

**Using rsync (recommended for large collections):**

```bash
# Sync entire media library
rsync -av --progress /local/media/ pi@rp4player.local:/home/pi/rp4player/media/

# Sync only stories
rsync -av --progress /local/stories/ pi@rp4player.local:/home/pi/rp4player/media/stories/
```

### 9.3 Media File Guidelines

**Naming Conventions:**
- Use descriptive names: `three-little-pigs.mp3` not `story1.mp3`
- Avoid special characters: Use `-` or `_` instead of spaces
- Use lowercase for consistency

**File Specifications:**
- Format: MP3
- Bitrate: 128kbps or higher
- Sample rate: 44.1kHz
- Alarm sounds: 15-60 seconds
- Stories: 5-30 minutes

**ID3 Tags (Optional but recommended):**
```bash
# Add tags using eyeD3
sudo apt-get install eyed3

eyed3 --title "The Three Little Pigs" \
      --artist "Narrator Name" \
      --album "Classic Tales" \
      story.mp3
```

### 9.4 Automatic Detection

The application automatically detects new files via:

1. **File System Watcher** - Immediate detection via `watchdog`
2. **Periodic Scan** - Every 60 seconds (configurable)
3. **On Startup** - Full scan on application start

**No restart needed!** Files appear in the UI within 60 seconds.

### 9.5 Batch Upload Script

**Create helper script on your computer:**

```bash
#!/bin/bash
# upload-media.sh

PI_HOST="pi@rp4player.local"
LOCAL_DIR="$1"
REMOTE_TYPE="$2"  # "alarms" or "stories"

if [ -z "$LOCAL_DIR" ] || [ -z "$REMOTE_TYPE" ]; then
    echo "Usage: ./upload-media.sh <local-directory> <alarms|stories>"
    exit 1
fi

REMOTE_DIR="/home/pi/rp4player/media/$REMOTE_TYPE/"

echo "Uploading $LOCAL_DIR to $PI_HOST:$REMOTE_DIR"
rsync -av --progress "$LOCAL_DIR/" "$PI_HOST:$REMOTE_DIR"

echo "Upload complete! Files will appear in app within 60 seconds."
```

**Usage:**
```bash
chmod +x upload-media.sh
./upload-media.sh ~/my-stories stories
./upload-media.sh ~/alarm-sounds alarms
```

---

## 10. Error Handling

[Same as before...]

---

## 11. Performance Requirements

### 11.1 Response Times

| Operation | Target | Maximum |
|-----------|--------|---------|
| Touch response | < 100ms | < 200ms |
| Screen transition | < 300ms | < 500ms |
| Audio playback start | < 200ms | < 500ms |
| JSON file read | < 50ms | < 100ms |
| JSON file write | < 100ms | < 200ms |
| Media scan (100 files) | < 5s | < 10s |
| File detection | < 60s | < 120s |

### 11.2 Resource Usage

| Resource | Target | Maximum |
|----------|--------|---------|
| Memory (RSS) | < 300MB | < 500MB |
| CPU (idle) | < 5% | < 10% |
| CPU (playing) | < 15% | < 25% |
| Disk I/O | < 1MB/s | < 5MB/s |
| Network (SSH) | N/A | Occasional |

### 11.3 Reliability Metrics

- System uptime: > 99.9%
- Alarm accuracy: ±5 seconds
- Audio playback reliability: > 99.5%
- Data persistence: 100% (no data loss)
- Boot success rate: > 99%
- File detection rate: 100%

---

**Document End**

**Changes from v1.0:**
- Removed USB dependencies (pyudev)
- Added file system monitoring (watchdog)
- Implemented SSH-based media management
- Added Media Scanner component
- Updated event types for media scanning
- Simplified architecture (no USB hardware/software)
- Enhanced security with SSH configuration
- Added batch upload scripts and guidelines
