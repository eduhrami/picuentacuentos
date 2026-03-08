import json
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import DictProperty, ListProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager

from app.constants import ALARMS_JSON, ANIMAL_SOUNDS_DIR, SOUNDS_JSON, STORIES_JSON, WALLPAPER_PATH


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

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "sound": self.sound,
            "icon": self.icon,
            "icon_path": self.icon_path,
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

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "sound": self.sound,
            "image": self.image,
            "image_path": self.image_path,
        }


class StoryCard(ButtonBehavior, BoxLayout):
    story = DictProperty({})


class SoundCard(ButtonBehavior, BoxLayout):
    sound = DictProperty({})


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
    is_playing = False
    play_icon = StringProperty("⏸️")

    def set_story(self, story: dict):
        self.story_title = story.get("title", "")
        self.story_icon = story.get("icon_path", "")
        self.is_playing = True
        self.play_icon = "⏸️"

    def toggle_play(self):
        self.is_playing = not self.is_playing
        self.play_icon = "⏸️" if self.is_playing else "▶️"


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
            "time": time_value,
            "days": self._format_days(days),
            "sound": sound_label,
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

    def update_sound(self, sound: dict):
        self.selected_sound_label = sound.get("label", "Gallo")

    def on_pre_enter(self):
        if not self.selected_sound_label:
            self.selected_sound_label = "Gallo"


class AlarmSoundScreen(Screen):
    sounds = ListProperty([])

    def on_pre_enter(self):
        self.sounds = [AnimalSound(item).as_dict() for item in _safe_load_json(SOUNDS_JSON, "sounds")]
        self._populate_sounds()

    def _populate_sounds(self):
        grid = self.ids.sound_grid
        grid.clear_widgets()
        for sound in self.sounds:
            grid.add_widget(SoundCard(sound=sound))


class RootScreenManager(ScreenManager):
    pass


class PiCuentaCuentosApp(App):
    wallpaper_path = StringProperty("")

    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        self.wallpaper_path = str(WALLPAPER_PATH.resolve())
        return Builder.load_file(str(Path(__file__).with_name("ui.kv")))

    def on_start(self):
        Clock.schedule_interval(self._update_time, 1)
        self._update_time(0)

    def _update_time(self, _dt):
        from datetime import datetime

        now = datetime.now()
        home = self.root.get_screen("home")
        home.ids.time_label.text = now.strftime("%H:%M")
        home.ids.date_label.text = now.strftime("%a, %d %b")

    def open_story(self, story: dict):
        player = self.root.get_screen("story_player")
        player.set_story(story)
        self.root.current = "story_player"

    def choose_alarm_sound(self, sound: dict):
        alarm_time = self.root.get_screen("alarm_time")
        alarm_time.update_sound(sound)
        self.root.current = "alarm_time"


if __name__ == "__main__":
    PiCuentaCuentosApp().run()
