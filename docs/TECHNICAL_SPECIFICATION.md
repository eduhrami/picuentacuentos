# RaspberryPi Kids' Audio Player - Technical Specification

**Document Version:** 2.0
**Date:** 2026-03-05
**Project:** RP4 Kids' MP3 Player & Alarm Clock
**UI Framework:** Kivy
**Storage:** JSON (Internal Only)
**Media Management:** JSON Config Files

---

## Table of Contents
0. [Product Requirements](#0-product-requirements)
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

## 0. Product Requirements

### 0.1 Scope

- Provide a touch-first interface for setting alarms and playing stories.
- Allow selecting an alarm sound per alarm.
- Support MP3 files only, installed via SSH.
- No remote control features in v2.0.

### 0.2 Personas and Usage

- Primary users: children (approx. ages 5 to 10).
- Device operation is entirely child-driven; adult involvement is limited to media updates via PC commands.
- Usage context: bedside alarm and bedtime story playback.

### 0.3 Functional Requirements

Alarms
- FR-ALARM-001: The system SHALL allow creating, editing, and deleting alarms.
- FR-ALARM-002: Each alarm SHALL define a time (HH:MM, 24 hour).
- FR-ALARM-003: Each alarm SHALL support day-of-week activation toggles.
- FR-ALARM-004: Each alarm SHALL allow selecting one MP3 sound for the alarm.
- FR-ALARM-005: Alarm playback SHALL loop until stopped or max duration is reached.
- FR-ALARM-006: Each alarm SHALL have an enabled or disabled state.
- FR-ALARM-007: Each alarm SHALL support a per-alarm volume setting.
- FR-ALARM-008: Alarm snooze SHOULD be supported with 5 to 10 minute interval.
- FR-ALARM-009: If an alarm triggers while a story is playing, story playback SHALL pause.
- FR-ALARM-010: Alarm time and day selection SHALL be edited separately from alarm sound selection.

Stories
- FR-STORY-001: The system SHALL list MP3 stories from internal /home/pi/picuentacuentos/media/stories.
- FR-STORY-002: The system SHALL allow play, pause, and stop controls.
- FR-STORY-003: The system SHALL allow next and previous within a collection.
- FR-STORY-004: The system SHALL provide a sleep timer with presets 10, 20, 30, 45, 60 minutes.
- FR-STORY-005: The system SHALL stop playback when the sleep timer elapses.

Media install and catalogs
- FR-MEDIA-001: The system SHALL load media catalogs from JSON files at startup.
- FR-MEDIA-002: Media catalog changes SHALL require app restart to take effect.
- FR-MEDIA-003: Media SHALL be installed via SSH to internal storage.
- FR-MEDIA-004: Media files SHALL be referenced via JSON catalogs, not filesystem scanning.

User interface
- FR-UI-001: All features SHALL be operable via touch only.
- FR-UI-002: The home screen SHALL show current time and day.
- FR-UI-003: The system SHALL provide dedicated screens for alarms and stories.
- FR-UI-004: The system SHALL provide a settings screen.
- FR-UI-005: The system SHALL allow selecting a wallpaper via a JSON-configured path.

System behavior
- FR-SYS-001: The app SHALL auto-start at boot in full-screen mode.
- FR-SYS-002: The system SHALL persist alarms and settings across reboots.

### 0.4 Non-Functional Requirements

- NFR-UX-001: Touch targets SHALL be at least 9 mm in size.
- NFR-PERF-001: Boot to UI target is 30 seconds or less.
- NFR-ROB-001: Settings SHALL be written using safe write (temp file then rename).
- NFR-AUDIO-001: Only one audio stream SHALL be active at a time.
- NFR-REL-001: Alarms MUST trigger regardless of story playback state.

### 0.5 Media Conventions

- Internal folder layout:
  - /home/pi/picuentacuentos/media/animal_sounds: alarm sounds and images
  - /home/pi/picuentacuentos/media/stories: story files and optional icons
  - /home/pi/picuentacuentos/media/animal_sounds/sounds.json: alarm catalog
  - /home/pi/picuentacuentos/media/stories/stories.json: story catalog
  - /home/pi/picuentacuentos/wallpapers/default.png: default wallpaper
- File types: MP3 only in v2.0.
- Display name: from JSON catalog (label/title).

### 0.6 UI Structure and Flows

Screens
- HomeScreen: time and day, buttons for Alarms, Stories, Settings
- AlarmListScreen: list alarms with time and enabled toggle, add alarm button
- AlarmTimeScreen: time selector, day toggles, save or delete
- AlarmSoundScreen: sound picker from sounds.json, volume slider
- StoryLibraryScreen: list stories by folder, tap to open NowPlayingScreen
- NowPlayingScreen: title, play or pause, next or previous, sleep timer button
- AlarmRingingScreen: stop and snooze buttons
- SettingsScreen: time set, max volume, brightness

Primary flows
- Alarm setup: Home -> Alarms -> Add Alarm -> Set time and days -> Next -> Choose sound -> Save
- Story playback: Home -> Stories -> Select Story -> Play -> Sleep Timer optional
- Media update: Upload MP3s via SSH -> update JSON catalogs -> restart app

### 0.7 Out of Scope v2.0

- Remote control of playback
- Multiple user profiles
- Playlists or shuffle

## 1. Technology Stack

### 1.1 Core Dependencies

```txt
# requirements.txt
kivy==2.2.1
pygame==2.5.2
APScheduler==3.10.4
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
openssh-server
```

### 1.3 Python Version
- Minimum: Python 3.9
- Recommended: Python 3.11

---

## 2. Application Structure

### 2.1 Directory Layout

```
/home/pi/picuentacuentos/
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
│   │   └── media_loader.py         # JSON config reader
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
│   │   │   ├── alarm_time.py       # Alarm time editor
│   │   │   ├── alarm_sound.py      # Alarm sound picker
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
│   ├── media.json                  # Media library (optional)
│   ├── playback.json               # Playback state
│   └── backups/                    # Backup files
│
├── config/
│   └── settings.json               # Application settings
│
├── media/
│   ├── animal_sounds/              # Alarm sound files + images
│   │   ├── sounds.json             # ** EDIT TO ADD/REMOVE alarm sounds **
│   │   ├── lion.mp3
│   │   ├── lion.png
│   │   └── ...
│   └── stories/                    # Story MP3 files + icons
│       ├── stories.json            # ** EDIT TO ADD/REMOVE stories **
│       ├── some-story.mp3
│       └── some-icon.png           # optional per story
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
│       ├── alarm_time.kv
│       ├── alarm_sound.kv
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
  ├── ui.app.PiCuentaCuentosApp
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
  ├── media.media_loader.MediaLoader
  │
  ├── core.event_bus.EventBus
  ├── core.state_manager.StateManager
  └── core.config_manager.ConfigManager
```

---

## 3. Data Models & JSON Schema

### 3.1 Animal Sounds Config

**File:** `media/animal_sounds/sounds.json`

```json
{
  "sounds": [
    {
      "id": "lion",
      "label": "León",
      "sound": "lion.mp3",
      "image": "lion.png"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `label` | string | Display name shown in the UI |
| `sound` | string | Filename relative to `media/animal_sounds/` |
| `image` | string | Filename relative to `media/animal_sounds/` |

### 3.2 Stories Config

**File:** `media/stories/stories.json`

```json
{
  "stories": [
    {
      "id": "la-liebre-y-la-tortuga",
      "title": "La Liebre y la Tortuga",
      "sound": "01 La liebre 🐰 y la tortuga 🐢 - Fábula infantil.mp3",
      "icon": "liebre.png"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `title` | string | Display title shown in the UI |
| `sound` | string | Filename relative to `media/stories/` |
| `icon` | string\|null | Filename relative to `media/stories/`, or `null` to use default icon |

### 3.3 Alarm Model

Alarms reference a sound by its `id` from `sounds.json`:

```json
{
  "alarms": [
    {
      "id": "a1b2c3",
      "label": "Despertar",
      "time": "07:30",
      "days": ["mon", "tue", "wed", "thu", "fri"],
      "sound_id": "rooster",
      "enabled": true
    }
  ]
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
    wallpaper_path: str = "/home/pi/picuentacuentos/wallpapers/default.png"

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
    sounds_config: str = "/home/pi/picuentacuentos/media/animal_sounds/sounds.json"
    stories_config: str = "/home/pi/picuentacuentos/media/stories/stories.json"

@dataclass
class SystemSettings:
    log_level: str = "INFO"
    log_file: str = "/home/pi/picuentacuentos/logs/app.log"

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
    "orientation": 0,
    "wallpaper_path": "/home/pi/picuentacuentos/wallpapers/default.png"
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
    "sounds_config": "/home/pi/picuentacuentos/media/animal_sounds/sounds.json",
    "stories_config": "/home/pi/picuentacuentos/media/stories/stories.json"
  },
  "system": {
    "log_level": "INFO",
    "log_file": "/home/pi/picuentacuentos/logs/app.log"
  }
}
```

---

## 4. API Specifications

[Alarm Repository and Media Repository sections remain the same...]

### 4.4 Media Loader API

**File:** `app/media/media_loader.py`

```python
import json
import os
from typing import List
from dataclasses import dataclass

@dataclass
class AnimalSound:
    id: str
    label: str
    sound_path: str
    image_path: str

@dataclass
class Story:
    id: str
    title: str
    sound_path: str
    icon_path: str | None  # None falls back to a default icon

class MediaLoader:
    """Load media catalogues from JSON config files."""

    def __init__(self, sounds_config: str, stories_config: str):
        self.sounds_config = sounds_config
        self.stories_config = stories_config

    def load_sounds(self) -> List[AnimalSound]:
        """Return all animal sounds defined in sounds.json."""
        base = os.path.dirname(self.sounds_config)
        with open(self.sounds_config, encoding="utf-8") as f:
            data = json.load(f)
        return [
            AnimalSound(
                id=s["id"],
                label=s["label"],
                sound_path=os.path.join(base, s["sound"]),
                image_path=os.path.join(base, s["image"]),
            )
            for s in data["sounds"]
        ]

    def load_stories(self) -> List[Story]:
        """Return all stories defined in stories.json."""
        base = os.path.dirname(self.stories_config)
        with open(self.stories_config, encoding="utf-8") as f:
            data = json.load(f)
        return [
            Story(
                id=s["id"],
                title=s["title"],
                sound_path=os.path.join(base, s["sound"]),
                icon_path=os.path.join(base, s["icon"]) if s.get("icon") else None,
            )
            for s in data["stories"]
        ]
```

Media is loaded once at startup. To add or remove content, edit the JSON file and restart the app.

[Audio Engine, Alarm Scheduler, etc. remain the same]

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

    # System events
    SLEEP_TIMER_STARTED = "system.sleep_timer_started"
    SLEEP_TIMER_EXPIRED = "system.sleep_timer_expired"
    VOLUME_CHANGED = "system.volume_changed"
```

---

## 9. Media Management via JSON Config

Media is catalogue-driven. The app reads two JSON files at startup and plays whatever
is listed in them. There is no filesystem scanning or background watching.

### 9.1 Adding an Animal Sound

1. Copy the `.mp3` and `.png` files into `media/animal_sounds/`.
2. Add an entry to `media/animal_sounds/sounds.json`:

```json
{
  "id": "frog",
  "label": "Rana",
  "sound": "frog.mp3",
  "image": "frog.png"
}
```

3. Restart the app: `sudo systemctl restart getty@tty1`

### 9.2 Adding a Story

1. Copy the `.mp3` into `media/stories/`. An icon image is optional.
2. Add an entry to `media/stories/stories.json`:

```json
{
  "id": "caperucita-roja",
  "title": "Caperucita Roja",
  "sound": "caperucita-roja.mp3",
  "icon": "caperucita.png"
}
```

Set `"icon": null` to use the default story icon.

3. Restart the app: `sudo systemctl restart getty@tty1`

### 9.3 Removing Content

Delete the entry from the JSON file and optionally remove the files from disk.
Restart the app to apply.

### 9.4 File Specifications

| Type | Format | Duration | Bitrate |
|------|--------|----------|---------|
| Animal sounds | MP3 | 2–30 seconds | 128kbps+ |
| Stories | MP3 | 5–30 minutes | 128kbps+ |
| Images / icons | PNG | — | 480×320 max |

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
| Media catalogue load | < 100ms | < 300ms |

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
- Media catalog load success rate: 100%

---

**Document End**

**Changes from v2.0:**
- Aligned docs to JSON-driven media catalogs and removed scanning references
- Clarified alarm time vs alarm sound screens
