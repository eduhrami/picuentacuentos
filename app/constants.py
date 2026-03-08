from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_DIR = BASE_DIR / "media"
STORIES_DIR = MEDIA_DIR / "stories"
ANIMAL_SOUNDS_DIR = MEDIA_DIR / "animal_sounds"
WALLPAPER_PATH = MEDIA_DIR / "wallpapers" / "default.png"
FALLBACK_WALLPAPER = MEDIA_DIR / "wallpapers" / "default.jpg"

ICONS_DIR = BASE_DIR / "assets" / "icons"
STORY_ICON = ICONS_DIR / "book.png"
ALARM_ICON = ICONS_DIR / "bell.png"
BACK_ICON = ICONS_DIR / "back.png"
HOME_ICON = ICONS_DIR / "home.png"

SOUNDS_JSON = ANIMAL_SOUNDS_DIR / "sounds.json"
STORIES_JSON = STORIES_DIR / "stories.json"

DATA_DIR = BASE_DIR / "data"
ALARMS_JSON = DATA_DIR / "alarms.json"
