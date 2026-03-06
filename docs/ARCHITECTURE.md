# RaspberryPi Kids' Audio Player - Architecture & Specification Document

**Document Version:** 1.0
**Date:** 2026-03-05
**Project:** RP4 Kids' MP3 Player & Alarm Clock
**Platform:** RaspberryPi 4 with 3.5" Touchscreen

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Component Specifications](#4-component-specifications)
5. [Data Architecture](#5-data-architecture)
6. [User Interface Specification](#6-user-interface-specification)
7. [Audio System Specification](#7-audio-system-specification)
8. [Security & Safety](#8-security--safety)
9. [Deployment Specification](#9-deployment-specification)
10. [Testing Strategy](#10-testing-strategy)

---

## 1. Executive Summary

### 1.1 Purpose
Design and implement a standalone, child-friendly audio player and alarm clock system running on RaspberryPi 4 hardware with a 3.5" touchscreen interface.

### 1.2 Key Objectives
- Provide intuitive alarm management for children aged 4+
- Enable bedtime story playback with sleep timer
- Support content management via SSH (administrator only)
- Ensure reliable, autonomous operation without child access to settings
- Deliver audio output through 3.5mm auxiliary jack

### 1.3 Success Criteria
- Touch response time < 200ms
- System boot time < 30 seconds
- Alarm accuracy within ±5 seconds
- Zero missed alarms due to system failures
- Child-operable without adult assistance
- Media updates via SSH only (secure, administrator-controlled)

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     RaspberryPi 4 Hardware                   │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   3.5" LCD  │  │   Network    │  │  3.5mm Audio Out │   │
│  │  Touchscreen│  │  (WiFi/Eth)  │  │   (AUX Jack)     │   │
│  └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘   │
│         │                │                    │              │
└─────────┼────────────────┼────────────────────┼──────────────┘
          │                │                    │
┌─────────┴────────────────┴────────────────────┴──────────────┐
│                   Operating System Layer                      │
│         Raspberry Pi OS (Debian-based) + SSH Server           │
└─────────────────────────────┬─────────────────────────────────┘
                              │
┌─────────────────────────────┴─────────────────────────────────┐
│                    Application Layer                          │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              Main Application (Python)                │    │
│  │                                                        │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐ │    │
│  │  │ UI Manager  │  │ Audio Engine │  │   Alarm     │ │    │
│  │  │  (Kivy)     │  │  (pygame)    │  │  Scheduler  │ │    │
│  │  └──────┬──────┘  └──────┬───────┘  └──────┬──────┘ │    │
│  │         │                │                  │         │    │
│  │  ┌──────┴────────────────┴──────────────────┴──────┐ │    │
│  │  │         Application Core (Event Bus)            │ │    │
│  │  └──────┬────────────────┬──────────────────┬──────┘ │    │
│  │         │                │                  │         │    │
│  │  ┌──────┴──────┐  ┌──────┴───────┐  ┌──────┴──────┐ │    │
│  │  │   Media     │  │    State     │  │   Config    │ │    │
│  │  │  Scanner    │  │   Manager    │  │   Manager   │ │    │
│  │  └─────────────┘  └──────────────┘  └─────────────┘ │    │
│  └──────────────────────────────────────────────────────┘    │
└───────────────────────────────┬───────────────────────────────┘
                                │
┌───────────────────────────────┴───────────────────────────────┐
│                     Data Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  JSON Data   │  │  JSON Config │  │   Media Files    │   │
│  │  (alarms)    │  │  (settings)  │  │   (MP3s)         │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└───────────────────────────────────────────────────────────────┘
        ▲
        │ SSH/SCP (Administrator uploads media)
        │
┌───────┴──────┐
│ Admin Client │
└──────────────┘
```

### 2.2 Component Interaction Diagram

```
┌──────────┐         ┌──────────────┐         ┌───────────┐
│          │ Touch   │              │ Events  │           │
│   User   ├────────>│  UI Manager  │<───────>│   Event   │
│          │ Events  │   (Kivy)     │         │    Bus    │
└──────────┘         └──────┬───────┘         └─────┬─────┘
                            │                       │
                     Screen │                       │ Commands
                    Updates │                       │
                            v                       v
                     ┌──────────────┐        ┌─────────────┐
                     │   Display    │        │   State     │
                     │  (3.5" LCD)  │        │  Manager    │
                     └──────────────┘        └──────┬──────┘
                                                    │
     ┌──────────────────────────────────────────────┼────────┐
     │                                              │        │
     v                                              v        v
┌─────────────┐                              ┌──────────┐  ┌──────────┐
│   Alarm     │ Trigger                      │  Audio   │  │  Media   │
│  Scheduler  ├─────────────────────────────>│  Engine  │  │ Scanner  │
└──────┬──────┘                              └────┬─────┘  └────┬─────┘
       │                                          │             │
       │ Check Time                               │ Play        │ Scan
       v                                          v             v
┌──────────────┐                          ┌────────────┐  ┌──────────┐
│   JSON       │                          │  3.5mm     │  │   Media  │
│  (Alarms)    │                          │  Audio Out │  │  Storage │
└──────────────┘                          └────────────┘  └──────────┘
                                                                ▲
                                                                │
                                                          SSH/SCP Upload
                                                                │
                                                          ┌──────────┐
                                                          │  Admin   │
                                                          └──────────┘
```

### 2.3 Process Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Main Process: rp4player                                │
│                                                          │
│  ┌────────────────────┐  ┌──────────────────────────┐  │
│  │  Thread 1:         │  │  Thread 2:               │  │
│  │  UI Event Loop     │  │  Audio Playback          │  │
│  │  (Kivy Main)       │  │  (pygame.mixer)          │  │
│  └────────────────────┘  └──────────────────────────┘  │
│                                                          │
│  ┌────────────────────┐  ┌──────────────────────────┐  │
│  │  Thread 3:         │  │  Thread 4:               │  │
│  │  Alarm Monitor     │  │  Media Scanner           │  │
│  │  (APScheduler)     │  │  (Periodic Scan)         │  │
│  └────────────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

### 3.1 Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Operating System | Raspberry Pi OS (Lite) | 11+ (Bullseye) | Base system |
| Programming Language | Python | 3.9+ | Application development |
| UI Framework | Kivy | 2.1.0+ | Touch interface |
| Audio Library | pygame | 2.5.0+ | MP3 playback |
| Scheduler | APScheduler | 3.10.0+ | Alarm scheduling |
| Database | SQLite | 3.x | Alarm storage |
| SSH Server | OpenSSH | Native | Remote media management |
| Audio Output | ALSA | Native | Audio routing to 3.5mm |

### 3.2 Python Dependencies

```
kivy==2.1.0
pygame==2.5.0
APScheduler==3.10.1
pyudev==0.24.0
mutagen==1.46.0  # MP3 metadata reading
```

### 3.3 System Dependencies

```
- python3-dev
- python3-pip
- libsdl2-dev
- libsdl2-image-dev
- libsdl2-mixer-dev
- libsdl2-ttf-dev
- libasound2-dev
- alsa-utils
```

---

## 4. Component Specifications

### 4.1 UI Manager (ui_manager.py)

**Responsibility:** Manage all screen rendering and touch input

**Interfaces:**
```python
class UIManager:
    def __init__(self, event_bus: EventBus)
    def show_screen(self, screen_name: str) -> None
    def update_alarm_list(self, alarms: List[Alarm]) -> None
    def update_story_list(self, stories: List[Story]) -> None
    def show_notification(self, message: str, duration: int) -> None
```

**Screen Definitions:**
- HomeScreen: Main menu with time and navigation
- AlarmListScreen: Display and manage alarms
- AlarmEditScreen: Create/edit alarm settings
- StoryPlayerScreen: Browse and play stories
- SettingsScreen: System configuration
- AlarmActiveScreen: Displayed during alarm trigger

**Key Features:**
- Resolution: 480x320 pixels (3.5" display)
- Font size: Minimum 24pt for readability
- Touch targets: Minimum 80x80 pixels
- Color scheme: High contrast, child-friendly

### 4.2 Audio Engine (audio_engine.py)

**Responsibility:** Handle all audio playback operations

**Interfaces:**
```python
class AudioEngine:
    def __init__(self, output_device: str = "hw:0,0")
    def play(self, file_path: str, volume: float = 0.7) -> None
    def stop(self) -> None
    def pause(self) -> None
    def resume(self) -> None
    def set_volume(self, level: float) -> None  # 0.0 to 1.0
    def get_duration(self, file_path: str) -> float
    def get_current_position(self) -> float
    def seek(self, position: float) -> None
```

**Audio Configuration:**
- Output: 3.5mm jack (ALSA device hw:0,0)
- Format support: MP3 (primary), WAV, OGG (optional)
- Sample rates: 44.1kHz, 48kHz
- Channels: Stereo
- Buffering: 2048 bytes

**State Management:**
```python
class PlaybackState(Enum):
    STOPPED = 0
    PLAYING = 1
    PAUSED = 2
```

### 4.3 Alarm Scheduler (alarm_scheduler.py)

**Responsibility:** Manage alarm scheduling and execution

**Interfaces:**
```python
class AlarmScheduler:
    def __init__(self, db_manager: DatabaseManager, audio_engine: AudioEngine)
    def add_alarm(self, alarm: Alarm) -> int
    def update_alarm(self, alarm_id: int, alarm: Alarm) -> None
    def delete_alarm(self, alarm_id: int) -> None
    def enable_alarm(self, alarm_id: int) -> None
    def disable_alarm(self, alarm_id: int) -> None
    def get_next_alarm(self) -> Optional[Alarm]
    def trigger_alarm(self, alarm_id: int) -> None
    def snooze_alarm(self, alarm_id: int, minutes: int = 5) -> None
    def dismiss_alarm(self, alarm_id: int) -> None
```

**Alarm Data Model:**
```python
@dataclass
class Alarm:
    id: int
    enabled: bool
    hour: int  # 0-23
    minute: int  # 0-59
    days: List[str]  # ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    sound_file: str
    volume: float  # 0.0 to 1.0
    label: str
    snooze_enabled: bool
    auto_dismiss_minutes: int  # Default: 10
```

**Scheduling Strategy:**
- Use APScheduler with CronTrigger
- Check alarms every minute for accuracy
- Persist alarm state to SQLite
- Handle daylight saving time transitions

### 4.4 USB Manager (usb_manager.py)

**Responsibility:** Detect USB devices and synchronize media files

**Interfaces:**
```python
class USBManager:
    def __init__(self, event_bus: EventBus, media_dir: str)
    def start_monitoring(self) -> None
    def stop_monitoring(self) -> None
    def sync_media(self, usb_path: str) -> SyncResult
    def validate_usb_structure(self, usb_path: str) -> bool
```

**Expected USB Structure:**
```
USB_DRIVE/
├── alarms/
│   ├── sound1.mp3
│   └── sound2.mp3
└── stories/
    ├── story1.mp3
    └── story2.mp3
```

**Sync Process:**
1. Detect USB insertion (udev event)
2. Mount device (if not auto-mounted)
3. Validate folder structure
4. Calculate files to copy (new/modified only)
5. Copy files with progress tracking
6. Verify copied files (checksum optional)
7. Update media database
8. Emit sync complete event
9. Safely unmount

**Sync Result:**
```python
@dataclass
class SyncResult:
    success: bool
    files_copied: int
    files_failed: int
    errors: List[str]
```

### 4.5 State Manager (state_manager.py)

**Responsibility:** Centralized application state management

**Interfaces:**
```python
class StateManager:
    def __init__(self)
    def get_state(self, key: str) -> Any
    def set_state(self, key: str, value: Any) -> None
    def subscribe(self, key: str, callback: Callable) -> None
```

**Application State:**
```python
AppState = {
    "current_screen": str,
    "active_alarm": Optional[Alarm],
    "playback_state": PlaybackState,
    "current_story": Optional[Story],
    "sleep_timer_active": bool,
    "sleep_timer_remaining": int,  # seconds
    "volume": float,
    "usb_sync_in_progress": bool,
}
```

### 4.6 Event Bus (event_bus.py)

**Responsibility:** Decouple components via event-driven architecture

**Interfaces:**
```python
class EventBus:
    def subscribe(self, event_type: str, handler: Callable) -> None
    def unsubscribe(self, event_type: str, handler: Callable) -> None
    def publish(self, event: Event) -> None
```

**Event Types:**
```python
class EventType(Enum):
    # Alarm events
    ALARM_TRIGGERED = "alarm.triggered"
    ALARM_SNOOZED = "alarm.snoozed"
    ALARM_DISMISSED = "alarm.dismissed"

    # Audio events
    PLAYBACK_STARTED = "audio.started"
    PLAYBACK_STOPPED = "audio.stopped"
    PLAYBACK_PAUSED = "audio.paused"
    PLAYBACK_COMPLETE = "audio.complete"

    # USB events
    USB_CONNECTED = "usb.connected"
    USB_DISCONNECTED = "usb.disconnected"
    USB_SYNC_STARTED = "usb.sync_started"
    USB_SYNC_COMPLETE = "usb.sync_complete"

    # UI events
    SCREEN_CHANGED = "ui.screen_changed"
    USER_INTERACTION = "ui.interaction"

    # System events
    SLEEP_TIMER_EXPIRED = "system.sleep_timer_expired"
    VOLUME_CHANGED = "system.volume_changed"
```

---

## 5. Data Architecture

### 5.1 Database Schema (SQLite)

**File:** `/home/pi/rp4player/data/rp4player.db`

```sql
-- Alarms Table
CREATE TABLE alarms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enabled BOOLEAN NOT NULL DEFAULT 1,
    hour INTEGER NOT NULL CHECK(hour >= 0 AND hour < 24),
    minute INTEGER NOT NULL CHECK(minute >= 0 AND minute < 60),
    days TEXT NOT NULL,  -- JSON array: ["mon","tue","wed"]
    sound_file TEXT NOT NULL,
    volume REAL NOT NULL DEFAULT 0.7 CHECK(volume >= 0.0 AND volume <= 1.0),
    label TEXT,
    snooze_enabled BOOLEAN DEFAULT 1,
    auto_dismiss_minutes INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Media Files Table
CREATE TABLE media_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL UNIQUE,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,  -- 'alarm' or 'story'
    duration_seconds REAL,
    file_size_bytes INTEGER,
    title TEXT,  -- From MP3 metadata
    artist TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Playback History Table (optional, for resume functionality)
CREATE TABLE playback_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    media_file_id INTEGER NOT NULL,
    last_position_seconds REAL DEFAULT 0,
    last_played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (media_file_id) REFERENCES media_files(id)
);

-- System Settings Table
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_alarms_enabled ON alarms(enabled);
CREATE INDEX idx_media_type ON media_files(file_type);
```

### 5.2 Configuration Files

**File:** `/home/pi/rp4player/config/settings.json`

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

### 5.3 File System Structure

```
/home/pi/rp4player/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   ├── config.py                  # Configuration loader
│   ├── event_bus.py               # Event system
│   ├── state_manager.py           # State management
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── ui_manager.py          # Main UI controller
│   │   ├── screens/
│   │   │   ├── home.py
│   │   │   ├── alarm_list.py
│   │   │   ├── alarm_edit.py
│   │   │   ├── story_player.py
│   │   │   └── settings.py
│   │   └── widgets/
│   │       ├── alarm_card.py
│   │       ├── story_card.py
│   │       └── time_picker.py
│   │
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── audio_engine.py        # Audio playback
│   │   └── audio_utils.py         # Helper functions
│   │
│   ├── alarms/
│   │   ├── __init__.py
│   │   ├── alarm_scheduler.py     # Alarm logic
│   │   └── alarm_models.py        # Data models
│   │
│   ├── usb/
│   │   ├── __init__.py
│   │   ├── usb_manager.py         # USB detection & sync
│   │   └── file_sync.py           # File operations
│   │
│   └── database/
│       ├── __init__.py
│       ├── db_manager.py          # Database operations
│       └── migrations/
│           └── 001_initial.sql
│
├── config/
│   └── settings.json              # Configuration file
│
├── data/
│   ├── rp4player.db              # SQLite database
│   └── backups/                  # DB backups
│
├── media/
│   ├── alarms/                   # Alarm sound files
│   └── stories/                  # Story files
│
├── logs/
│   └── app.log                   # Application logs
│
├── assets/
│   ├── fonts/                    # UI fonts
│   ├── icons/                    # UI icons
│   └── images/                   # Background images
│
├── tests/
│   ├── test_audio.py
│   ├── test_alarms.py
│   └── test_usb.py
│
├── requirements.txt              # Python dependencies
├── setup.sh                      # Installation script
└── README.md                     # Documentation
```

---

## 6. User Interface Specification

### 6.1 Display Specifications

- **Resolution:** 480x320 pixels
- **Orientation:** Landscape
- **Touch Type:** Resistive/Capacitive (driver dependent)
- **Color Depth:** 24-bit RGB

### 6.2 Design System

**Color Palette:**
```python
COLORS = {
    "primary": "#4A90E2",      # Blue
    "secondary": "#50C878",    # Green
    "warning": "#FFB347",      # Orange
    "danger": "#FF6B6B",       # Red
    "background": "#F5F5F5",   # Light Gray
    "surface": "#FFFFFF",      # White
    "text_primary": "#212121", # Dark Gray
    "text_secondary": "#757575" # Medium Gray
}
```

**Typography:**
```python
FONTS = {
    "heading": ("Roboto-Bold", 32),
    "subheading": ("Roboto-Medium", 24),
    "body": ("Roboto-Regular", 20),
    "caption": ("Roboto-Regular", 16)
}
```

**Spacing:**
```python
SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32
}
```

### 6.3 Screen Layouts

#### Home Screen (home.kv)
```
┌────────────────────────────────────────┐
│  🕐 7:35 AM          Wed, Mar 5        │ <- Header
├────────────────────────────────────────┤
│                                        │
│      Next Alarm: Tomorrow 6:30 AM      │
│                                        │
│  ┌──────────┐  ┌──────────┐          │
│  │    🔔    │  │    📖    │          │
│  │          │  │          │          │
│  │  Alarms  │  │ Stories  │          │
│  │          │  │          │          │
│  └──────────┘  └──────────┘          │
│                                        │
│  ┌──────────────────────────────┐    │
│  │            ⚙️                 │    │
│  │         Settings             │    │
│  └──────────────────────────────┘    │
│                                        │
└────────────────────────────────────────┘
```

#### Alarm List Screen
```
┌────────────────────────────────────────┐
│  ← Back            ALARMS              │
├────────────────────────────────────────┤
│                                        │
│  ┌─────────────────────────────────┐  │
│  │ 🌅 6:30 AM      [ON/OFF Toggle] │  │
│  │ Mon, Tue, Wed, Thu, Fri         │  │
│  │ 🔊 Rooster Sound                │  │
│  └─────────────────────────────────┘  │
│                                        │
│  ┌─────────────────────────────────┐  │
│  │ 🌙 9:00 PM      [ON/OFF Toggle] │  │
│  │ Every Day                        │  │
│  │ 🔊 Gentle Bells                 │  │
│  └─────────────────────────────────┘  │
│                                        │
│           ┌──────────┐                │
│           │    +     │                │
│           │ Add New  │                │
│           └──────────┘                │
└────────────────────────────────────────┘
```

#### Story Player Screen
```
┌────────────────────────────────────────┐
│  ← Back          BEDTIME STORIES       │
├────────────────────────────────────────┤
│  Now Playing:                          │
│  🎵 The Three Little Pigs              │
│                                        │
│  ┌────────────────────────────────┐   │
│  │▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░│   │ <- Progress
│  └────────────────────────────────┘   │
│  2:35 / 8:45                           │
│                                        │
│     ⏮️         ⏯️         ⏭️            │ <- Controls
│   Previous    Play      Next           │
│                                        │
│  ┌─────────────────┐  ┌────────────┐  │
│  │  🔊 Volume: 75% │  │  ⏲️ Timer  │  │
│  └─────────────────┘  └────────────┘  │
│                                        │
│  Story List: ▼                         │
│  • The Three Little Pigs (playing)     │
│  • Goldilocks                          │
│  • Little Red Riding Hood              │
└────────────────────────────────────────┘
```

### 6.4 Interaction Patterns

**Button States:**
- Normal: Base color
- Hover/Touch: 10% darker
- Active/Pressed: 20% darker
- Disabled: 50% opacity, grayscale

**Feedback:**
- Touch: Visual highlight (immediate)
- Action: Brief animation (200ms)
- Success: Green checkmark (2s)
- Error: Red X with message (5s)

**Navigation:**
- Back button: Top-left on all sub-screens
- Home button: Dedicated hardware or screen button
- Swipe gestures: Optional, not primary navigation

---

## 7. Audio System Specification

### 7.1 Hardware Configuration

**Audio Output:**
- Port: 3.5mm TRRS jack (GPIO header pins or USB audio adapter)
- Channels: Stereo (L/R)
- Impedance: 32Ω (typical headphone/speaker)
- Output level: Line level (~1V RMS) or headphone level

**ALSA Configuration:**

File: `/etc/asound.conf`
```
pcm.!default {
    type hw
    card 0
    device 0
}

ctl.!default {
    type hw
    card 0
}
```

**Force 3.5mm Jack Output:**

File: `/boot/config.txt`
```
# Force audio output to 3.5mm jack
dtparam=audio=on
audio_pwm_mode=2

# Disable HDMI audio
hdmi_ignore_edid_audio=1
```

### 7.2 Audio Engine Implementation

**pygame.mixer Configuration:**
```python
import pygame

pygame.mixer.init(
    frequency=44100,    # Sample rate (Hz)
    size=-16,           # Sample size (16-bit signed)
    channels=2,         # Stereo
    buffer=2048,        # Buffer size (samples)
    devicename=None,    # Use default ALSA device
    allowedchanges=0    # Don't allow format changes
)
```

**Volume Control:**
```python
# System volume (ALSA)
import subprocess

def set_system_volume(percent: int):
    """Set system volume via amixer"""
    subprocess.run([
        'amixer', 'sset', 'PCM', f'{percent}%'
    ])

# Application volume (pygame)
def set_app_volume(level: float):
    """Set application volume (0.0 to 1.0)"""
    pygame.mixer.music.set_volume(level)
```

**Audio File Support:**
- Primary: MP3 (MPEG-1 Audio Layer III)
- Fallback: WAV (uncompressed)
- Optional: OGG Vorbis

**Playback Features:**
- Concurrent playback: No (single channel for simplicity)
- Queue support: Yes (playlist for stories)
- Resume playback: Yes (save position to database)
- Crossfade: No (v1.0), Optional (v2.0)

### 7.3 Audio Testing Procedure

**Test Sequence:**
1. System boot audio test
   ```bash
   aplay /usr/share/sounds/alsa/Front_Center.wav
   ```

2. Python audio test
   ```python
   import pygame
   pygame.mixer.init()
   pygame.mixer.music.load("test.mp3")
   pygame.mixer.music.play()
   ```

3. Volume range test (0%, 50%, 100%)
4. Long playback test (30 min file)
5. Interrupt handling test (alarm over story)

---

## 8. Security & Safety

### 8.1 File System Security

**Read-Only Root Filesystem:**
- Enable overlayfs to prevent SD card corruption
- Mount `/home/pi/rp4player/data` as read-write
- Regular database backups to USB

**File Validation:**
```python
ALLOWED_EXTENSIONS = ['.mp3', '.wav']
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

def validate_media_file(file_path: str) -> bool:
    # Check extension
    if not any(file_path.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        return False

    # Check file size
    if os.path.getsize(file_path) > MAX_FILE_SIZE:
        return False

    # Verify MP3 header (basic check)
    try:
        from mutagen.mp3 import MP3
        MP3(file_path)
        return True
    except:
        return False
```

### 8.2 Child Safety Features

**Parental Lock (Future):**
- PIN-protected settings screen
- Restrict alarm deletion
- Prevent volume exceeding safe levels (85dB)

**Volume Limiting:**
```python
MAX_SAFE_VOLUME = 0.85  # 85% maximum

def set_volume_safe(level: float):
    capped_volume = min(level, MAX_SAFE_VOLUME)
    audio_engine.set_volume(capped_volume)
```

**Screen Time Management:**
- Auto-sleep display after inactivity
- No internet access (offline only)
- No app installation capabilities

### 8.3 Error Handling

**Graceful Degradation:**
- Missing audio file: Use default beep tone
- Database corruption: Fallback to JSON config
- USB sync failure: Retry with user notification

**Logging:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/pi/rp4player/logs/app.log'),
        logging.StreamHandler()
    ]
)
```

**Watchdog:**
- Monitor main application process
- Auto-restart on crash
- Send error logs to persistent storage

---

## 9. Deployment Specification

### 9.1 System Requirements

**Hardware:**
- RaspberryPi 4 (2GB+ RAM recommended)
- 3.5" touchscreen display (SPI or HDMI)
- MicroSD card (16GB+ Class 10)
- 3.5mm speakers or headphones
- 5V 3A USB-C power supply
- USB flash drive for content updates

**Software:**
- Raspberry Pi OS (Lite or Desktop)
- Python 3.9+
- 2GB free disk space

### 9.2 Installation Script

**File:** `setup.sh`

```bash
#!/bin/bash
set -e

echo "=== RaspberryPi Kids' Player Setup ==="

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libasound2-dev \
    alsa-utils \
    git

# Configure audio output to 3.5mm jack
sudo amixer cset numid=3 1

# Create application directory
mkdir -p /home/pi/rp4player
cd /home/pi/rp4player

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create directory structure
mkdir -p config data media/alarms media/stories logs assets/{fonts,icons,images}

# Initialize database
python app/database/db_manager.py --init

# Copy default configuration
cp config/settings.default.json config/settings.json

# Set permissions
chmod +x app/main.py

# Create systemd service
sudo tee /etc/systemd/system/rp4player.service > /dev/null <<EOF
[Unit]
Description=RaspberryPi Kids Audio Player
After=sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/rp4player
ExecStart=/home/pi/rp4player/venv/bin/python /home/pi/rp4player/app/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable rp4player.service

# Configure auto-start on boot (for GUI)
mkdir -p /home/pi/.config/autostart
tee /home/pi/.config/autostart/rp4player.desktop > /dev/null <<EOF
[Desktop Entry]
Type=Application
Name=RP4Player
Exec=/home/pi/rp4player/venv/bin/python /home/pi/rp4player/app/main.py
EOF

echo "=== Setup Complete ==="
echo "Reboot to start the application"
```

### 9.3 Configuration Steps

**1. Display Configuration:**

For SPI displays, edit `/boot/config.txt`:
```
# Enable SPI
dtparam=spi=on

# LCD settings (example for Waveshare 3.5")
dtoverlay=waveshare35a
hdmi_force_hotplug=1
hdmi_cvt=480 320 60 1 0 0 0
hdmi_group=2
hdmi_mode=87
```

**2. Touch Calibration:**
```bash
sudo apt-get install xinput-calibrator
DISPLAY=:0.0 xinput_calibrator
```

**3. Disable Screen Blanking:**

Edit `/etc/xdg/lxsession/LXDE-pi/autostart`:
```
@xset s off
@xset -dpms
@xset s noblank
```

### 9.4 Startup Sequence

```
1. Boot Raspberry Pi OS
2. Start systemd services
3. Initialize ALSA audio
4. Launch rp4player.service
   ├── Load configuration
   ├── Initialize database connection
   ├── Start audio engine
   ├── Start alarm scheduler
   ├── Start USB monitor
   ├── Initialize UI (Kivy)
   └── Show home screen
5. Ready for user interaction
```

### 9.5 Update Procedure

**Application Updates:**
```bash
cd /home/pi/rp4player
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart rp4player.service
```

**Content Updates:**
1. Insert USB drive with media files
2. Application auto-detects USB
3. Sync process runs automatically
4. Notification shows completion
5. Remove USB drive

---

## 10. Testing Strategy

### 10.1 Unit Testing

**Test Framework:** pytest

**Test Coverage Requirements:**
- Audio engine: 90%+
- Alarm scheduler: 95%+
- Database operations: 90%+
- USB manager: 85%+
- UI components: 70%+

**Example Test Cases:**

```python
# tests/test_audio.py
def test_audio_playback():
    engine = AudioEngine()
    engine.play("test_files/sample.mp3")
    assert engine.is_playing()
    engine.stop()
    assert not engine.is_playing()

def test_volume_control():
    engine = AudioEngine()
    engine.set_volume(0.5)
    assert engine.get_volume() == 0.5

# tests/test_alarms.py
def test_alarm_creation():
    scheduler = AlarmScheduler(mock_db, mock_audio)
    alarm = Alarm(hour=7, minute=30, days=["mon", "tue"])
    alarm_id = scheduler.add_alarm(alarm)
    assert alarm_id > 0

def test_alarm_trigger():
    scheduler = AlarmScheduler(mock_db, mock_audio)
    with freeze_time("2026-03-05 07:30:00"):
        scheduler.check_alarms()
        assert mock_audio.play_called
```

### 10.2 Integration Testing

**Test Scenarios:**
1. Complete alarm flow: Set → Trigger → Snooze → Dismiss
2. Story playback: Browse → Select → Play → Pause → Resume
3. USB sync: Insert → Detect → Copy → Complete
4. UI navigation: Home → Alarms → Edit → Save → Home
5. Sleep timer: Start story → Set timer → Auto-stop

### 10.3 Hardware Testing

**Manual Test Checklist:**

- [ ] Display renders correctly (no artifacts)
- [ ] Touch input responsive (<200ms)
- [ ] Audio output clear through 3.5mm jack
- [ ] Volume control functional (0-100%)
- [ ] USB detection immediate (<2s)
- [ ] System boots to app automatically
- [ ] No audio dropouts during playback
- [ ] Alarms trigger at exact time (±5s)
- [ ] Screen dimming after timeout
- [ ] System stable over 48h operation

### 10.4 User Acceptance Testing

**Child Testing Protocol:**
- Age group: 4-8 years
- Tasks:
  1. Set a new alarm
  2. Turn alarm on/off
  3. Browse and play a story
  4. Adjust volume
  5. Stop story playback

**Success Criteria:**
- 90%+ task completion without adult help
- <2 minutes to complete each task
- Positive feedback on interface
- No confusion on primary actions

### 10.5 Performance Benchmarks

| Metric | Target | Acceptable | Unacceptable |
|--------|--------|------------|--------------|
| Boot time | <20s | <30s | >30s |
| Touch response | <100ms | <200ms | >200ms |
| Screen transition | <300ms | <500ms | >500ms |
| Audio start latency | <100ms | <200ms | >200ms |
| USB sync (100 files) | <30s | <60s | >60s |
| Memory usage | <500MB | <750MB | >1GB |
| CPU usage (idle) | <10% | <20% | >30% |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| ALSA | Advanced Linux Sound Architecture - Linux audio framework |
| APScheduler | Advanced Python Scheduler - Python job scheduling library |
| Kivy | Open-source Python framework for multi-touch applications |
| TRRS | Tip-Ring-Ring-Sleeve - 4-conductor 3.5mm audio connector |
| Pygame | Python library for multimedia applications |
| udev | Linux device manager for /dev/ directory |

---

## Appendix B: Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-05 | System Architect | Initial architecture specification |

---

**Document End**
