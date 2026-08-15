from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from ..styles.themes import Theme

class CardWidget(BoxLayout):
    def __init__(self, bg_color=Theme.CARD_BG, radius=[10], **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 8
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=radius)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class PartHeaderLabel(Label):
    def __init__(self, title, is_premium=False, **kwargs):
        super().__init__(**kwargs)
        badge = " [color=E8AB26][★ Premium][/color]" if is_premium else " [color=8AB86C][✓ Gratuit][/color]"
        self.text = f"[b]{title}[/b]{badge}"
        self.markup = True
        self.font_size = '18sp'
        self.color = Theme.PRIMARY_DARK
        self.size_hint_y = None
        self.height = 40
        self.halign = 'left'
        self.valign = 'middle'
        self.bind(size=self._update_size)

    def _update_size(self, instance, value):
        self.text_size = (self.width, None)

class ChapterButton(Button):
    def __init__(self, title, is_premium=False, reading_time=5, **kwargs):
        super().__init__(**kwargs)
        icon = "[★ LOCK]" if is_premium else "▸"
        self.text = f"  {icon}  {title} ({reading_time} min)"
        self.font_size = '15sp'
        self.size_hint_y = None
        self.height = 50
        self.background_normal = ''
        self.background_color = Theme.PRIMARY_MAIN if not is_premium else Theme.BROWN_MAIN
        self.color = Theme.TEXT_LIGHT
        self.halign = 'left'
        self.valign = 'middle'
        self.bind(size=self._update_size)

    def _update_size(self, instance, value):
        self.text_size = (self.width - 20, None)
