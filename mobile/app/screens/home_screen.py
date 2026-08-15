from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from ..styles.themes import Theme
from ..services.content_service import ContentService
from ..components.cards import PartHeaderLabel, ChapterButton, CardWidget
from ..components.navigation_drawer import NavigationDrawer

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_service = ContentService()
        self.drawer = None

        with self.canvas.before:
            Color(*Theme.BG_CREAM)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.root_layout = BoxLayout(orientation='vertical')

        # Top App Bar with Menu Hamburger Button
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, padding=[10, 5, 10, 5], spacing=10)
        with header.canvas.before:
            Color(*Theme.HEADER_BG)
            self.header_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=self._update_header_rect, pos=self._update_header_rect)

        menu_btn = Button(
            text="☰",
            font_size='22sp',
            size_hint_x=None,
            width=50,
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=Theme.TEXT_LIGHT
        )
        menu_btn.bind(on_release=self.toggle_drawer)

        app_title = Label(
            text="[b]Guide du Potager[/b]",
            markup=True,
            font_size='20sp',
            color=Theme.TEXT_LIGHT,
            halign='left',
            valign='middle'
        )
        app_title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

        profile_icon = Button(
            text="👤",
            font_size='20sp',
            size_hint_x=None,
            width=50,
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=Theme.TEXT_LIGHT
        )
        profile_icon.bind(on_release=lambda x: setattr(self.manager, 'current', 'profile'))

        header.add_widget(menu_btn)
        header.add_widget(app_title)
        header.add_widget(profile_icon)
        self.root_layout.add_widget(header)

        # Content Scroll Area
        self.scroll = ScrollView()
        self.content_container = BoxLayout(orientation='vertical', size_hint_y=None, padding=15, spacing=15)
        self.content_container.bind(minimum_height=self.content_container.setter('height'))
        self.scroll.add_widget(self.content_container)

        self.root_layout.add_widget(self.scroll)
        self.add_widget(self.root_layout)

    def on_enter(self):
        self.load_parts_and_chapters()

    def load_parts_and_chapters(self):
        self.content_container.clear_widgets()
        res = self.content_service.get_parts()

        if not res.get('success'):
            err_label = Label(
                text="⚠️ Impossible de charger le contenu.\nVérifiez votre connexion internet.",
                color=Theme.TEXT_MUTED, font_size='16sp', size_hint_y=None, height=100
            )
            self.content_container.add_widget(err_label)
            return

        parts = res.get('data', [])

        for part in parts:
            part_card = CardWidget(bg_color=Theme.CARD_BG)

            # Header Label for Part (Non-clickable)
            part_label = PartHeaderLabel(title=part['title'], is_premium=part.get('is_premium', False))
            part_card.add_widget(part_label)

            if part.get('description'):
                desc = Label(
                    text=part['description'],
                    color=Theme.TEXT_MUTED,
                    font_size='13sp',
                    size_hint_y=None,
                    height=35,
                    halign='left',
                    valign='middle'
                )
                desc.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
                part_card.add_widget(desc)

            # Chapters List as clickable buttons
            for chapter in part.get('chapters', []):
                chap_btn = ChapterButton(
                    title=chapter['title'],
                    is_premium=chapter.get('is_premium', False),
                    reading_time=chapter.get('estimated_reading_time', 5)
                )
                chap_id = chapter['id']
                chap_btn.bind(on_release=lambda instance, cid=chap_id: self.open_chapter(cid))
                part_card.add_widget(chap_btn)

            self.content_container.add_widget(part_card)

    def open_chapter(self, chapter_id):
        chapter_screen = self.manager.get_screen('chapter')
        chapter_screen.load_chapter(chapter_id)
        self.manager.current = 'chapter'

    def toggle_drawer(self, instance):
        if not self.drawer:
            self.drawer = NavigationDrawer(
                screen_manager=self.manager,
                logout_callback=self.handle_logout
            )
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
