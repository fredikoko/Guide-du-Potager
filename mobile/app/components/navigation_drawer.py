from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from ..styles.themes import Theme

class DrawerButton(Button):
    def __init__(self, text, prefix="•", **kwargs):
        super().__init__(**kwargs)
        self.text = f"  {prefix}  {text}"
        self.font_size = '15sp'
        self.size_hint_y = None
        self.height = 50
        self.background_normal = ''
        self.background_color = Theme.PRIMARY_MAIN
        self.color = Theme.TEXT_LIGHT
        self.halign = 'left'
        self.valign = 'middle'
        self.text_size = (240, None)

class NavigationDrawer(FloatLayout):
    def __init__(self, screen_manager, logout_callback, close_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.screen_manager = screen_manager
        self.logout_callback = logout_callback
        self.close_callback = close_callback

        # Semi-transparent dark backdrop overlay covering the whole screen
        with self.canvas.before:
            Color(0, 0, 0, 0.45)
            self.backdrop_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_backdrop, pos=self._update_backdrop)

        # Drawer Left Panel
        self.panel = BoxLayout(
            orientation='vertical',
            size_hint=(None, 1),
            width=270,
            pos_hint={'x': 0, 'y': 0}
        )
        with self.panel.canvas.before:
            Color(*Theme.PRIMARY_DARK)
            self.panel_rect = Rectangle(size=self.panel.size, pos=self.panel.pos)
        self.panel.bind(size=self._update_panel_rect, pos=self._update_panel_rect)

        # Header Section with Close Button
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=100,
            padding=[14, 10, 10, 10],
            spacing=6
        )
        with header.canvas.before:
            Color(*Theme.BROWN_DARK)
            self.header_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=self._update_header_rect, pos=self._update_header_rect)

        title_box = BoxLayout(orientation='vertical', spacing=2)
        app_title = Label(
            text="[b]🌿 Guide du Potager[/b]\n[size=13sp][color=47C26B]Tropical & Sahélien[/color][/size]",
            markup=True,
            font_size='16sp',
            color=Theme.TEXT_LIGHT,
            halign='left',
            valign='middle'
        )
        app_title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

        app_subtitle = Label(
            text="Conventionnel, Raisonné & Bio",
            font_size='11sp',
            color=Theme.PRIMARY_LIGHT,
            halign='left',
            valign='middle',
            size_hint_y=None,
            height=18
        )
        app_subtitle.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

        title_box.add_widget(app_title)
        title_box.add_widget(app_subtitle)

        close_btn = Button(
            text="✕",
            font_size='18sp',
            size_hint=(None, None),
            size=(36, 36),
            pos_hint={'top': 1},
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=Theme.TEXT_LIGHT
        )
        close_btn.bind(on_release=lambda x: self.close())

        header.add_widget(title_box)
        header.add_widget(close_btn)
        self.panel.add_widget(header)

        # Scrollable Menu Items
        scroll = ScrollView()
        menu_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=2, padding=[0, 8, 0, 8])
        menu_box.bind(minimum_height=menu_box.setter('height'))

        items = [
            ("Accueil & Manuel", "home", "🏠"),
            ("Simulateur Calendrier", "calendar", "📅"),
            ("Fiches Légumes", "vegetables", "🥕"),
            ("Familles Botaniques", "families", "🌱"),
            ("Outils Maraîchers", "tools", "🛠️"),
            ("Maladies & Soins", "diseases", "🩺"),
            ("Insectes & Biocontrôle", "insects", "🐛"),
            ("Blog & Actualités", "blog", "📰"),
            ("Pass & Abonnement", "subscription", "⭐"),
            ("Mon Profil", "profile", "👤"),
            ("À Propos du Guide", "about", "ℹ️"),
        ]

        for title, screen_name, prefix in items:
            btn = DrawerButton(text=title, prefix=prefix)
            if screen_name == "subscription":
                btn.background_color = Theme.ACCENT_EXCLUSIVE
            btn.bind(on_release=lambda instance, s=screen_name: self.navigate(s))
            menu_box.add_widget(btn)

        scroll.add_widget(menu_box)
        self.panel.add_widget(scroll)

        # Logout Footer
        logout_btn = DrawerButton(text="Déconnexion", prefix="🚪")
        logout_btn.background_color = Theme.BROWN_MAIN
        logout_btn.bind(on_release=lambda x: self._on_logout())
        self.panel.add_widget(logout_btn)

        self.add_widget(self.panel)

    def close(self):
        if self.close_callback:
            self.close_callback()
        elif self.parent:
            parent = self.parent
            if hasattr(parent, 'drawer') and parent.drawer is self:
                parent.drawer = None
            parent.remove_widget(self)

    def navigate(self, screen_name):
        self.close()
        if self.screen_manager:
            self.screen_manager.current = screen_name

    def _on_logout(self):
        self.close()
        if self.logout_callback:
            self.logout_callback()

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        if self.panel.collide_point(*touch.pos):
            super().on_touch_down(touch)
            return True
        # Touch outside panel (on backdrop) -> auto close and consume touch
        self.close()
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is not None:
            return super().on_touch_move(touch)
        if self.collide_point(*touch.pos):
            super().on_touch_move(touch)
            return True
        return False

    def on_touch_up(self, touch):
        if touch.grab_current is not None:
            return super().on_touch_up(touch)
        if self.collide_point(*touch.pos):
            super().on_touch_up(touch)
            return True
        return False

    def _update_backdrop(self, instance, value):
        self.backdrop_rect.pos = instance.pos
        self.backdrop_rect.size = instance.size

    def _update_panel_rect(self, instance, value):
        self.panel_rect.pos = instance.pos
        self.panel_rect.size = instance.size

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
