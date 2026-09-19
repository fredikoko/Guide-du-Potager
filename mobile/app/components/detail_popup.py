from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from ..styles.themes import Theme

class DetailPopup(Popup):
    def __init__(self, title_text, image_url=None, fields=[], is_locked=False, upgrade_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.title = title_text
        self.title_size = '18sp'
        self.title_color = Theme.TEXT_LIGHT
        self.background_color = (0.1, 0.2, 0.12, 0.95)
        self.size_hint = (0.9, 0.85)
        self.auto_dismiss = True

        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        scroll = ScrollView()
        content_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=12)
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
        for label_title, text_val, text_color in fields:
            if text_val:
                lbl = Label(
                    text=f"[b]{label_title} :[/b]\n{text_val}",
                    markup=True,
                    color=text_color or Theme.TEXT_DARK,
                    font_size='15sp',
                    size_hint_y=None,
                    halign='left',
                    valign='top'
                )
                lbl.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                lbl.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
                content_box.add_widget(lbl)

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
