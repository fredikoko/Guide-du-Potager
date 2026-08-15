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
from ..components.navigation_drawer import NavigationDrawer

class ToolsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glossary_service = GlossaryService()
        self.drawer = None

        with self.canvas.before:
            Color(*Theme.BG_CREAM)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        layout = BoxLayout(orientation='vertical')

        # Header
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
            text="[b]Outils Maraîchers[/b]", markup=True, font_size='18sp',
            color=Theme.TEXT_LIGHT, halign='left', valign='middle'
        )
        title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

        header.add_widget(menu_btn)
        header.add_widget(title)
        layout.add_widget(header)

        # Search Bar
        search_box = BoxLayout(size_hint_y=None, height=55, padding=[15, 8, 15, 0])
        search_bar = SearchBar(on_search_callback=self.filter_tools, placeholder="Chercher un outil...")
        search_box.add_widget(search_bar)
        layout.add_widget(search_box)

        # Scrollable Tools List
        scroll = ScrollView()
        self.tools_container = BoxLayout(orientation='vertical', size_hint_y=None, padding=15, spacing=15)
        self.tools_container.bind(minimum_height=self.tools_container.setter('height'))
        scroll.add_widget(self.tools_container)

        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self):
        self.load_tools()

    def filter_tools(self, query):
        self.load_tools(search=query)

    def load_tools(self, search=None):
        self.tools_container.clear_widgets()
        res = self.glossary_service.get_tools(search=search)

        if not res.get('success'):
            err = Label(text="⚠️ Impossible de charger les outils.", color=Theme.TEXT_MUTED, font_size='16sp', size_hint_y=None, height=50)
            self.tools_container.add_widget(err)
            return

        tools = res.get('data', [])
        for tool in tools:
            card = CardWidget(bg_color=Theme.CARD_BG)

            badge = " ⭐ Premium" if tool.get('is_premium') else ""
            t_title = Label(
                text=f"[b]🛠️ {tool['name']}[/b][color=E8AB26]{badge}[/color]",
                markup=True, font_size='17sp', color=Theme.PRIMARY_DARK,
                size_hint_y=None, height=35, halign='left', valign='middle'
            )
            t_title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

            t_desc = Label(
                text=tool['description'],
                color=Theme.TEXT_DARK, font_size='14sp', size_hint_y=None, halign='left', valign='top'
            )
            t_desc.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
            t_desc.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))

            card.add_widget(t_title)
            card.add_widget(t_desc)

            if tool.get('usage_tips'):
                tips = Label(
                    text=f"[b]💡 Conseils d'utilisation :[/b] {tool['usage_tips']}",
                    markup=True, color=Theme.PRIMARY_MAIN, font_size='13sp', size_hint_y=None, halign='left', valign='top'
                )
                tips.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                tips.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
                card.add_widget(tips)

            self.tools_container.add_widget(card)

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
