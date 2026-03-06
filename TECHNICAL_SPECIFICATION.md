# RaspberryPi Kids' Audio Player - Technical Specification

**Document Version:** 1.0
**Date:** 2026-03-05
**Project:** RP4 Kids' MP3 Player & Alarm Clock
**UI Framework:** Kivy
**Storage:** JSON

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
9. [Error Handling](#9-error-handling)
10. [Performance Requirements](#10-performance-requirements)

---

## 1. Technology Stack

### 1.1 Core Dependencies

```txt
# requirements.txt
kivy==2.1.0
pygame==2.5.0
APScheduler==3.10.1
pyudev==0.24.0
mutagen==1.46.0
python-dateutil==2.8.2
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
│   ├── usb/
│   │   ├── __init__.py
│   │   ├── usb_monitor.py          # USB device detection
│   │   └── file_sync.py            # Media synchronization
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
├── media/
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
    └── test_usb.py
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
  ├── usb.usb_monitor.USBMonitor
  │   ├── pyudev
  │   └── usb.file_sync
  │
  ├── core.event_bus.EventBus
  ├── core.state_manager.StateManager
  └── core.config_manager.ConfigManager
```

---

## 3. Data Models & JSON Schema

### 3.1 Alarm Model

**File:** `app/models/alarm.py`

```python
from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import time
import json

@dataclass
class Alarm:
    """Alarm data model"""
    id: int
    enabled: bool
    hour: int  # 0-23
    minute: int  # 0-59
    days: List[str]  # ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    sound_file: str
    volume: float  # 0.0 to 1.0
    label: str
    snooze_enabled: bool
    auto_dismiss_minutes: int
    created_at: str  # ISO 8601 format
    updated_at: str  # ISO 8601 format

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Alarm':
        """Create Alarm from dictionary"""
        return cls(**data)

    def get_time_str(self) -> str:
        """Get formatted time string (e.g., '07:30 AM')"""
        hour_12 = self.hour % 12 or 12
        am_pm = 'AM' if self.hour < 12 else 'PM'
        return f"{hour_12:02d}:{self.minute:02d} {am_pm}"

    def get_days_str(self) -> str:
        """Get formatted days string"""
        if len(self.days) == 7:
            return "Every Day"
        elif set(self.days) == {"mon", "tue", "wed", "thu", "fri"}:
            return "Weekdays"
        elif set(self.days) == {"sat", "sun"}:
            return "Weekends"
        else:
            day_names = {
                "mon": "Mon", "tue": "Tue", "wed": "Wed",
                "thu": "Thu", "fri": "Fri", "sat": "Sat", "sun": "Sun"
            }
            return ", ".join(day_names[d] for d in self.days)

    def is_active_today(self) -> bool:
        """Check if alarm is active today"""
        from datetime import datetime
        today = datetime.now().strftime("%a").lower()
        day_map = {
            "mon": "mon", "tue": "tue", "wed": "wed",
            "thu": "thu", "fri": "fri", "sat": "sat", "sun": "sun"
        }
        return day_map.get(today) in self.days
```

**JSON Schema:** `data/alarms.json`

```json
{
  "alarms": [
    {
      "id": 1,
      "enabled": true,
      "hour": 7,
      "minute": 30,
      "days": ["mon", "tue", "wed", "thu", "fri"],
      "sound_file": "rooster.mp3",
      "volume": 0.8,
      "label": "School Wake Up",
      "snooze_enabled": true,
      "auto_dismiss_minutes": 10,
      "created_at": "2026-03-05T08:00:00",
      "updated_at": "2026-03-05T08:00:00"
    },
    {
      "id": 2,
      "enabled": true,
      "hour": 21,
      "minute": 0,
      "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
      "sound_file": "gentle-bells.mp3",
      "volume": 0.6,
      "label": "Bedtime",
      "snooze_enabled": false,
      "auto_dismiss_minutes": 5,
      "created_at": "2026-03-05T08:00:00",
      "updated_at": "2026-03-05T08:00:00"
    }
  ],
  "next_id": 3
}
```

### 3.2 Media File Model

**File:** `app/models/media.py`

```python
from dataclasses import dataclass, asdict
from typing import Optional
import os

@dataclass
class MediaFile:
    """Media file data model"""
    id: int
    file_path: str
    file_name: str
    file_type: str  # 'alarm' or 'story'
    duration_seconds: float
    file_size_bytes: int
    title: Optional[str]  # From MP3 metadata
    artist: Optional[str]  # From MP3 metadata
    added_at: str  # ISO 8601 format

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'MediaFile':
        """Create MediaFile from dictionary"""
        return cls(**data)

    def get_display_name(self) -> str:
        """Get display name (title or filename)"""
        if self.title:
            return self.title
        # Remove extension and format filename
        name = os.path.splitext(self.file_name)[0]
        return name.replace('_', ' ').replace('-', ' ').title()

    def get_duration_str(self) -> str:
        """Get formatted duration (e.g., '3:45')"""
        minutes = int(self.duration_seconds // 60)
        seconds = int(self.duration_seconds % 60)
        return f"{minutes}:{seconds:02d}"

    def exists(self) -> bool:
        """Check if file exists on disk"""
        return os.path.exists(self.file_path)
```

**JSON Schema:** `data/media.json`

```json
{
  "media_files": [
    {
      "id": 1,
      "file_path": "/home/pi/rp4player/media/alarms/rooster.mp3",
      "file_name": "rooster.mp3",
      "file_type": "alarm",
      "duration_seconds": 15.5,
      "file_size_bytes": 248320,
      "title": "Rooster Crow",
      "artist": null,
      "added_at": "2026-03-05T08:00:00"
    },
    {
      "id": 2,
      "file_path": "/home/pi/rp4player/media/stories/three-little-pigs.mp3",
      "file_name": "three-little-pigs.mp3",
      "file_type": "story",
      "duration_seconds": 525.0,
      "file_size_bytes": 8405120,
      "title": "The Three Little Pigs",
      "artist": "Narrator",
      "added_at": "2026-03-05T08:00:00"
    }
  ],
  "next_id": 3
}
```

### 3.3 Playback State Model

**JSON Schema:** `data/playback.json`

```json
{
  "current_media_id": 2,
  "position_seconds": 125.5,
  "volume": 0.7,
  "is_playing": false,
  "sleep_timer_enabled": true,
  "sleep_timer_end_time": "2026-03-05T21:30:00",
  "playlist": [2, 5, 7],
  "playlist_index": 0,
  "last_updated": "2026-03-05T21:00:00"
}
```

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
class USBSettings:
    auto_sync: bool = True
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
    usb: USBSettings
    system: SystemSettings

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "audio": asdict(self.audio),
            "display": asdict(self.display),
            "alarms": asdict(self.alarms),
            "stories": asdict(self.stories),
            "usb": asdict(self.usb),
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
            usb=USBSettings(**data.get("usb", {})),
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
  "usb": {
    "auto_sync": true,
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

### 4.1 JSON Storage Manager

**File:** `app/storage/json_storage.py`

```python
import json
import os
from typing import Any, Dict
from threading import Lock
import shutil
from datetime import datetime

class JSONStorage:
    """Thread-safe JSON file storage manager"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.lock = Lock()
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create file with empty structure if it doesn't exist"""
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            self.write({})

    def read(self) -> Dict[str, Any]:
        """Read and parse JSON file"""
        with self.lock:
            try:
                with open(self.file_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # Return empty dict if file is corrupted
                return {}
            except FileNotFoundError:
                return {}

    def write(self, data: Dict[str, Any]) -> None:
        """Write data to JSON file with atomic operation"""
        with self.lock:
            # Write to temporary file first
            temp_path = f"{self.file_path}.tmp"
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)

            # Atomic replace
            shutil.move(temp_path, self.file_path)

    def backup(self) -> str:
        """Create backup of JSON file"""
        with self.lock:
            if os.path.exists(self.file_path):
                backup_dir = os.path.join(
                    os.path.dirname(self.file_path),
                    'backups'
                )
                os.makedirs(backup_dir, exist_ok=True)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{os.path.basename(self.file_path)}.{timestamp}.bak"
                backup_path = os.path.join(backup_dir, backup_name)

                shutil.copy2(self.file_path, backup_path)
                return backup_path
        return ""

    def restore(self, backup_path: str) -> bool:
        """Restore from backup file"""
        with self.lock:
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, self.file_path)
                return True
        return False
```

### 4.2 Alarm Repository

**File:** `app/storage/alarm_repository.py`

```python
from typing import List, Optional
from datetime import datetime
from app.models.alarm import Alarm
from app.storage.json_storage import JSONStorage

class AlarmRepository:
    """Repository for alarm data operations"""

    def __init__(self, storage_path: str):
        self.storage = JSONStorage(storage_path)

    def get_all(self) -> List[Alarm]:
        """Get all alarms"""
        data = self.storage.read()
        alarms_data = data.get('alarms', [])
        return [Alarm.from_dict(a) for a in alarms_data]

    def get_by_id(self, alarm_id: int) -> Optional[Alarm]:
        """Get alarm by ID"""
        alarms = self.get_all()
        for alarm in alarms:
            if alarm.id == alarm_id:
                return alarm
        return None

    def get_enabled(self) -> List[Alarm]:
        """Get all enabled alarms"""
        return [a for a in self.get_all() if a.enabled]

    def add(self, alarm: Alarm) -> int:
        """Add new alarm, returns alarm ID"""
        data = self.storage.read()

        # Generate new ID
        next_id = data.get('next_id', 1)
        alarm.id = next_id
        alarm.created_at = datetime.now().isoformat()
        alarm.updated_at = datetime.now().isoformat()

        # Add to list
        alarms = data.get('alarms', [])
        alarms.append(alarm.to_dict())

        # Save
        data['alarms'] = alarms
        data['next_id'] = next_id + 1
        self.storage.write(data)

        return alarm.id

    def update(self, alarm: Alarm) -> bool:
        """Update existing alarm"""
        data = self.storage.read()
        alarms = data.get('alarms', [])

        for i, a in enumerate(alarms):
            if a['id'] == alarm.id:
                alarm.updated_at = datetime.now().isoformat()
                alarms[i] = alarm.to_dict()
                data['alarms'] = alarms
                self.storage.write(data)
                return True

        return False

    def delete(self, alarm_id: int) -> bool:
        """Delete alarm by ID"""
        data = self.storage.read()
        alarms = data.get('alarms', [])

        filtered = [a for a in alarms if a['id'] != alarm_id]
        if len(filtered) < len(alarms):
            data['alarms'] = filtered
            self.storage.write(data)
            return True

        return False

    def enable(self, alarm_id: int) -> bool:
        """Enable alarm"""
        alarm = self.get_by_id(alarm_id)
        if alarm:
            alarm.enabled = True
            return self.update(alarm)
        return False

    def disable(self, alarm_id: int) -> bool:
        """Disable alarm"""
        alarm = self.get_by_id(alarm_id)
        if alarm:
            alarm.enabled = False
            return self.update(alarm)
        return False

    def backup(self) -> str:
        """Create backup of alarms"""
        return self.storage.backup()
```

### 4.3 Media Repository

**File:** `app/storage/media_repository.py`

```python
from typing import List, Optional
from datetime import datetime
from app.models.media import MediaFile
from app.storage.json_storage import JSONStorage

class MediaRepository:
    """Repository for media file data operations"""

    def __init__(self, storage_path: str):
        self.storage = JSONStorage(storage_path)

    def get_all(self) -> List[MediaFile]:
        """Get all media files"""
        data = self.storage.read()
        media_data = data.get('media_files', [])
        return [MediaFile.from_dict(m) for m in media_data]

    def get_by_id(self, media_id: int) -> Optional[MediaFile]:
        """Get media file by ID"""
        media_files = self.get_all()
        for media in media_files:
            if media.id == media_id:
                return media
        return None

    def get_by_type(self, file_type: str) -> List[MediaFile]:
        """Get media files by type ('alarm' or 'story')"""
        return [m for m in self.get_all() if m.file_type == file_type]

    def get_by_path(self, file_path: str) -> Optional[MediaFile]:
        """Get media file by path"""
        media_files = self.get_all()
        for media in media_files:
            if media.file_path == file_path:
                return media
        return None

    def add(self, media: MediaFile) -> int:
        """Add new media file, returns media ID"""
        data = self.storage.read()

        # Generate new ID
        next_id = data.get('next_id', 1)
        media.id = next_id
        media.added_at = datetime.now().isoformat()

        # Add to list
        media_files = data.get('media_files', [])
        media_files.append(media.to_dict())

        # Save
        data['media_files'] = media_files
        data['next_id'] = next_id + 1
        self.storage.write(data)

        return media.id

    def update(self, media: MediaFile) -> bool:
        """Update existing media file"""
        data = self.storage.read()
        media_files = data.get('media_files', [])

        for i, m in enumerate(media_files):
            if m['id'] == media.id:
                media_files[i] = media.to_dict()
                data['media_files'] = media_files
                self.storage.write(data)
                return True

        return False

    def delete(self, media_id: int) -> bool:
        """Delete media file by ID"""
        data = self.storage.read()
        media_files = data.get('media_files', [])

        filtered = [m for m in media_files if m['id'] != media_id]
        if len(filtered) < len(media_files):
            data['media_files'] = filtered
            self.storage.write(data)
            return True

        return False

    def cleanup_missing(self) -> int:
        """Remove entries for files that no longer exist"""
        media_files = self.get_all()
        removed = 0

        for media in media_files:
            if not media.exists():
                self.delete(media.id)
                removed += 1

        return removed
```

### 4.4 Audio Engine API

**File:** `app/audio/audio_engine.py`

```python
import pygame
from typing import Optional, Callable
from enum import Enum
import os

class PlaybackState(Enum):
    STOPPED = 0
    PLAYING = 1
    PAUSED = 2

class AudioEngine:
    """Audio playback engine using pygame.mixer"""

    def __init__(self, output_device: str = "hw:0,0"):
        """Initialize pygame mixer"""
        pygame.mixer.init(
            frequency=44100,
            size=-16,
            channels=2,
            buffer=2048
        )

        self.state = PlaybackState.STOPPED
        self.current_file = None
        self.volume = 0.7
        self._on_end_callback = None

        # Set volume
        pygame.mixer.music.set_volume(self.volume)

    def play(self, file_path: str, volume: Optional[float] = None) -> bool:
        """Play audio file"""
        if not os.path.exists(file_path):
            return False

        try:
            pygame.mixer.music.load(file_path)

            if volume is not None:
                self.set_volume(volume)

            pygame.mixer.music.play()
            self.state = PlaybackState.PLAYING
            self.current_file = file_path

            # Set end event
            pygame.mixer.music.set_endevent(pygame.USEREVENT)

            return True
        except pygame.error as e:
            print(f"Audio playback error: {e}")
            return False

    def stop(self) -> None:
        """Stop playback"""
        pygame.mixer.music.stop()
        self.state = PlaybackState.STOPPED
        self.current_file = None

    def pause(self) -> None:
        """Pause playback"""
        if self.state == PlaybackState.PLAYING:
            pygame.mixer.music.pause()
            self.state = PlaybackState.PAUSED

    def resume(self) -> None:
        """Resume playback"""
        if self.state == PlaybackState.PAUSED:
            pygame.mixer.music.unpause()
            self.state = PlaybackState.PLAYING

    def set_volume(self, level: float) -> None:
        """Set volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, level))
        pygame.mixer.music.set_volume(self.volume)

    def get_volume(self) -> float:
        """Get current volume"""
        return self.volume

    def get_position(self) -> float:
        """Get current playback position in seconds"""
        if self.state != PlaybackState.STOPPED:
            # pygame returns position in milliseconds
            pos_ms = pygame.mixer.music.get_pos()
            return pos_ms / 1000.0
        return 0.0

    def seek(self, position: float) -> None:
        """Seek to position in seconds"""
        if self.state != PlaybackState.STOPPED:
            pygame.mixer.music.set_pos(position)

    def is_playing(self) -> bool:
        """Check if audio is currently playing"""
        return self.state == PlaybackState.PLAYING and pygame.mixer.music.get_busy()

    def on_playback_end(self, callback: Callable) -> None:
        """Set callback for when playback ends"""
        self._on_end_callback = callback

    def check_events(self) -> None:
        """Check for pygame music events (call in main loop)"""
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                # Music ended
                self.state = PlaybackState.STOPPED
                if self._on_end_callback:
                    self._on_end_callback()

    def cleanup(self) -> None:
        """Cleanup audio resources"""
        self.stop()
        pygame.mixer.quit()
```

### 4.5 Alarm Scheduler API

**File:** `app/scheduling/alarm_scheduler.py`

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Callable, Optional, List
from datetime import datetime, timedelta
from app.models.alarm import Alarm
from app.storage.alarm_repository import AlarmRepository

class AlarmScheduler:
    """Alarm scheduling using APScheduler"""

    def __init__(self, alarm_repo: AlarmRepository, trigger_callback: Callable):
        self.alarm_repo = alarm_repo
        self.trigger_callback = trigger_callback
        self.scheduler = BackgroundScheduler()
        self.active_alarm_id = None
        self.snooze_job_id = None

    def start(self) -> None:
        """Start the scheduler"""
        self.scheduler.start()
        self._schedule_all_alarms()

    def stop(self) -> None:
        """Stop the scheduler"""
        self.scheduler.shutdown()

    def _schedule_all_alarms(self) -> None:
        """Schedule all enabled alarms"""
        alarms = self.alarm_repo.get_enabled()
        for alarm in alarms:
            self._schedule_alarm(alarm)

    def _schedule_alarm(self, alarm: Alarm) -> None:
        """Schedule a single alarm"""
        if not alarm.enabled:
            return

        # Convert day names to cron format
        day_map = {
            'mon': 'mon', 'tue': 'tue', 'wed': 'wed',
            'thu': 'thu', 'fri': 'fri', 'sat': 'sat', 'sun': 'sun'
        }

        cron_days = ','.join(day_map[d] for d in alarm.days)

        # Create cron trigger
        trigger = CronTrigger(
            hour=alarm.hour,
            minute=alarm.minute,
            day_of_week=cron_days
        )

        # Add job
        job_id = f"alarm_{alarm.id}"
        self.scheduler.add_job(
            func=self._trigger_alarm,
            trigger=trigger,
            id=job_id,
            args=[alarm.id],
            replace_existing=True
        )

    def _trigger_alarm(self, alarm_id: int) -> None:
        """Trigger alarm callback"""
        self.active_alarm_id = alarm_id
        alarm = self.alarm_repo.get_by_id(alarm_id)

        if alarm and alarm.enabled:
            self.trigger_callback(alarm)

            # Schedule auto-dismiss
            if alarm.auto_dismiss_minutes > 0:
                dismiss_time = datetime.now() + timedelta(
                    minutes=alarm.auto_dismiss_minutes
                )
                self.scheduler.add_job(
                    func=self.dismiss_alarm,
                    trigger='date',
                    run_date=dismiss_time,
                    id=f"dismiss_{alarm_id}",
                    args=[alarm_id]
                )

    def snooze_alarm(self, alarm_id: int, minutes: int = 5) -> None:
        """Snooze active alarm"""
        if self.active_alarm_id == alarm_id:
            # Cancel auto-dismiss
            try:
                self.scheduler.remove_job(f"dismiss_{alarm_id}")
            except:
                pass

            # Schedule snooze trigger
            snooze_time = datetime.now() + timedelta(minutes=minutes)
            self.snooze_job_id = f"snooze_{alarm_id}"

            self.scheduler.add_job(
                func=self._trigger_alarm,
                trigger='date',
                run_date=snooze_time,
                id=self.snooze_job_id,
                args=[alarm_id]
            )

            self.active_alarm_id = None

    def dismiss_alarm(self, alarm_id: int) -> None:
        """Dismiss active alarm"""
        if self.active_alarm_id == alarm_id:
            # Cancel auto-dismiss
            try:
                self.scheduler.remove_job(f"dismiss_{alarm_id}")
            except:
                pass

            self.active_alarm_id = None

    def add_alarm(self, alarm: Alarm) -> None:
        """Add and schedule new alarm"""
        self._schedule_alarm(alarm)

    def update_alarm(self, alarm: Alarm) -> None:
        """Update alarm schedule"""
        # Remove old job
        job_id = f"alarm_{alarm.id}"
        try:
            self.scheduler.remove_job(job_id)
        except:
            pass

        # Reschedule if enabled
        if alarm.enabled:
            self._schedule_alarm(alarm)

    def remove_alarm(self, alarm_id: int) -> None:
        """Remove alarm from schedule"""
        job_id = f"alarm_{alarm_id}"
        try:
            self.scheduler.remove_job(job_id)
        except:
            pass

    def get_next_alarm(self) -> Optional[Alarm]:
        """Get next scheduled alarm"""
        alarms = self.alarm_repo.get_enabled()
        if not alarms:
            return None

        now = datetime.now()
        next_alarm = None
        min_delta = None

        for alarm in alarms:
            if alarm.is_active_today():
                alarm_time = datetime.now().replace(
                    hour=alarm.hour,
                    minute=alarm.minute,
                    second=0,
                    microsecond=0
                )

                if alarm_time > now:
                    delta = alarm_time - now
                    if min_delta is None or delta < min_delta:
                        min_delta = delta
                        next_alarm = alarm

        return next_alarm
```

---

## 5. Kivy UI Implementation

### 5.1 Main App Structure

**File:** `app/ui/app.py`

```python
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.config import Config

from app.ui.screens.home import HomeScreen
from app.ui.screens.alarm_list import AlarmListScreen
from app.ui.screens.alarm_edit import AlarmEditScreen
from app.ui.screens.story_player import StoryPlayerScreen
from app.ui.screens.alarm_trigger import AlarmTriggerScreen
from app.ui.screens.settings import SettingsScreen

class RP4PlayerApp(App):
    """Main Kivy application"""

    def __init__(self, event_bus, state_manager, **kwargs):
        super().__init__(**kwargs)
        self.event_bus = event_bus
        self.state_manager = state_manager

        # Configure window
        Config.set('graphics', 'width', '480')
        Config.set('graphics', 'height', '320')
        Config.set('graphics', 'resizable', False)

        # Hide mouse cursor (touchscreen only)
        Config.set('graphics', 'show_cursor', '0')

        Window.size = (480, 320)
        Window.clearcolor = (0.96, 0.96, 0.96, 1)

    def build(self):
        """Build UI"""
        # Create screen manager
        sm = ScreenManager(transition=SlideTransition())

        # Add screens
        sm.add_widget(HomeScreen(name='home', app=self))
        sm.add_widget(AlarmListScreen(name='alarm_list', app=self))
        sm.add_widget(AlarmEditScreen(name='alarm_edit', app=self))
        sm.add_widget(StoryPlayerScreen(name='story_player', app=self))
        sm.add_widget(AlarmTriggerScreen(name='alarm_trigger', app=self))
        sm.add_widget(SettingsScreen(name='settings', app=self))

        # Subscribe to events
        self._subscribe_events()

        return sm

    def _subscribe_events(self):
        """Subscribe to application events"""
        self.event_bus.subscribe('alarm.triggered', self.on_alarm_triggered)
        self.event_bus.subscribe('audio.complete', self.on_audio_complete)

    def on_alarm_triggered(self, alarm):
        """Handle alarm trigger event"""
        self.root.current = 'alarm_trigger'

    def on_audio_complete(self):
        """Handle audio playback completion"""
        # Auto-play next story if in playlist mode
        pass

    def go_to_screen(self, screen_name: str):
        """Navigate to screen"""
        self.root.current = screen_name

    def go_back(self):
        """Navigate back to previous screen"""
        if self.root.current != 'home':
            self.root.current = 'home'
```

### 5.2 Screen Definitions

**File:** `app/ui/screens/home.py`

```python
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from datetime import datetime

class HomeScreen(Screen):
    """Home screen with main navigation"""

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.build_ui()

        # Update clock every second
        Clock.schedule_interval(self.update_clock, 1.0)

    def build_ui(self):
        """Build screen UI"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Header with clock
        header = BoxLayout(size_hint_y=0.2)
        self.time_label = Label(
            text='12:00 AM',
            font_size='32sp',
            bold=True
        )
        self.date_label = Label(
            text='Wed, Mar 5',
            font_size='18sp'
        )
        header.add_widget(self.time_label)
        header.add_widget(self.date_label)
        layout.add_widget(header)

        # Next alarm indicator
        self.next_alarm_label = Label(
            text='Next Alarm: Tomorrow 6:30 AM',
            font_size='16sp',
            size_hint_y=0.1
        )
        layout.add_widget(self.next_alarm_label)

        # Main buttons
        buttons_layout = BoxLayout(spacing=20, size_hint_y=0.5)

        alarm_btn = Button(
            text='🔔\nAlarms',
            font_size='24sp',
            on_press=lambda x: self.app.go_to_screen('alarm_list')
        )

        story_btn = Button(
            text='📖\nStories',
            font_size='24sp',
            on_press=lambda x: self.app.go_to_screen('story_player')
        )

        buttons_layout.add_widget(alarm_btn)
        buttons_layout.add_widget(story_btn)
        layout.add_widget(buttons_layout)

        # Settings button
        settings_btn = Button(
            text='⚙️ Settings',
            font_size='20sp',
            size_hint_y=0.2,
            on_press=lambda x: self.app.go_to_screen('settings')
        )
        layout.add_widget(settings_btn)

        self.add_widget(layout)

    def update_clock(self, dt):
        """Update clock display"""
        now = datetime.now()
        self.time_label.text = now.strftime('%I:%M %p')
        self.date_label.text = now.strftime('%a, %b %d')

    def on_enter(self):
        """Called when screen is displayed"""
        self.update_next_alarm()

    def update_next_alarm(self):
        """Update next alarm display"""
        # Get next alarm from scheduler
        # next_alarm = self.app.alarm_scheduler.get_next_alarm()
        # if next_alarm:
        #     self.next_alarm_label.text = f"Next: {next_alarm.get_time_str()}"
        pass
```

**File:** `app/ui/screens/alarm_list.py`

```python
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from app.ui.widgets.alarm_card import AlarmCard

class AlarmListScreen(Screen):
    """Alarm list screen"""

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.build_ui()

    def build_ui(self):
        """Build screen UI"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header
        header = BoxLayout(size_hint_y=0.1)
        back_btn = Button(
            text='← Back',
            size_hint_x=0.3,
            on_press=lambda x: self.app.go_back()
        )
        title = Label(text='ALARMS', font_size='24sp', bold=True)
        header.add_widget(back_btn)
        header.add_widget(title)
        layout.add_widget(header)

        # Alarm list (scrollable)
        scroll = ScrollView(size_hint_y=0.7)
        self.alarm_container = BoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None
        )
        self.alarm_container.bind(
            minimum_height=self.alarm_container.setter('height')
        )
        scroll.add_widget(self.alarm_container)
        layout.add_widget(scroll)

        # Add button
        add_btn = Button(
            text='+ Add New Alarm',
            font_size='20sp',
            size_hint_y=0.2,
            on_press=lambda x: self.add_alarm()
        )
        layout.add_widget(add_btn)

        self.add_widget(layout)

    def on_enter(self):
        """Called when screen is displayed"""
        self.refresh_alarms()

    def refresh_alarms(self):
        """Reload alarm list"""
        self.alarm_container.clear_widgets()

        # Get alarms from repository
        alarms = self.app.alarm_repo.get_all()

        for alarm in alarms:
            card = AlarmCard(alarm=alarm, screen=self)
            self.alarm_container.add_widget(card)

    def add_alarm(self):
        """Navigate to alarm edit screen"""
        self.app.state_manager.set_state('edit_alarm_id', None)
        self.app.go_to_screen('alarm_edit')

    def edit_alarm(self, alarm_id):
        """Navigate to edit existing alarm"""
        self.app.state_manager.set_state('edit_alarm_id', alarm_id)
        self.app.go_to_screen('alarm_edit')

    def toggle_alarm(self, alarm_id, enabled):
        """Enable/disable alarm"""
        if enabled:
            self.app.alarm_repo.enable(alarm_id)
            self.app.alarm_scheduler.update_alarm(
                self.app.alarm_repo.get_by_id(alarm_id)
            )
        else:
            self.app.alarm_repo.disable(alarm_id)
            self.app.alarm_scheduler.remove_alarm(alarm_id)
```

### 5.3 Custom Widgets

**File:** `app/ui/widgets/alarm_card.py`

```python
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.button import Button
from kivy.properties import ObjectProperty

class AlarmCard(BoxLayout):
    """Alarm list item widget"""

    alarm = ObjectProperty(None)

    def __init__(self, alarm, screen, **kwargs):
        super().__init__(**kwargs)
        self.alarm = alarm
        self.screen = screen

        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 100
        self.padding = 10
        self.spacing = 10

        self.build_ui()

    def build_ui(self):
        """Build card UI"""
        # Left side: Alarm info
        info_layout = BoxLayout(
            orientation='vertical',
            size_hint_x=0.7
        )

        # Time
        time_label = Label(
            text=self.alarm.get_time_str(),
            font_size='24sp',
            bold=True,
            halign='left',
            size_hint_y=0.5
        )

        # Days and sound
        details = f"{self.alarm.get_days_str()}\n🔊 {self.alarm.sound_file}"
        details_label = Label(
            text=details,
            font_size='14sp',
            halign='left',
            size_hint_y=0.5
        )

        info_layout.add_widget(time_label)
        info_layout.add_widget(details_label)

        # Right side: Toggle switch
        toggle = Switch(
            active=self.alarm.enabled,
            size_hint_x=0.3
        )
        toggle.bind(active=self.on_toggle)

        self.add_widget(info_layout)
        self.add_widget(toggle)

        # Make entire card clickable for editing
        self.bind(on_touch_down=self.on_card_click)

    def on_toggle(self, instance, value):
        """Handle toggle switch"""
        self.screen.toggle_alarm(self.alarm.id, value)

    def on_card_click(self, instance, touch):
        """Handle card click for editing"""
        if self.collide_point(*touch.pos):
            self.screen.edit_alarm(self.alarm.id)
            return True
        return super().on_touch_down(touch)
```

**File:** `app/ui/widgets/time_picker.py`

```python
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import NumericProperty

class TimePicker(BoxLayout):
    """Time selection widget"""

    hour = NumericProperty(7)
    minute = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = 20
        self.build_ui()

    def build_ui(self):
        """Build time picker UI"""
        # Hour picker
        hour_layout = BoxLayout(orientation='vertical', spacing=5)
        hour_up = Button(text='▲', size_hint_y=0.3)
        hour_up.bind(on_press=lambda x: self.change_hour(1))

        self.hour_label = Label(
            text='07',
            font_size='32sp',
            bold=True,
            size_hint_y=0.4
        )

        hour_down = Button(text='▼', size_hint_y=0.3)
        hour_down.bind(on_press=lambda x: self.change_hour(-1))

        hour_layout.add_widget(hour_up)
        hour_layout.add_widget(self.hour_label)
        hour_layout.add_widget(hour_down)

        # Separator
        separator = Label(text=':', font_size='32sp', size_hint_x=0.2)

        # Minute picker
        minute_layout = BoxLayout(orientation='vertical', spacing=5)
        minute_up = Button(text='▲', size_hint_y=0.3)
        minute_up.bind(on_press=lambda x: self.change_minute(1))

        self.minute_label = Label(
            text='00',
            font_size='32sp',
            bold=True,
            size_hint_y=0.4
        )

        minute_down = Button(text='▼', size_hint_y=0.3)
        minute_down.bind(on_press=lambda x: self.change_minute(-1))

        minute_layout.add_widget(minute_up)
        minute_layout.add_widget(self.minute_label)
        minute_layout.add_widget(minute_down)

        # AM/PM toggle
        self.am_pm_btn = Button(
            text='AM',
            font_size='20sp',
            size_hint_x=0.3
        )
        self.am_pm_btn.bind(on_press=self.toggle_am_pm)

        self.add_widget(hour_layout)
        self.add_widget(separator)
        self.add_widget(minute_layout)
        self.add_widget(self.am_pm_btn)

    def change_hour(self, delta):
        """Change hour value"""
        self.hour = (self.hour + delta) % 12
        if self.hour == 0:
            self.hour = 12
        self.hour_label.text = f"{self.hour:02d}"

    def change_minute(self, delta):
        """Change minute value"""
        self.minute = (self.minute + delta) % 60
        self.minute_label.text = f"{self.minute:02d}"

    def toggle_am_pm(self, instance):
        """Toggle AM/PM"""
        if instance.text == 'AM':
            instance.text = 'PM'
        else:
            instance.text = 'AM'

    def get_24hour(self) -> int:
        """Get hour in 24-hour format"""
        hour = self.hour % 12
        if self.am_pm_btn.text == 'PM':
            hour += 12
        return hour

    def set_time(self, hour: int, minute: int):
        """Set time value"""
        self.hour = hour % 12 or 12
        self.minute = minute
        self.hour_label.text = f"{self.hour:02d}"
        self.minute_label.text = f"{self.minute:02d}"
        self.am_pm_btn.text = 'PM' if hour >= 12 else 'AM'
```

### 5.4 Kivy Language (.kv) Files

**File:** `assets/kv/widgets.kv`

```
#:kivy 2.1.0

<RoundedButton@Button>:
    background_color: 0.29, 0.56, 0.89, 1  # Blue
    background_normal: ''
    color: 1, 1, 1, 1
    font_size: '18sp'
    size_hint_y: None
    height: 60
    canvas.before:
        Color:
            rgba: self.background_color
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [10,]

<Card@BoxLayout>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [8,]
        Color:
            rgba: 0.8, 0.8, 0.8, 1
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, 8)
            width: 1

<IconButton@Button>:
    background_color: 0.31, 0.78, 0.47, 1  # Green
    background_normal: ''
    color: 1, 1, 1, 1
    font_size: '48sp'
    canvas.before:
        Color:
            rgba: self.background_color
        Ellipse:
            size: self.size
            pos: self.pos
```

---

## 6. Audio System Implementation

### 6.1 MP3 Metadata Reader

**File:** `app/audio/metadata.py`

```python
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from typing import Optional, Tuple

class MP3Metadata:
    """Read MP3 file metadata"""

    @staticmethod
    def get_duration(file_path: str) -> float:
        """Get MP3 duration in seconds"""
        try:
            audio = MP3(file_path)
            return audio.info.length
        except:
            return 0.0

    @staticmethod
    def get_tags(file_path: str) -> Tuple[Optional[str], Optional[str]]:
        """Get title and artist from ID3 tags"""
        try:
            audio = ID3(file_path)
            title = str(audio.get('TIT2', None))
            artist = str(audio.get('TPE1', None))
            return (title, artist)
        except:
            return (None, None)

    @staticmethod
    def get_all_info(file_path: str) -> dict:
        """Get all metadata information"""
        duration = MP3Metadata.get_duration(file_path)
        title, artist = MP3Metadata.get_tags(file_path)

        return {
            'duration': duration,
            'title': title,
            'artist': artist
        }
```

### 6.2 Playlist Manager

**File:** `app/audio/playlist.py`

```python
from typing import List, Optional
from app.models.media import MediaFile

class Playlist:
    """Playlist management"""

    def __init__(self):
        self.items: List[MediaFile] = []
        self.current_index: int = 0

    def add(self, media: MediaFile) -> None:
        """Add media to playlist"""
        self.items.append(media)

    def add_all(self, media_list: List[MediaFile]) -> None:
        """Add multiple media files"""
        self.items.extend(media_list)

    def clear(self) -> None:
        """Clear playlist"""
        self.items.clear()
        self.current_index = 0

    def get_current(self) -> Optional[MediaFile]:
        """Get current media file"""
        if 0 <= self.current_index < len(self.items):
            return self.items[self.current_index]
        return None

    def next(self) -> Optional[MediaFile]:
        """Move to next item"""
        if self.current_index < len(self.items) - 1:
            self.current_index += 1
            return self.get_current()
        return None

    def previous(self) -> Optional[MediaFile]:
        """Move to previous item"""
        if self.current_index > 0:
            self.current_index -= 1
            return self.get_current()
        return None

    def has_next(self) -> bool:
        """Check if there's a next item"""
        return self.current_index < len(self.items) - 1

    def has_previous(self) -> bool:
        """Check if there's a previous item"""
        return self.current_index > 0

    def size(self) -> int:
        """Get playlist size"""
        return len(self.items)

    def is_empty(self) -> bool:
        """Check if playlist is empty"""
        return len(self.items) == 0
```

### 6.3 Sleep Timer

**File:** `app/scheduling/sleep_timer.py`

```python
from threading import Timer
from typing import Callable, Optional
from datetime import datetime, timedelta

class SleepTimer:
    """Sleep timer for auto-stopping playback"""

    def __init__(self, callback: Callable):
        self.callback = callback
        self.timer: Optional[Timer] = None
        self.end_time: Optional[datetime] = None

    def start(self, minutes: int) -> None:
        """Start sleep timer"""
        self.stop()  # Cancel existing timer

        self.end_time = datetime.now() + timedelta(minutes=minutes)
        self.timer = Timer(minutes * 60, self.callback)
        self.timer.start()

    def stop(self) -> None:
        """Stop sleep timer"""
        if self.timer:
            self.timer.cancel()
            self.timer = None
        self.end_time = None

    def is_active(self) -> bool:
        """Check if timer is active"""
        return self.timer is not None and self.timer.is_alive()

    def get_remaining_minutes(self) -> int:
        """Get remaining minutes"""
        if self.end_time:
            remaining = (self.end_time - datetime.now()).total_seconds()
            return max(0, int(remaining / 60))
        return 0
```

---

## 7. Event System

### 7.1 Event Bus Implementation

**File:** `app/core/event_bus.py`

```python
from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from threading import Lock

@dataclass
class Event:
    """Event data class"""
    type: str
    data: Any = None

class EventBus:
    """Simple event bus for decoupled communication"""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._lock = Lock()

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to an event type"""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Unsubscribe from an event type"""
        with self._lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(handler)
                except ValueError:
                    pass

    def publish(self, event_type: str, data: Any = None) -> None:
        """Publish an event"""
        event = Event(type=event_type, data=data)

        with self._lock:
            handlers = self._subscribers.get(event_type, []).copy()

        for handler in handlers:
            try:
                handler(event.data)
            except Exception as e:
                print(f"Error in event handler: {e}")

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

    # USB events
    USB_CONNECTED = "usb.connected"
    USB_DISCONNECTED = "usb.disconnected"
    USB_SYNC_STARTED = "usb.sync_started"
    USB_SYNC_PROGRESS = "usb.sync_progress"
    USB_SYNC_COMPLETE = "usb.sync_complete"
    USB_SYNC_ERROR = "usb.sync_error"

    # System events
    SLEEP_TIMER_STARTED = "system.sleep_timer_started"
    SLEEP_TIMER_EXPIRED = "system.sleep_timer_expired"
    VOLUME_CHANGED = "system.volume_changed"
```

---

## 8. Configuration Management

**File:** `app/core/config_manager.py`

```python
import os
from app.models.settings import Settings
from app.storage.json_storage import JSONStorage

class ConfigManager:
    """Application configuration manager"""

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.storage = JSONStorage(config_path)
        self.settings: Settings = self._load_settings()

    def _load_settings(self) -> Settings:
        """Load settings from JSON file"""
        data = self.storage.read()

        if not data:
            # Create default settings
            settings = Settings(
                audio=AudioSettings(),
                display=DisplaySettings(),
                alarms=AlarmSettings(),
                stories=StorySettings(),
                usb=USBSettings(),
                system=SystemSettings()
            )
            self.storage.write(settings.to_dict())
            return settings

        return Settings.from_dict(data)

    def save(self) -> None:
        """Save current settings"""
        self.storage.write(self.settings.to_dict())

    def get(self, section: str, key: str) -> Any:
        """Get setting value"""
        section_obj = getattr(self.settings, section, None)
        if section_obj:
            return getattr(section_obj, key, None)
        return None

    def set(self, section: str, key: str, value: Any) -> None:
        """Set setting value"""
        section_obj = getattr(self.settings, section, None)
        if section_obj:
            setattr(section_obj, key, value)
            self.save()
```

---

## 9. Error Handling

### 9.1 Logging Configuration

**File:** `app/utils/logger.py`

```python
import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(log_file: str, log_level: str = "INFO") -> logging.Logger:
    """Configure application logger"""

    # Create logger
    logger = logging.getLogger("rp4player")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Create logs directory
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
```

### 9.2 Exception Handling

```python
# Custom exceptions
class RP4PlayerException(Exception):
    """Base exception for RP4 Player"""
    pass

class AudioException(RP4PlayerException):
    """Audio-related exceptions"""
    pass

class StorageException(RP4PlayerException):
    """Storage-related exceptions"""
    pass

class USBException(RP4PlayerException):
    """USB-related exceptions"""
    pass
```

---

## 10. Performance Requirements

### 10.1 Response Times

| Operation | Target | Maximum |
|-----------|--------|---------|
| Touch response | < 100ms | < 200ms |
| Screen transition | < 300ms | < 500ms |
| Audio playback start | < 200ms | < 500ms |
| JSON file read | < 50ms | < 100ms |
| JSON file write | < 100ms | < 200ms |
| USB detection | < 2s | < 5s |

### 10.2 Resource Usage

| Resource | Target | Maximum |
|----------|--------|---------|
| Memory (RSS) | < 300MB | < 500MB |
| CPU (idle) | < 5% | < 10% |
| CPU (playing) | < 15% | < 25% |
| Disk I/O | < 1MB/s | < 5MB/s |

### 10.3 Reliability Metrics

- System uptime: > 99.9%
- Alarm accuracy: ±5 seconds
- Audio playback reliability: > 99.5%
- Data persistence: 100% (no data loss)
- Boot success rate: > 99%

---

**Document End**
