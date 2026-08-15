from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from ..styles.themes import Theme
from ..services.glossary_service import GlossaryService
from ..components.cards import CardWidget
from ..components.search_bar import SearchBar

class VegetablesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glossary_service = GlossaryService()
        self.current_family_id = None

        with self.canvas.before:
            Color(*Theme.BG_CREAM)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        layout = BoxLayout(orientation='vertical')

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, padding=10, spacing=10)
        with header.canvas.before:
            Color(*Theme.HEADER_BG)
            self.header_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=self._update_header_rect, pos=self._update_header_rect)

        back_btn = Button(
            text="← Retour", font_size='16sp', size_hint_x=None, width=90,
            background_normal='', background_color=(0, 0, 0, 0), color=Theme.TEXT_LIGHT
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'families'))

        self.title_label = Label(
            text="[b]Fiches Légumes[/b]", markup=True, font_size='18sp',
            color=Theme.TEXT_LIGHT, halign='left', valign='middle'
        )
        self.title_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

        header.add_widget(back_btn)
        header.add_widget(self.title_label)
        layout.add_widget(header)

        # Search bar
        search_box = BoxLayout(size_hint_y=None, height=55, padding=[15, 8, 15, 0])
        search_bar = SearchBar(on_search_callback=self.filter_vegetables, placeholder="Chercher un me légume...")
        search_box.add_widget(search_bar)
        layout.add_widget(search_box)

        scroll = ScrollView()
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, padding=15, spacing=15)
        self.container.bind(minimum_height=self.container.setter('height'))
        scroll.add_widget(self.container)

        layout.add_widget(scroll)
        self.add_widget(layout)

    def filter_vegetables(self, query):
        self.load_vegetables(family_id=self.current_family_id, search=query)

    def load_vegetables(self, family_id=None, family_name=None, search=None):
        self.current_family_id = family_id
        if family_name:
            self.title_label.text = f"[b]Légumes : {family_name}[/b]"

        self.container.clear_widgets()
        res = self.glossary_service.get_vegetables(family_id=family_id, search=search)

        if not res.get('success'):
            err = Label(text="⚠️ Erreur de chargement des légumes.", color=Theme.TEXT_MUTED, font_size='16sp', size_hint_y=None, height=50)
            self.container.add_widget(err)
            return

        vegetables = res.get('data', [])
        for veg in vegetables:
            card = CardWidget(bg_color=Theme.CARD_BG)

            v_title = Label(
                text=f"[b]🥬 {veg['name']}[/b] [i]({veg.get('scientific_name', '')})[/i]",
                markup=True, font_size='17sp', color=Theme.PRIMARY_DARK,
                size_hint_y=None, height=35, halign='left', valign='middle'
            )
            v_title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

            sow = Label(
                text=f"[b]🌱 Semis :[/b] {veg.get('sowing_period', 'N/A')}",
                markup=True, color=Theme.TEXT_DARK, font_size='14sp', size_hint_y=None, height=25, halign='left'
            )
            sow.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

            harvest = Label(
                text=f"[b]🧺 Récolte :[/b] {veg.get('harvest_period', 'N/A')}",
                markup=True, color=Theme.BROWN_MAIN, font_size='14sp', size_hint_y=None, height=25, halign='left'
            )
            harvest.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

            tips = Label(
                text=f"[b]💚 Soins & Entretien :[/b]\n{veg.get('care_tips', '')}",
                markup=True, color=Theme.TEXT_DARK, font_size='14sp', size_hint_y=None, halign='left', valign='top'
            )
            tips.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
            tips.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))

            card.add_widget(v_title)
            card.add_widget(sow)
            card.add_widget(harvest)
            card.add_widget(tips)

            self.container.add_widget(card)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
