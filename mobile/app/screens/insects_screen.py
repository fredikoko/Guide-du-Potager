from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from ..styles.themes import Theme
from ..services.pest_service import PestService
from ..components.cards import CardWidget
from ..components.search_bar import SearchBar
from ..components.navigation_drawer import NavigationDrawer

class InsectsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pest_service = PestService()
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
            text="≡", font_size='26sp', size_hint_x=None, width=50,
            background_normal='', background_color=(0, 0, 0, 0), color=Theme.TEXT_LIGHT
        )
        menu_btn.bind(on_release=self.toggle_drawer)

        title = Label(
            text="[b]Insectes Nuisibles[/b]", markup=True, font_size='18sp',
            color=Theme.TEXT_LIGHT, halign='left', valign='middle'
        )
        title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

        header.add_widget(menu_btn)
        header.add_widget(title)
        layout.add_widget(header)

        # Search bar
        search_box = BoxLayout(size_hint_y=None, height=55, padding=[15, 8, 15, 0])
        search_bar = SearchBar(on_search_callback=self.filter_insects, placeholder="Chercher un insecte...")
        search_box.add_widget(search_bar)
        layout.add_widget(search_box)

        scroll = ScrollView()
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, padding=15, spacing=15)
        self.container.bind(minimum_height=self.container.setter('height'))
        scroll.add_widget(self.container)

        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self):
        self.load_insects()

    def filter_insects(self, query):
        self.load_insects(search=query)

    def load_insects(self, search=None):
        self.container.clear_widgets()
        res = self.pest_service.get_insects(search=search)

        if not res.get('success'):
            err = Label(text="⚠️ Erreur de chargement.", color=Theme.TEXT_MUTED, font_size='16sp', size_hint_y=None, height=50)
            self.container.add_widget(err)
            return

        insects = res.get('data', [])
        for insect in insects:
            card = CardWidget(bg_color=Theme.CARD_BG)

            badge = " [★ Premium]" if insect.get('is_premium') else ""
            i_title = Label(
                text=f"[b]◆ {insect['name']}[/b][color=E8AB26]{badge}[/color]",
                markup=True, font_size='17sp', color=Theme.PRIMARY_DARK,
                size_hint_y=None, height=35, halign='left', valign='middle'
            )
            i_title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

            desc = Label(
                text=f"[b]▸ Description :[/b] {insect.get('description', '')}",
                markup=True, color=Theme.TEXT_DARK, font_size='14sp', size_hint_y=None, halign='left', valign='top'
            )
            desc.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
            desc.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))

            damage = Label(
                text=f"[b]⚠ Dégâts :[/b] {insect.get('damage', '')}",
                markup=True, color=(0.8, 0.3, 0.2, 1), font_size='14sp', size_hint_y=None, halign='left', valign='top'
            )
            damage.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
            damage.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))

            sol = Label(
                text=f"[b]✓ Solution Bio / Traitement :[/b] {insect.get('solution', '')}",
                markup=True, color=Theme.PRIMARY_MAIN, font_size='14sp', size_hint_y=None, halign='left', valign='top'
            )
            sol.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
            sol.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))

            card.add_widget(i_title)
            card.add_widget(desc)
            card.add_widget(damage)
            card.add_widget(sol)

            self.container.add_widget(card)

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
