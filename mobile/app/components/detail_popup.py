from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, RoundedRectangle
from ..styles.themes import Theme

class DetailPopup(Popup):
    def __init__(self, title_text, image_url=None, fields=[], is_locked=False, upgrade_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.title = title_text
        self.title_size = '18sp'
        self.title_color = Theme.TEXT_LIGHT
        self.background_color = (0.1, 0.22, 0.13, 0.95)
        self.size_hint = (0.92, 0.88)
        self.auto_dismiss = True

        main_layout = BoxLayout(orientation='vertical', padding=14, spacing=10)

        # Light cream card background for the main content area
        with main_layout.canvas.before:
            Color(*Theme.BG_CREAM)
            self.rect = RoundedRectangle(size=main_layout.size, pos=main_layout.pos, radius=[8, 8, 8, 8])
        main_layout.bind(size=self._update_rect, pos=self._update_rect)

        scroll = ScrollView()
        content_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=14, padding=[6, 6, 6, 6])
        content_box.bind(minimum_height=content_box.setter('height'))

        # Render Image if available
        if image_url:
            img = AsyncImage(
                source=image_url,
                size_hint_y=None,
                height=180
            )
            content_box.add_widget(img)

        # Render detail fields (key, value, color)
        for field in fields:
            label_title = field[0]
            text_val = field[1]
            title_color = field[2] if len(field) > 2 and field[2] else Theme.PRIMARY_DARK

            if text_val:
                # Section title in bold with header color
                title_lbl = Label(
                    text=f"[b]{label_title} :[/b]",
                    markup=True,
                    color=title_color,
                    font_size='16sp',
                    size_hint_y=None,
                    height=26,
                    halign='left',
                    valign='middle'
                )
                title_lbl.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
                content_box.add_widget(title_lbl)

                # Section body in dark text on light cream background
                val_lbl = Label(
                    text=text_val,
                    markup=True,
                    color=Theme.TEXT_DARK,
                    font_size='15sp',
                    size_hint_y=None,
                    halign='left',
                    valign='top'
                )
                val_lbl.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                val_lbl.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
                content_box.add_widget(val_lbl)

        # Upgrade button if premium locked
        if is_locked and upgrade_callback:
            up_btn = Button(
                text="★ Débloquer avec l'Abonnement Premium",
                font_size='15sp',
                size_hint_y=None,
                height=48,
                background_normal='',
                background_color=Theme.GOLD_PREMIUM,
                color=Theme.TEXT_LIGHT
            )
            up_btn.bind(on_release=lambda x: (self.dismiss(), upgrade_callback()))
            content_box.add_widget(up_btn)

        scroll.add_widget(content_box)
        main_layout.add_widget(scroll)

        # Close Button
        close_btn = Button(
            text="Fermer",
            font_size='16sp',
            size_hint_y=None,
            height=44,
            background_normal='',
            background_color=Theme.PRIMARY_MAIN,
            color=Theme.TEXT_LIGHT
        )
        close_btn.bind(on_release=self.dismiss)
        main_layout.add_widget(close_btn)

        self.content = main_layout

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
