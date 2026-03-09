import json
from pathlib import Path

from kivy.config import Config

Config.set("graphics", "width", "480")
Config.set("graphics", "height", "320")
Config.set("graphics", "fullscreen", "1")
Config.set("graphics", "borderless", "1")

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.factory import Factory
from kivy.properties import DictProperty, ListProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager

from app.constants import (
    ADD_ICON,
    ALARMS_JSON,
    ALARM_ICON,
    ANIMAL_SOUNDS_DIR,
    BACK_ICON,
    FALLBACK_WALLPAPER,
    HOME_ICON,
    NEXT_ICON,
    PAUSE_ICON,
    PLAY_ICON,
    PREV_ICON,
    SOUNDS_JSON,
    STORIES_JSON,
    STORY_ICON,
    WALLPAPER_PATH,
)


def _safe_load_json(path: Path, key: str):
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return []
    items = data.get(key, [])
    if not isinstance(items, list):
        return []
    return items


class Story:
    def __init__(self, payload: dict):
        self.id = payload.get("id", "")
        self.title = payload.get("title", "")
        self.sound = payload.get("sound", "")
        self.icon = payload.get("icon", "")

    @property
    def icon_path(self) -> str:
        return str((STORIES_JSON.parent / self.icon).resolve())

    @property
    def sound_path(self) -> str:
        return str((STORIES_JSON.parent / self.sound).resolve())

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "sound": self.sound,
            "icon": self.icon,
            "icon_path": self.icon_path,
            "sound_path": self.sound_path,
        }


class AnimalSound:
    def __init__(self, payload: dict):
        self.id = payload.get("id", "")
        self.label = payload.get("label", "")
        self.sound = payload.get("sound", "")
        self.image = payload.get("image", "")

    @property
    def image_path(self) -> str:
        return str((ANIMAL_SOUNDS_DIR / self.image).resolve())

    @property
    def sound_path(self) -> str:
        return str((ANIMAL_SOUNDS_DIR / self.sound).resolve())

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "sound": self.sound,
            "image": self.image,
            "image_path": self.image_path,
            "sound_path": self.sound_path,
        }


class StoryCard(ButtonBehavior, BoxLayout):
    story = DictProperty({})


class SoundCard(ButtonBehavior, BoxLayout):
    sound = DictProperty({})


class SoundCardSelected(SoundCard):
    pass


class AlarmCard(ButtonBehavior, BoxLayout):
    alarm = DictProperty({})


class HomeScreen(Screen):
    pass


class StoryListScreen(Screen):
    stories = ListProperty([])

    def on_pre_enter(self):
        self.stories = [Story(item).as_dict() for item in _safe_load_json(STORIES_JSON, "stories")]
        self._populate_stories()

    def _populate_stories(self):
        grid = self.ids.story_grid
        grid.clear_widgets()
        for story in self.stories:
            grid.add_widget(StoryCard(story=story))


class StoryPlayerScreen(Screen):
    story_title = StringProperty("")
    story_icon = StringProperty("")
    play_icon = StringProperty("")
    
    _sound = None
    _story_data = None
    _stories = []
    _current_index = 0

    def set_story(self, story: dict, stories: list = None, index: int = 0):
        """Set the story data to be played."""
        self._story_data = story
        self._stories = stories or []
        self._current_index = index
        self.story_title = story.get("title", "")
        self.story_icon = story.get("icon_path", "")

    def on_enter(self):
        """Auto-play when entering the screen."""
        self._load_and_play()

    def on_leave(self):
        """Stop audio when leaving the screen."""
        self._stop_audio()

    def _load_and_play(self):
        """Load the story audio and start playing."""
        if not self._story_data:
            return
        
        sound_path = self._story_data.get("sound_path", "")
        if not sound_path:
            Logger.warning("StoryPlayer: No sound path in story data")
            return
        
        try:
            # Stop any existing audio first
            self._stop_audio()
            
            # Load the new sound
            self._sound = SoundLoader.load(sound_path)
            if self._sound:
                self._sound.play()
                self._update_play_icon(playing=True)
                Logger.info(f"StoryPlayer: Playing {sound_path}")
            else:
                Logger.warning(f"StoryPlayer: Failed to load {sound_path}")
        except Exception:
            Logger.exception("StoryPlayer: Error loading audio")

    def _stop_audio(self):
        """Stop and unload the current audio."""
        if self._sound:
            self._sound.stop()
            self._sound.unload()
            self._sound = None

    def toggle_play(self):
        """Toggle between play and pause."""
        if not self._sound:
            # No sound loaded, try to load and play
            self._load_and_play()
            return
        
        if self._sound.state == "play":
            self._sound.stop()
            self._update_play_icon(playing=False)
        else:
            self._sound.play()
            self._update_play_icon(playing=True)

    def _update_play_icon(self, playing: bool):
        """Update the play/pause button icon."""
        if playing:
            self.play_icon = str(PAUSE_ICON.resolve()) if PAUSE_ICON.exists() else ""
        else:
            self.play_icon = str(PLAY_ICON.resolve()) if PLAY_ICON.exists() else ""

    def prev_story(self):
        """Go to the previous story in the list."""
        if not self._stories:
            return
        self._current_index = (self._current_index - 1) % len(self._stories)
        self._switch_to_story(self._current_index)

    def next_story(self):
        """Go to the next story in the list."""
        if not self._stories:
            return
        self._current_index = (self._current_index + 1) % len(self._stories)
        self._switch_to_story(self._current_index)

    def _switch_to_story(self, index: int):
        """Switch to a story by index and start playing."""
        story = self._stories[index]
        self._story_data = story
        self.story_title = story.get("title", "")
        self.story_icon = story.get("icon_path", "")
        self._load_and_play()


class AlarmListScreen(Screen):
    alarms = ListProperty([])

    def on_pre_enter(self):
        self._load_alarms()

    def _load_alarms(self):
        sounds = _safe_load_json(SOUNDS_JSON, "sounds")
        sound_labels = {item.get("id"): item.get("label", "") for item in sounds}
        alarms = _safe_load_json(ALARMS_JSON, "alarms")
        self.alarms = [self._format_alarm(item, sound_labels) for item in alarms]
        self._populate_list()

    def _format_alarm(self, alarm: dict, sound_labels: dict) -> dict:
        time_value = alarm.get("time", "06:30")
        days = alarm.get("days", [])
        sound_id = alarm.get("sound_id")
        sound_label = sound_labels.get(sound_id, "Sin sonido")
        return {
            "id": alarm.get("id", ""),
            "time": time_value,
            "days": self._format_days(days),
            "days_raw": days,
            "sound": sound_label,
            "sound_id": sound_id,
            "enabled": alarm.get("enabled", True),
        }

    def _format_days(self, days):
        day_map = {
            "mon": "Lun",
            "tue": "Mar",
            "wed": "Mie",
            "thu": "Jue",
            "fri": "Vie",
            "sat": "Sab",
            "sun": "Dom",
        }
        if not isinstance(days, list) or not days:
            return "Sin dias"
        if len(days) == 7:
            return "Diario"
        labels = [day_map.get(day, day) for day in days]
        return ", ".join([label for label in labels if label])

    def _populate_list(self):
        container = self.ids.alarm_list_box
        container.clear_widgets()
        for alarm in self.alarms:
            container.add_widget(AlarmCard(alarm=alarm))


class AlarmTimeScreen(Screen):
    selected_sound_label = StringProperty("Gallo")
    selected_sound_id = StringProperty("rooster")
    alarm_time = StringProperty("06:30")
    alarm_id = StringProperty("")
    selected_days = ListProperty([])

    def set_alarm(self, alarm: dict):
        """Set the alarm to edit."""
        self.alarm_id = alarm.get("id", "")
        self.alarm_time = alarm.get("time", "06:30")
        self.selected_sound_id = alarm.get("sound_id", "rooster")
        self.selected_sound_label = alarm.get("sound", "Gallo")
        self.selected_days = list(alarm.get("days_raw", []))

    def toggle_day(self, day_id: str):
        """Toggle a day on/off."""
        if day_id in self.selected_days:
            self.selected_days.remove(day_id)
        else:
            self.selected_days.append(day_id)
        # Force property update
        self.selected_days = list(self.selected_days)

    def update_sound(self, sound: dict):
        self.selected_sound_label = sound.get("label", "Gallo")
        self.selected_sound_id = sound.get("id", "")

    def save_alarm(self):
        """Save the current alarm to the alarms.json file."""
        if not self.alarm_id:
            Logger.warning("AlarmTimeScreen: No alarm_id set, cannot save")
            return False
        
        try:
            # Load existing alarms
            alarms_data = {"alarms": []}
            if ALARMS_JSON.exists():
                with open(ALARMS_JSON, "r") as f:
                    alarms_data = json.load(f)
            
            # Find and update the alarm
            alarms = alarms_data.get("alarms", [])
            for alarm in alarms:
                if alarm.get("id") == self.alarm_id:
                    alarm["time"] = self.alarm_time
                    alarm["days"] = self.selected_days
                    alarm["sound_id"] = self.selected_sound_id
                    break
            
            # Save back to file
            with open(ALARMS_JSON, "w") as f:
                json.dump(alarms_data, f, indent=2)
            
            Logger.info(f"AlarmTimeScreen: Saved alarm {self.alarm_id}")
            return True
        except Exception:
            Logger.exception("AlarmTimeScreen: Failed to save alarm")
            return False

    def on_pre_enter(self):
        if not self.selected_sound_label:
            self.selected_sound_label = "Gallo"


class AlarmSoundScreen(Screen):
    sounds = ListProperty([])
    selected_sound_id = StringProperty("")

    def on_pre_enter(self):
        self.sounds = [AnimalSound(item).as_dict() for item in _safe_load_json(SOUNDS_JSON, "sounds")]
        self._sync_selected_from_alarm_time()
        self._populate_sounds()

    def _populate_sounds(self):
        grid = self.ids.sound_grid
        grid.clear_widgets()
        for sound in self.sounds:
            card_cls = SoundCard
            if self.selected_sound_id and sound.get("id") == self.selected_sound_id:
                card_cls = SoundCardSelected
            grid.add_widget(card_cls(sound=sound))
        grid.do_layout()

    def set_selected_sound(self, sound_id: str):
        self.selected_sound_id = sound_id
        Clock.schedule_once(lambda _dt: self._populate_sounds(), 0)

    def _sync_selected_from_alarm_time(self):
        alarm_time = self.manager.get_screen("alarm_time")
        selected_id = getattr(alarm_time, "selected_sound_id", "")
        if not selected_id:
            selected_id = "rooster"
        self.selected_sound_id = selected_id
        if not alarm_time.selected_sound_label:
            rooster = next((item for item in self.sounds if item.get("id") == "rooster"), None)
            if rooster:
                alarm_time.update_sound(rooster)


class RootScreenManager(ScreenManager):
    pass


class AlarmRingingScreen(Screen):
    pass


Factory.register("RootScreenManager", cls=RootScreenManager)
Factory.register("AlarmRingingScreen", cls=AlarmRingingScreen)
Factory.register("SoundCardSelected", cls=SoundCardSelected)


class PiCuentaCuentosApp(App):
    wallpaper_path = StringProperty("")
    story_icon_path = StringProperty("")
    alarm_icon_path = StringProperty("")
    back_icon_path = StringProperty("")
    home_icon_path = StringProperty("")
    prev_icon_path = StringProperty("")
    next_icon_path = StringProperty("")
    play_icon_path = StringProperty("")
    pause_icon_path = StringProperty("")
    add_icon_path = StringProperty("")

    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        self._alarm_preview = None
        if WALLPAPER_PATH.exists():
            self.wallpaper_path = str(WALLPAPER_PATH.resolve())
        elif FALLBACK_WALLPAPER.exists():
            self.wallpaper_path = str(FALLBACK_WALLPAPER.resolve())
        else:
            self.wallpaper_path = ""
        return Builder.load_file(str(Path(__file__).with_name("ui.kv")))

    def on_start(self):
        Clock.schedule_interval(self._update_time, 1)
        self._update_time(0)
        self._load_home_icons()

    def _update_time(self, _dt):
        from datetime import datetime

        now = datetime.now()
        home = self.root.get_screen("home")
        home.ids.time_label.text = now.strftime("%H:%M")
        home.ids.date_label.text = now.strftime("%a, %d %b")

    def _load_home_icons(self):
        if STORY_ICON.exists():
            self.story_icon_path = str(STORY_ICON.resolve())
        else:
            self.story_icon_path = ""

        if ALARM_ICON.exists():
            self.alarm_icon_path = str(ALARM_ICON.resolve())
        else:
            self.alarm_icon_path = ""

        if BACK_ICON.exists():
            self.back_icon_path = str(BACK_ICON.resolve())
        else:
            self.back_icon_path = ""

        if HOME_ICON.exists():
            self.home_icon_path = str(HOME_ICON.resolve())
        else:
            self.home_icon_path = ""

        if PREV_ICON.exists():
            self.prev_icon_path = str(PREV_ICON.resolve())
        else:
            self.prev_icon_path = ""

        if NEXT_ICON.exists():
            self.next_icon_path = str(NEXT_ICON.resolve())
        else:
            self.next_icon_path = ""

        if PLAY_ICON.exists():
            self.play_icon_path = str(PLAY_ICON.resolve())
        else:
            self.play_icon_path = ""

        if PAUSE_ICON.exists():
            self.pause_icon_path = str(PAUSE_ICON.resolve())
        else:
            self.pause_icon_path = ""

        if ADD_ICON.exists():
            self.add_icon_path = str(ADD_ICON.resolve())
        else:
            self.add_icon_path = ""

    def open_story(self, story: dict):
        # Get the stories list from StoryListScreen
        story_list_screen = self.root.get_screen("story_list")
        stories = story_list_screen.stories
        
        # Find the index of the selected story
        index = 0
        story_id = story.get("id", "")
        for i, s in enumerate(stories):
            if s.get("id") == story_id:
                index = i
                break
        
        player = self.root.get_screen("story_player")
        player.set_story(story, stories, index)
        self.root.current = "story_player"

    def edit_alarm(self, alarm: dict):
        """Open the alarm editor with the selected alarm."""
        alarm_time_screen = self.root.get_screen("alarm_time")
        alarm_time_screen.set_alarm(alarm)
        self.root.current = "alarm_time"

    def choose_alarm_sound(self, sound: dict):
        alarm_time = self.root.get_screen("alarm_time")
        alarm_time.update_sound(sound)
        self.root.current = "alarm_time"

    def select_alarm_sound(self, sound: dict):
        try:
            self.preview_alarm_sound(sound)
            alarm_time = self.root.get_screen("alarm_time")
            alarm_time.update_sound(sound)
            alarm_sound = self.root.get_screen("alarm_sound")
            alarm_sound.set_selected_sound(sound.get("id", ""))
        except Exception:
            Logger.exception("Alarm sound selection failed")

    def preview_alarm_sound(self, sound: dict):
        """Play a short preview of the selected alarm sound."""
        try:
            # Stop any existing preview
            self.stop_alarm_preview()
            
            # Get the sound file path
            sound_file = sound.get("sound", "")
            if not sound_file:
                return
            
            sound_path = ANIMAL_SOUNDS_DIR / sound_file
            if not sound_path.exists():
                Logger.warning(f"Sound file not found: {sound_path}")
                return
            
            # Load and play
            self._alarm_preview = SoundLoader.load(str(sound_path))
            if self._alarm_preview:
                self._alarm_preview.play()
                # Auto-stop after 2 seconds
                Clock.schedule_once(lambda dt: self.stop_alarm_preview(), 2.0)
        except Exception:
            Logger.exception("Failed to preview alarm sound")

    def stop_alarm_preview(self):
        if self._alarm_preview:
            self._alarm_preview.stop()
            self._alarm_preview = None


if __name__ == "__main__":
    PiCuentaCuentosApp().run()
