# AGENTS

## Project snapshot
- App: Kivy UI for Raspberry Pi kiosk (`app/main.py`, `app/ui.kv`)
- Assets: alarm sounds are app-owned in `assets/animal_sounds`
- Stories: user media in `media/stories`
- Icons: `assets/icons`
- Device: Pi reachable as `picuentacuentos.local`

## Kiosk + Pi workflow
- Start kiosk: `sudo systemctl restart getty@tty1`
- Stop kiosk: `sudo systemctl stop getty@tty1`
- Current `/home/pi/.bash_profile`: starts X once (no restart loop)
- Stop X session: `sudo pkill -f Xorg`
- Logs: `/home/pi/.kivy/logs/kivy_*.txt`
- App entry: `/home/pi/picuentacuentos/start.sh` (sets `PYTHONPATH`)

## Deployment
- Use `rsync -av --exclude ".git" ./ pi@picuentacuentos.local:/home/pi/picuentacuentos/`
- Then restart kiosk with `sudo systemctl restart getty@tty1`

## UI patterns (keep consistent)
- Icon buttons: use `ButtonBehavior+Layout` composite
- Header nav on list screens: 48px container, 32px icon
- Player controls: `IconOnlyButton` with fixed 72px icon
- Floating back/home: anchored top-left with explicit size + `pos_hint`
- Avoid ScrollView when a fixed grid fits on-screen (touch issues on Pi)

## Alarm sounds
- Source: `assets/animal_sounds/sounds.json`
- Kivy path: `app/constants.py` (`ANIMAL_SOUNDS_DIR`)
- Default selection: `rooster` when none set
- Selection should stay on Alarm Sound screen (no auto-navigation)

## Known issues / debugging
- Audio preview in Alarm Sound screen freezes input when played directly.
- Audio test works in isolation using:
  `/home/pi/picuentacuentos/tmp_audio_test.py`
- If UI freezes, check Kivy logs for exceptions.

## Suggested next investigation
- Build a minimal Kivy test app with one button that plays a sound.
- Try alternate backend (ffpyplayer) or preload sound objects on screen entry.
