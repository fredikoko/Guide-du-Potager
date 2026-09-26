from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.uix.image import AsyncImage
from ..styles.themes import Theme
from ..services.glossary_service import GlossaryService
from ..components.cards import CardWidget
from ..components.search_bar import SearchBar
from ..components.navigation_drawer import NavigationDrawer
from ..utils.config import Config

class VegetablesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glossary_service = GlossaryService()
        self.current_family_id = None
        self.current_family_name = None
        self.drawer = None

        with self.canvas.before:
            Color(*Theme.BG_CREAM)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        layout = BoxLayout(orientation='vertical')

        # Header bar
        self.header = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, padding=10, spacing=10)
        with self.header.canvas.before:
            Color(*Theme.HEADER_BG)
            self.header_rect = Rectangle(size=self.header.size, pos=self.header.pos)
        self.header.bind(size=self._update_header_rect, pos=self._update_header_rect)

        # Action button (MENU or Back depending on whether filtered by family)
        self.action_btn = Button(
            text="MENU", font_size='13sp', size_hint_x=None, width=60,
            background_normal='', background_color=(0, 0, 0, 0), color=Theme.TEXT_LIGHT
        )
        self.action_btn.bind(on_release=self._on_action_btn_pressed)

        self.title_label = Label(
            text="[b]Fiches Légumes[/b]", markup=True, font_size='18sp',
            color=Theme.TEXT_LIGHT, halign='left', valign='middle'
        )
        self.title_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

        self.header.add_widget(self.action_btn)
        self.header.add_widget(self.title_label)
        layout.add_widget(self.header)

        # Search bar
        search_box = BoxLayout(size_hint_y=None, height=55, padding=[15, 8, 15, 0])
        self.search_bar = SearchBar(on_search_callback=self.filter_vegetables, placeholder="Chercher un légume...")
        search_box.add_widget(self.search_bar)
        layout.add_widget(search_box)

        # Scrollable Vegetables List
        scroll = ScrollView()
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, padding=15, spacing=15)
        self.container.bind(minimum_height=self.container.setter('height'))
        scroll.add_widget(self.container)

        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self):
        """Called automatically whenever the user navigates to this screen."""
        self._refresh_header_button()
        self.load_vegetables(family_id=self.current_family_id, family_name=self.current_family_name)

    def _refresh_header_button(self):
        if self.current_family_id is not None:
            self.action_btn.text = "← Retour"
            self.action_btn.font_size = '15sp'
            self.action_btn.width = 85
        else:
            self.action_btn.text = "MENU"
            self.action_btn.font_size = '13sp'
            self.action_btn.width = 60

    def _on_action_btn_pressed(self, instance):
        if self.current_family_id is not None:
            # Revenir aux familles botaniques et réinitialiser le filtre
            self.current_family_id = None
            self.current_family_name = None
            if self.manager:
                self.manager.current = 'families'
        else:
            self.toggle_drawer()

    def filter_vegetables(self, query):
        self.load_vegetables(family_id=self.current_family_id, family_name=self.current_family_name, search=query)

    def load_vegetables(self, family_id=None, family_name=None, search=None):
        self.current_family_id = family_id
        self.current_family_name = family_name
        self._refresh_header_button()

        if family_name:
            self.title_label.text = f"[b]Légumes : {family_name}[/b]"
        else:
            self.title_label.text = "[b]Fiches Légumes[/b]"

        self.container.clear_widgets()
        res = self.glossary_service.get_vegetables(family_id=family_id, search=search)

        if not res.get('success'):
            err = Label(
                text="⚠️ Erreur de chargement des légumes.\nVérifiez votre connexion internet.",
                color=Theme.TEXT_MUTED, font_size='15sp', size_hint_y=None, height=60,
                halign='center'
            )
            self.container.add_widget(err)
            return

        vegetables = res.get('data', [])
        if isinstance(vegetables, dict) and 'results' in vegetables:
            vegetables = vegetables['results']

        vegetables = sorted(vegetables, key=lambda v: v.get('name', '').lower())

        if not vegetables:
            empty_msg = "Aucun légume ne correspond à votre recherche." if search else "Aucune fiche légume disponible pour le moment."
            empty_lbl = Label(
                text=empty_msg,
                color=Theme.TEXT_MUTED, font_size='15sp', size_hint_y=None, height=60,
                halign='center'
            )
            self.container.add_widget(empty_lbl)
            return

        base_root = Config.API_BASE_URL.replace('/api', '')
        for veg in vegetables:
            card = CardWidget(bg_color=Theme.CARD_BG)

            # Image if available
            img_url = veg.get('image')
            if img_url:
                if img_url.startswith('/'):
                    img_url = f"{base_root}{img_url}"
                img_widget = AsyncImage(
                    source=img_url,
                    size_hint_y=None,
                    height=140
                )
                card.add_widget(img_widget)

            # Family tag if available
            if veg.get('family_name'):
                fam_lbl = Label(
                    text=f"[color=3D7A42][b]🌱 {veg['family_name']}[/b][/color]",
                    markup=True, font_size='12sp', size_hint_y=None, height=20, halign='left'
                )
                fam_lbl.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
                card.add_widget(fam_lbl)

            v_title = Label(
                text=f"[b]{veg['name']}[/b] [i]({veg.get('scientific_name', '')})[/i]",
                markup=True, font_size='17sp', color=Theme.PRIMARY_DARK,
                size_hint_y=None, height=35, halign='left', valign='middle'
            )
            v_title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

            sow = Label(
                text=f"[b]Semis :[/b] {veg.get('sowing_period', 'N/A')}",
                markup=True, color=Theme.TEXT_DARK, font_size='14sp', size_hint_y=None, height=25, halign='left'
            )
            sow.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

            harvest = Label(
                text=f"[b]Récolte :[/b] {veg.get('harvest_period', 'N/A')}",
                markup=True, color=Theme.BROWN_MAIN, font_size='14sp', size_hint_y=None, height=25, halign='left'
            )
            harvest.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

            # Caractéristiques agro-climatiques tropicales
            trop_parts = []
            if veg.get('tropical_season_display'):
                trop_parts.append(f"[b]Saison :[/b] {veg['tropical_season_display']}")
            if veg.get('cycle_duration_days'):
                trop_parts.append(f"[b]Cycle :[/b] {veg['cycle_duration_days']} j")
            if veg.get('heat_tolerance_display'):
                trop_parts.append(f"[b]Chaleur :[/b] {veg['heat_tolerance_display']}")
            if veg.get('water_requirement_display'):
                trop_parts.append(f"[b]Arrosage :[/b] {veg['water_requirement_display']}")
            if veg.get('sun_exposure_display'):
                trop_parts.append(f"[b]Exposition :[/b] {veg['sun_exposure_display']}")

            card.add_widget(v_title)
            card.add_widget(sow)
            card.add_widget(harvest)

            if trop_parts:
                trop_info = Label(
                    text=" • ".join(trop_parts),
                    markup=True, color=Theme.PRIMARY_DARK, font_size='13sp', size_hint_y=None, height=26, halign='left'
                )
                trop_info.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
                card.add_widget(trop_info)

            if veg.get('tropical_varieties'):
                vars_lbl = Label(
                    text=f"[b]Variétés tropicales conseillées :[/b] {veg['tropical_varieties']}",
                    markup=True, color=Theme.BROWN_MAIN, font_size='13sp', size_hint_y=None, halign='left'
                )
                vars_lbl.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                vars_lbl.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
                card.add_widget(vars_lbl)

            if veg.get('care_tips'):
                tips = Label(
                    text=f"[b]Soins & Entretien :[/b]\n{veg.get('care_tips', '')}",
                    markup=True, color=Theme.TEXT_DARK, font_size='14sp', size_hint_y=None, halign='left', valign='top'
                )
                tips.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                tips.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
                card.add_widget(tips)

            self.container.add_widget(card)

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
