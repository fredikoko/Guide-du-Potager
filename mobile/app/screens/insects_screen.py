from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, Rectangle
from ..styles.themes import Theme
from ..services.pest_service import PestService
from ..services.auth_service import AuthService
from ..components.cards import CardWidget
from ..components.search_bar import SearchBar
from ..components.navigation_drawer import NavigationDrawer
from ..components.detail_popup import DetailPopup
from ..utils.config import Config

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
            text="MENU", font_size='13sp', size_hint_x=None, width=60,
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

        base_root = Config.API_BASE_URL.replace('/api', '')
        insects = res.get('data', [])

        for insect in insects:
            card = CardWidget(bg_color=Theme.CARD_BG)
            is_prem = bool(insect.get('is_premium'))

            title_txt = f"[b]{insect['name']}[/b]" + (" [color=47C26B]★[/color]" if is_prem else "")
            i_title = Label(
                text=title_txt,
                markup=True, font_size='17sp',
                color=Theme.ACCENT_EXCLUSIVE if is_prem else Theme.PRIMARY_DARK,
                size_hint_y=None, height=35, halign='left', valign='middle'
            )
            i_title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
            card.add_widget(i_title)

            # Insect image in list
            img_url = insect.get('image')
            if img_url:
                if img_url.startswith('/'):
                    img_url = f"{base_root}{img_url}"
                img_widget = AsyncImage(
                    source=img_url,
                    size_hint_y=None,
                    height=140
                )
                card.add_widget(img_widget)

            if insect.get('damage'):
                dam_text = insect['damage'][:100] + ("..." if len(insect['damage']) > 100 else "")
                i_desc = Label(
                    text=dam_text,
                    color=Theme.TEXT_DARK, font_size='13sp', size_hint_y=None, height=40, halign='left', valign='top'
                )
                i_desc.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
                card.add_widget(i_desc)

            iid = insect['id']
            detail_btn = Button(
                text="Voir les détails →",
                font_size='14sp',
                size_hint_y=None,
                height=42,
                background_normal='',
                background_color=Theme.ACCENT_EXCLUSIVE if is_prem else Theme.PRIMARY_MAIN,
                color=Theme.TEXT_LIGHT
            )
            detail_btn.bind(on_release=lambda instance, insect_id=iid, i_url=img_url: self.open_insect_detail(insect_id, i_url))
            card.add_widget(detail_btn)

            self.container.add_widget(card)

    def open_insect_detail(self, insect_id, fallback_img=None):
        res = self.pest_service.get_insect_detail(insect_id)
        if not res.get('success'):
            return

        data = res['data']
        is_prem = bool(data.get('is_premium'))
        is_sub = AuthService().is_subscribed()
        is_locked = data.get('is_locked', False) or (is_prem and not is_sub)

        base_root = Config.API_BASE_URL.replace('/api', '')
        img_url = data.get('image') or fallback_img
        if img_url and img_url.startswith('/'):
            img_url = f"{base_root}{img_url}"

        if is_locked:
            fields = [
                ("Description", "🔒 La fiche d'identification complète, les solutions curatives bio et les méthodes de lutte sont réservées aux abonnés.", Theme.TEXT_MUTED),
            ]
        else:
            fields = [
                ("Description", data.get('description', ''), Theme.TEXT_DARK),
                ("Dégâts constatés", data.get('damage', ''), (0.8, 0.3, 0.2, 1)),
                ("Solution Bio / Traitement", data.get('solution', ''), Theme.PRIMARY_MAIN),
            ]
            if data.get('favorable_season'):
                fields.append(("Saison favorable", data.get('favorable_season'), (0.85, 0.45, 0.15, 1)))
            if data.get('tropical_bio_control'):
                fields.append(("Lutte biologique tropicale", data.get('tropical_bio_control'), Theme.PRIMARY_DARK))
            if data.get('prevention_tips'):
                fields.append(("Conseils de prévention", data.get('prevention_tips'), Theme.BROWN_MAIN))

        popup = DetailPopup(
            title_text=data['name'],
            image_url=img_url,
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
