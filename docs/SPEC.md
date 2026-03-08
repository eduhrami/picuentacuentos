# Raspberry Pi Kids' Audio Player - Product Specification (v2.0)

This document defines the v2.0 product specification and high-level architecture for a Raspberry Pi based MP3 player and alarm clock designed for children. The system runs on a Raspberry Pi 4 with a 3.5 inch touch display and stores all media internally. Media is managed via JSON catalog files and installed via SSH.

## 1. Scope

- Provide a touch-first interface for setting alarms and playing stories.
- Allow selecting an alarm sound per alarm.
- Support MP3 files only, installed via SSH.
- No remote control features in v2.0.

## 2. Personas and Usage

- Primary users: children (approx. ages 5 to 10).
- Secondary users: parents for setup and maintenance.
- Usage context: bedside alarm and bedtime story playback.

## 3. Functional Requirements

### 3.1 Alarms

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

### 3.2 Stories

- FR-STORY-001: The system SHALL list MP3 stories from internal /home/pi/picuentacuentos/media/stories.
- FR-STORY-002: The system SHALL allow play, pause, and stop controls.
- FR-STORY-003: The system SHALL allow next and previous within a collection.
- FR-STORY-004: The system SHALL provide a sleep timer with presets 10, 20, 30, 45, 60 minutes.
- FR-STORY-005: The system SHALL stop playback when the sleep timer elapses.

### 3.3 Media Install and Catalogs

- FR-MEDIA-001: The system SHALL load media catalogs from JSON files at startup.
- FR-MEDIA-002: Media catalog changes SHALL require app restart to take effect.
- FR-MEDIA-003: Media SHALL be installed via SSH to internal storage.
- FR-MEDIA-004: Media files SHALL be referenced via JSON catalogs, not filesystem scanning.

### 3.4 User Interface

- FR-UI-001: All features SHALL be operable via touch only.
- FR-UI-002: The home screen SHALL show current time and day.
- FR-UI-003: The system SHALL provide dedicated screens for alarms and stories.
- FR-UI-004: The system SHALL provide a settings screen.

### 3.5 System Behavior

- FR-SYS-001: The app SHALL auto-start at boot in full-screen mode.
- FR-SYS-002: The system SHALL persist alarms and settings across reboots.

## 4. Non-Functional Requirements

- NFR-UX-001: Touch targets SHALL be at least 9 mm in size.
- NFR-PERF-001: Boot to UI target is 30 seconds or less.
- NFR-ROB-001: Settings SHALL be written using safe write (temp file then rename).
- NFR-AUDIO-001: Only one audio stream SHALL be active at a time.
- NFR-REL-001: Alarms MUST trigger regardless of story playback state.

## 5. Media Conventions

- Internal folder layout:
  - /home/pi/picuentacuentos/media/animal_sounds: alarm sounds and images
  - /home/pi/picuentacuentos/media/stories: story files and optional icons
  - /home/pi/picuentacuentos/media/animal_sounds/sounds.json: alarm catalog
  - /home/pi/picuentacuentos/media/stories/stories.json: story catalog
- File types: MP3 only in v2.0.
- Display name: from JSON catalog (label/title).

## 6. Architecture

### 6.1 Technology Choice

- Language: Python 3
- UI: Kivy (touch-first)
- Audio: pygame.mixer
- Storage: JSON (v2.0)

### 6.2 Component Overview

- UI Layer
  - HomeScreen
  - AlarmListScreen
  - AlarmTimeScreen
  - AlarmSoundScreen
  - StoryLibraryScreen
  - NowPlayingScreen
  - SettingsScreen
  - AlarmRingingScreen

- Services
  - AlarmService: schedules alarms, triggers playback, snooze logic
  - PlayerService: audio control, volume, playback state
- MediaLoader: loads JSON catalogs at startup
  - SettingsService: persistent settings and safe write
  - ClockService: time access and manual setting

### 6.3 Data Storage

JSON storage (v2.0):

- data/alarms.json
  - alarms: list of alarm objects
  - fields: id, time, enabled, days, sound_id, volume, snooze_minutes

- data/playback.json
  - resume state for stories (optional)

- config/settings.json
  - structured settings for audio, display, alarms, stories, media, system

- media/animal_sounds/sounds.json
  - catalog of alarm sounds (id, label, sound, image)

- media/stories/stories.json
  - catalog of stories (id, title, sound, icon)

Notes:
- Use safe write: write temp file then rename.

### 6.4 Media Catalog Loading

- Media is stored under /home/pi/picuentacuentos/media.
- On app start:
  - load media/animal_sounds/sounds.json
  - load media/stories/stories.json
  - no background scanning or watchers

### 6.5 Alarm Scheduling

- AlarmService checks schedule at 30 second interval or uses APScheduler.
- On trigger:
  - pause story playback if active
  - play alarm sound on loop
  - show AlarmRingingScreen with Stop and Snooze

### 6.6 Playback Rules

- Only one audio stream at a time.
- Alarm playback has priority over stories.
- Story resume after alarm stop is optional and can be enabled in settings.

### 6.7 App Startup

- Systemd service auto-starts the app on boot.
- Kiosk mode: disable screen blanking and cursor.

## 7. UI Structure and Flows

### 7.1 Screens

- HomeScreen
  - shows time and day
  - buttons: Alarms, Stories, Settings

- AlarmListScreen
  - list alarms with time and enabled toggle
  - add alarm button

- AlarmTimeScreen
  - time selector
  - day toggles
  - save or delete

- AlarmSoundScreen
  - sound picker from sounds.json
  - volume slider

- StoryLibraryScreen
  - list stories by folder
  - tap story to open NowPlayingScreen

- NowPlayingScreen
  - title, play or pause, next or previous
  - sleep timer button

- AlarmRingingScreen
  - stop and snooze buttons

- SettingsScreen
  - time set
  - max volume
  - brightness

### 7.2 Primary Flows

Alarm setup:
- Home -> Alarms -> Add Alarm -> Set time and days -> Next -> Choose sound -> Save

Story playback:
- Home -> Stories -> Select Story -> Play -> Sleep Timer optional

Media update:
- Upload MP3s via SSH -> update JSON catalogs -> restart app

## 8. Out of Scope v2.0

- Remote control of playback
- Multiple user profiles
- Playlists or shuffle
