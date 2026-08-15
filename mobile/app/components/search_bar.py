from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from ..styles.themes import Theme

class SearchBar(BoxLayout):
    def __init__(self, on_search_callback=None, placeholder="Rechercher...", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 45
        self.spacing = 5

        self.input_field = TextInput(
            hint_text=placeholder,
            multiline=False,
            font_size='15sp',
            background_normal='',
            background_color=(1, 1, 1, 1),
            foreground_color=Theme.TEXT_DARK,
            padding=[10, 10, 10, 10]
        )

        search_btn = Button(
            text="Chercher",
            font_size='13sp',
            size_hint_x=None,
            width=80,
            background_normal='',
            background_color=Theme.PRIMARY_MAIN,
            color=Theme.TEXT_LIGHT
        )

        if on_search_callback:
            search_btn.bind(on_release=lambda x: on_search_callback(self.input_field.text))
            self.input_field.bind(on_text_validate=lambda x: on_search_callback(self.input_field.text))

        self.add_widget(self.input_field)
        self.add_widget(search_btn)
