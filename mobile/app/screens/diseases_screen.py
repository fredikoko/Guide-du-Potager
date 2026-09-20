from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, Rectangle
from ..styles.themes import Theme
from ..services.pest_service import PestService
from ..components.cards import CardWidget
from ..components.search_bar import SearchBar
from ..components.navigation_drawer import NavigationDrawer
from ..components.detail_popup import DetailPopup
from ..utils.config import Config

class DiseasesScreen(Screen):
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
            text="MENU", font_size='13sp', size_hint_x=None, width=60,
            background_normal='', background_color=(0, 0, 0, 0), color=Theme.TEXT_LIGHT
        )
        menu_btn.bind(on_release=self.toggle_drawer)

        title = Label(
            text="[b]Maladies & Soins[/b]", markup=True, font_size='18sp',
            color=Theme.TEXT_LIGHT, halign='left', valign='middle'
        )
        title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

        header.add_widget(menu_btn)
        header.add_widget(title)
        layout.add_widget(header)

        # Search bar
        search_box = BoxLayout(size_hint_y=None, height=55, padding=[15, 8, 15, 0])
        search_bar = SearchBar(on_search_callback=self.filter_diseases, placeholder="Chercher une maladie...")
        search_box.add_widget(search_bar)
        layout.add_widget(search_box)

        scroll = ScrollView()
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, padding=15, spacing=15)
        self.container.bind(minimum_height=self.container.setter('height'))
        scroll.add_widget(self.container)

        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self):
        self.load_diseases()

    def filter_diseases(self, query):
        self.load_diseases(search=query)

    def load_diseases(self, search=None):
        self.container.clear_widgets()
        res = self.pest_service.get_diseases(search=search)

        if not res.get('success'):
            err = Label(text="⚠️ Erreur de chargement.", color=Theme.TEXT_MUTED, font_size='16sp', size_hint_y=None, height=50)
            self.container.add_widget(err)
            return

        base_root = Config.API_BASE_URL.replace('/api', '')
        diseases = res.get('data', [])

        for disease in diseases:
            card = CardWidget(bg_color=Theme.CARD_BG)

            badge = " [PREMIUM]" if disease.get('is_premium') else ""
            d_title = Label(
                text=f"[b]{disease['name']}[/b][color=E8AB26]{badge}[/color]",
                markup=True, font_size='17sp', color=(0.8, 0.2, 0.2, 1),
                size_hint_y=None, height=35, halign='left', valign='middle'
            )
            d_title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
            card.add_widget(d_title)

            # Disease image in list
            img_url = disease.get('image')
            if img_url:
                if img_url.startswith('/'):
                    img_url = f"{base_root}{img_url}"
                img_widget = AsyncImage(
                    source=img_url,
                    size_hint_y=None,
                    height=140
                )
                card.add_widget(img_widget)

            did = disease['id']
            detail_btn = Button(
                text="Voir les détails →",
                font_size='14sp',
                size_hint_y=None,
                height=42,
                background_normal='',
                background_color=Theme.PRIMARY_MAIN,
                color=Theme.TEXT_LIGHT
            )
            detail_btn.bind(on_release=lambda instance, disease_id=did, i_url=img_url: self.open_disease_detail(disease_id, i_url))
            card.add_widget(detail_btn)

            self.container.add_widget(card)

    def open_disease_detail(self, disease_id, fallback_img=None):
        res = self.pest_service.get_disease_detail(disease_id)
        if not res.get('success'):
            return

        data = res['data']
        base_root = Config.API_BASE_URL.replace('/api', '')
        img_url = data.get('image') or fallback_img
        if img_url and img_url.startswith('/'):
            img_url = f"{base_root}{img_url}"

        fields = [
            ("Symptômes", data.get('symptoms', ''), Theme.TEXT_DARK),
            ("Traitement", data.get('treatment', ''), Theme.PRIMARY_MAIN),
            ("Prévention", data.get('prevention', ''), Theme.BROWN_MAIN),
        ]
        if data.get('favorable_season'):
            fields.append(("Saison de prolifération", data.get('favorable_season'), (0.85, 0.45, 0.15, 1)))
        if data.get('tropical_organic_treatment'):
            fields.append(("Traitement bio tropical", data.get('tropical_organic_treatment'), Theme.PRIMARY_DARK))

        popup = DetailPopup(
            title_text=data['name'],
            image_url=img_url,
            fields=fields,
            is_locked=data.get('is_locked', False),
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
