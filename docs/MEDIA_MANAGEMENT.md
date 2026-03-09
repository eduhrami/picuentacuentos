# Media Management Guide

Media content is managed through two JSON configuration files.
The app reads them at startup — no background scanning, no auto-detection.
To add or remove content, edit the JSON and restart the app.

---

## Directory Structure

```
media/
└── stories/
    ├── stories.json    ← catalogue of stories
    ├── some-story.mp3
    └── some-icon.png   ← optional per story

assets/
└── animal_sounds/
    ├── sounds.json     ← catalogue of alarm sounds
    ├── lion.mp3
    ├── lion.png
    └── ...
```

---

## Animal Sounds (`assets/animal_sounds/sounds.json`)

Each entry needs a sound file and an image file, both in the same folder.

```json
{
  "sounds": [
    {
      "id": "lion",
      "label": "León",
      "sound": "lion.mp3",
      "image": "lion.png"
    },
    {
      "id": "rooster",
      "label": "Gallo",
      "sound": "rooster.mp3",
      "image": "rooster.png"
    }
  ]
}
```

| Field | Description |
|-------|-------------|
| `id` | Unique identifier (used internally and in alarm records) |
| `label` | Display name shown in the UI |
| `sound` | MP3 filename (relative to `assets/animal_sounds/`) |
| `image` | PNG filename (relative to `assets/animal_sounds/`) |

### Add an animal sound

1. Copy `mySound.mp3` and `mySound.png` into `assets/animal_sounds/`
2. Add entry to `sounds.json`
3. Restart: `sudo systemctl restart getty@tty1`

### Remove an animal sound

1. Delete the entry from `sounds.json`
2. Optionally delete the files from disk
3. Restart: `sudo systemctl restart getty@tty1`

---

## Stories (`media/stories/stories.json`)

Each entry needs a sound file. An icon is optional — omit it or set it to `null`
to fall back to the default story icon.

```json
{
  "stories": [
    {
      "id": "la-liebre-y-la-tortuga",
      "title": "La Liebre y la Tortuga",
      "sound": "01 La liebre 🐰 y la tortuga 🐢 - Fábula infantil.mp3",
      "icon": null
    },
    {
      "id": "caperucita-roja",
      "title": "Caperucita Roja",
      "sound": "caperucita-roja.mp3",
      "icon": "caperucita.png"
    }
  ]
}
```

| Field | Description |
|-------|-------------|
| `id` | Unique identifier |
| `title` | Display title shown in the UI |
| `sound` | MP3 filename (relative to `media/stories/`) |
| `icon` | PNG filename, or `null` to use the default icon |

### Add a story

1. Copy the `.mp3` (and optionally a `.png` icon) into `media/stories/`
2. Add entry to `stories.json`
3. Restart: `sudo systemctl restart getty@tty1`

### Remove a story

1. Delete the entry from `stories.json`
2. Optionally delete the files from disk
3. Restart: `sudo systemctl restart getty@tty1`

---

## File Specifications

| Type | Format | Duration | Bitrate |
|------|--------|----------|---------|
| Animal sounds | MP3 | 2–30 seconds | 128kbps+ |
| Stories | MP3 | 5–30 minutes | 128kbps+ |
| Images / icons | PNG | — | 480×320 max |

---

## Copying Files to the Pi

Files live in the project repository and are deployed to the Pi via the normal
deploy workflow (see `deploy-to-pi` skill). You can also copy files manually:

```bash
# Copy a new story
scp my-story.mp3 pi@picuentacuentos.local:/home/pi/picuentacuentos/media/stories/

# Copy a new animal sound + image
scp frog.mp3 frog.png pi@picuentacuentos.local:/home/pi/picuentacuentos/assets/animal_sounds/

# Then edit the JSON and restart
ssh pi@picuentacuentos.local 'nano /home/pi/picuentacuentos/media/stories/stories.json'
ssh pi@picuentacuentos.local 'sudo systemctl restart getty@tty1'
```

If `picuentacuentos.local` does not resolve, add it on your PC:
- Linux/macOS:
  ```bash
  sudo sh -c 'printf "\n192.168.x.x picuentacuentos.local\n" >> /etc/hosts'
  ```
- Windows: add `192.168.x.x picuentacuentos.local` to
  `C:\Windows\System32\drivers\etc\hosts`
