from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, Rectangle
from ..styles.themes import Theme
from ..services.glossary_service import GlossaryService
from ..components.cards import CardWidget
from ..components.search_bar import SearchBar
from ..components.navigation_drawer import NavigationDrawer
from ..components.detail_popup import DetailPopup
from ..utils.config import Config

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
            text="MENU", font_size='13sp', size_hint_x=None, width=60,
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

        base_root = Config.API_BASE_URL.replace('/api', '')
        tools = res.get('data', [])

        for tool in tools:
            card = CardWidget(bg_color=Theme.CARD_BG)

            badge = " [PREMIUM]" if tool.get('is_premium') else ""
            t_title = Label(
                text=f"[b]{tool['name']}[/b][color=E8AB26]{badge}[/color]",
                markup=True, font_size='17sp', color=Theme.PRIMARY_DARK,
                size_hint_y=None, height=35, halign='left', valign='middle'
            )
            t_title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
            card.add_widget(t_title)

            # Image in list item
            img_url = tool.get('image')
            if img_url:
                if img_url.startswith('/'):
                    img_url = f"{base_root}{img_url}"
                img_widget = AsyncImage(
                    source=img_url,
                    size_hint_y=None,
                    height=140
                )
                card.add_widget(img_widget)

            t_desc = Label(
                text=tool['description'][:110] + ("..." if len(tool['description']) > 110 else ""),
                color=Theme.TEXT_DARK, font_size='14sp', size_hint_y=None, height=45, halign='left', valign='top'
            )
            t_desc.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
            card.add_widget(t_desc)

            # Details Button
            tool_item = tool
            detail_btn = Button(
                text="Voir les détails →",
                font_size='14sp',
                size_hint_y=None,
                height=42,
                background_normal='',
                background_color=Theme.PRIMARY_MAIN,
                color=Theme.TEXT_LIGHT
            )
            detail_btn.bind(on_release=lambda instance, t=tool_item, i_url=img_url: self.open_tool_detail(t, i_url))
            card.add_widget(detail_btn)

            self.tools_container.add_widget(card)

    def open_tool_detail(self, tool, image_url):
        fields = [
            ("Catégorie", tool.get('category', '').replace('_', ' ').title(), Theme.BROWN_MAIN),
            ("Description", tool.get('description', ''), Theme.TEXT_DARK),
            ("Conseils d'utilisation", tool.get('usage_tips', ''), Theme.PRIMARY_MAIN),
        ]
        if tool.get('tropical_tips'):
            fields.append(("Spécificités en climat tropical", tool.get('tropical_tips'), Theme.PRIMARY_DARK))

        popup = DetailPopup(
            title_text=tool['name'],
            image_url=image_url,
            fields=fields
        )
        popup.open()

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
