from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, Rectangle
from ..styles.themes import Theme
from ..services.glossary_service import GlossaryService
from ..services.auth_service import AuthService
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

        # Category Horizontal Filter
        cat_scroll = ScrollView(size_hint_y=None, height=48, do_scroll_y=False)
        self.cat_box = BoxLayout(size_hint_x=None, height=42, padding=[10, 3, 10, 3], spacing=8)
        self.cat_box.bind(minimum_width=self.cat_box.setter('width'))
        cat_scroll.add_widget(self.cat_box)
        layout.add_widget(cat_scroll)

        # Scrollable Tools List
        scroll = ScrollView()
        self.tools_container = BoxLayout(orientation='vertical', size_hint_y=None, padding=15, spacing=15)
        self.tools_container.bind(minimum_height=self.tools_container.setter('height'))
        scroll.add_widget(self.tools_container)

        layout.add_widget(scroll)
        self.add_widget(layout)

        self.selected_category = None
        self.search_query = None

    def on_enter(self):
        self.render_categories()
        self.load_tools()

    def render_categories(self):
        self.cat_box.clear_widgets()
        tool_cats = [
            (None, "Tous les outils"),
            ("travail_sol", "Travail du Sol"),
            ("semis_plantation", "Semis & Plantation"),
            ("entretien", "Entretien"),
            ("irrigation", "Irrigation"),
            ("recolte", "Récolte"),
        ]
        for cat_code, cat_label in tool_cats:
            is_active = (self.selected_category == cat_code)
            btn = Button(
                text=cat_label,
                size_hint=(None, None),
                size=(max(len(cat_label) * 8 + 24, 90), 34),
                font_size='12sp',
                background_normal='',
                background_color=Theme.PRIMARY_DARK if is_active else (0.85, 0.88, 0.85, 1.0),
                color=Theme.TEXT_LIGHT if is_active else Theme.TEXT_DARK
            )
            btn.bind(on_release=lambda instance, code=cat_code: self.select_category(code))
            self.cat_box.add_widget(btn)

    def select_category(self, cat_code):
        self.selected_category = cat_code
        self.render_categories()
        self.load_tools(category=cat_code, search=self.search_query)

    def filter_tools(self, query):
        self.search_query = query
        self.load_tools(category=self.selected_category, search=query)

    def load_tools(self, category=None, search=None):
        self.tools_container.clear_widgets()
        res = self.glossary_service.get_tools(category=category, search=search)

        if not res.get('success'):
            err = Label(text="⚠️ Impossible de charger les outils.", color=Theme.TEXT_MUTED, font_size='16sp', size_hint_y=None, height=50)
            self.tools_container.add_widget(err)
            return

        base_root = Config.API_BASE_URL.replace('/api', '')
        tools = res.get('data', [])

        for tool in tools:
            card = CardWidget(bg_color=Theme.CARD_BG)
            is_prem = bool(tool.get('is_premium'))

            title_txt = f"[b]{tool['name']}[/b]" + (" [color=47C26B]★[/color]" if is_prem else "")
            t_title = Label(
                text=title_txt,
                markup=True, font_size='17sp',
                color=Theme.ACCENT_EXCLUSIVE if is_prem else Theme.PRIMARY_DARK,
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
                background_color=Theme.ACCENT_EXCLUSIVE if is_prem else Theme.PRIMARY_MAIN,
                color=Theme.TEXT_LIGHT
            )
            detail_btn.bind(on_release=lambda instance, t=tool_item, i_url=img_url: self.open_tool_detail(t, i_url))
            card.add_widget(detail_btn)

            self.tools_container.add_widget(card)

    def open_tool_detail(self, tool, image_url):
        tool_id = tool.get('id')
        res = self.glossary_service.get_tool_detail(tool_id) if tool_id else None
        data = res['data'] if (res and res.get('success')) else tool

        is_prem = bool(data.get('is_premium'))
        is_sub = AuthService().is_subscribed()
        is_locked = data.get('is_locked', False) or (is_prem and not is_sub)

        category_txt = data.get('category_display') or data.get('category', '').replace('_', ' ').title()

        if is_locked:
            fields = [
                ("Catégorie", category_txt, Theme.BROWN_MAIN),
                ("Description", "🔒 Cette fiche outil spécialisée et ses techniques d'utilisation sont réservées aux abonnés.", Theme.TEXT_MUTED),
            ]
        else:
            fields = [
                ("Catégorie", category_txt, Theme.BROWN_MAIN),
                ("Description", data.get('description', ''), Theme.TEXT_DARK),
                ("Conseils d'utilisation", data.get('usage_tips', ''), Theme.PRIMARY_MAIN),
            ]
            if data.get('tropical_tips'):
                fields.append(("Spécificités en climat tropical", data.get('tropical_tips'), Theme.PRIMARY_DARK))

        popup = DetailPopup(
            title_text=data['name'],
            image_url=image_url,
            fields=fields,
            is_locked=is_locked,
            upgrade_callback=lambda: setattr(self.manager, 'current', 'subscription')
        )
        popup.open()

    def toggle_drawer(self, instance=None):
        if not self.drawer:
            self.drawer = NavigationDrawer(
                screen_manager=self.manager,
                logout_callback=self.handle_logout,
                close_callback=self.close_drawer
            )
            self.add_widget(self.drawer)
        else:
            self.close_drawer()

    def close_drawer(self):
        if self.drawer:
            if self.drawer.parent:
                self.drawer.parent.remove_widget(self.drawer)
            self.drawer = None

    def on_leave(self):
        self.close_drawer()

    def handle_logout(self):
        from ..services.auth_service import AuthService
        AuthService().logout()
        self.close_drawer()
        self.manager.current = 'login'

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
