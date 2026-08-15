from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from ..styles.themes import Theme
from ..services.glossary_service import GlossaryService
from ..components.cards import CardWidget
from ..components.navigation_drawer import NavigationDrawer

class FamiliesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glossary_service = GlossaryService()
        self.drawer = None

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

        menu_btn = Button(
            text="☰", font_size='22sp', size_hint_x=None, width=50,
            background_normal='', background_color=(0, 0, 0, 0), color=Theme.TEXT_LIGHT
        )
        menu_btn.bind(on_release=self.toggle_drawer)

        title = Label(
            text="[b]Familles Botaniques[/b]", markup=True, font_size='18sp',
            color=Theme.TEXT_LIGHT, halign='left', valign='middle'
        )
        title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

        header.add_widget(menu_btn)
        header.add_widget(title)
        layout.add_widget(header)

        scroll = ScrollView()
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, padding=15, spacing=15)
        self.container.bind(minimum_height=self.container.setter('height'))
        scroll.add_widget(self.container)

        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self):
        self.load_families()

    def load_families(self):
        self.container.clear_widgets()
        res = self.glossary_service.get_families()

        if not res.get('success'):
            err = Label(text="⚠️ Erreur de chargement.", color=Theme.TEXT_MUTED, font_size='16sp', size_hint_y=None, height=50)
            self.container.add_widget(err)
            return

        families = res.get('data', [])
        for family in families:
            card = CardWidget(bg_color=Theme.CARD_BG)

            f_title = Label(
                text=f"[b]🌱 {family['name']}[/b]",
                markup=True, font_size='18sp', color=Theme.PRIMARY_DARK,
                size_hint_y=None, height=35, halign='left', valign='middle'
            )
            f_title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

            f_desc = Label(
                text=family['description'],
                color=Theme.TEXT_DARK, font_size='14sp', size_hint_y=None, halign='left', valign='top'
            )
            f_desc.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
            f_desc.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))

            card.add_widget(f_title)
            card.add_widget(f_desc)

            # Button to filter vegetables for this family
            fid = family['id']
            fname = family['name']
            veg_btn = Button(
                text=f"Voir les légumes de la famille ({len(family.get('vegetables', []))}) →",
                font_size='14sp', size_hint_y=None, height=44,
                background_normal='', background_color=Theme.PRIMARY_MAIN, color=Theme.TEXT_LIGHT
            )
            veg_btn.bind(on_release=lambda instance, fid=fid, fname=fname: self.open_vegetables(fid, fname))
            card.add_widget(veg_btn)

            self.container.add_widget(card)

    def open_vegetables(self, family_id, family_name):
        veg_screen = self.manager.get_screen('vegetables')
        veg_screen.load_vegetables(family_id=family_id, family_name=family_name)
        self.manager.current = 'vegetables'

    def toggle_drawer(self, instance):
        if not self.drawer:
            self.drawer = NavigationDrawer(screen_manager=self.manager, logout_callback=self.handle_logout)
            self.add_widget(self.drawer)
        else:
            self.remove_widget(self.drawer)
            self.drawer = None

    def handle_logout(self):
        from ..services.auth_service import AuthService
        AuthService().logout()
        if self.drawer:
            self.remove_widget(self.drawer)
            self.drawer = None
        self.manager.current = 'login'

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
