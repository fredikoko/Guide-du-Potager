from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from ..styles.themes import Theme

class DrawerButton(Button):
    def __init__(self, text, symbol="●", **kwargs):
        super().__init__(**kwargs)
        self.text = f"  {symbol}   {text}"
        self.font_size = '15sp'
        self.size_hint_y = None
        self.height = 52
        self.background_normal = ''
        self.background_color = Theme.PRIMARY_MAIN
        self.color = Theme.TEXT_LIGHT
        self.halign = 'left'
        self.valign = 'middle'
        self.text_size = (220, None)

class NavigationDrawer(BoxLayout):
    def __init__(self, screen_manager, logout_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_x = None
        self.width = 260
        self.screen_manager = screen_manager
        self.logout_callback = logout_callback

        # Draw Background
        with self.canvas.before:
            Color(*Theme.PRIMARY_DARK)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Header Section
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=110, padding=15, spacing=5)
        with header.canvas.before:
            Color(*Theme.BROWN_DARK)
            self.header_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=self._update_header_rect, pos=self._update_header_rect)

        app_title = Label(
            text="[b]Guide du Potager[/b]",
            markup=True,
            font_size='20sp',
            color=Theme.TEXT_LIGHT,
            halign='left'
        )
        app_subtitle = Label(
            text="Botanique & Maraîchage Bio",
            font_size='13sp',
            color=Theme.PRIMARY_LIGHT,
            halign='left'
        )
        header.add_widget(app_title)
        header.add_widget(app_subtitle)
        self.add_widget(header)

        # Scrollable Menu Items
        scroll = ScrollView()
        menu_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=2, padding=[0, 10, 0, 10])
        menu_box.bind(minimum_height=menu_box.setter('height'))

        items = [
            ("Accueil", "home", "⌂"),
            ("Outils Maraîchers", "tools", "⚙"),
            ("Familles Botaniques", "families", "☘"),
            ("Maladies & Soins", "diseases", "✚"),
            ("Insectes Nuisibles", "insects", "◆"),
            ("Mon Profil", "profile", "👤"),
            ("Abonnement Premium", "subscription", "★"),
        ]

        for title, screen_name, symbol in items:
            btn = DrawerButton(text=title, symbol=symbol)
            btn.bind(on_release=lambda instance, s=screen_name: self.navigate(s))
            menu_box.add_widget(btn)

        scroll.add_widget(menu_box)
        self.add_widget(scroll)

        # Logout Footer
        logout_btn = DrawerButton(text="Déconnexion", symbol="⎋")
        logout_btn.background_color = Theme.BROWN_MAIN
        logout_btn.bind(on_release=lambda x: self.logout_callback())
        self.add_widget(logout_btn)

    def navigate(self, screen_name):
        if self.screen_manager:
            self.screen_manager.current = screen_name

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
