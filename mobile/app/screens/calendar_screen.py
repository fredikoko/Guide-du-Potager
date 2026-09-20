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
from ..components.navigation_drawer import NavigationDrawer
from ..utils.config import Config

MONTHS = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
]

class CalendarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glossary_service = GlossaryService()
        self.drawer = None
        self.selected_month = "Mars"
        self.selected_action = "semis"  # "semis" or "recolte"

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
            text="[b]Simulateur de Calendrier[/b]", markup=True, font_size='18sp',
            color=Theme.TEXT_LIGHT, halign='left', valign='middle'
        )
        title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

        header.add_widget(menu_btn)
        header.add_widget(title)
        layout.add_widget(header)

        # Filter Section: Action Toggle Buttons
        action_box = BoxLayout(size_hint_y=None, height=45, padding=[15, 8, 15, 0], spacing=10)
        self.semis_btn = Button(
            text="Semis & Plantations", font_size='14sp',
            background_normal='', background_color=Theme.PRIMARY_MAIN, color=Theme.TEXT_LIGHT
        )
        self.semis_btn.bind(on_release=lambda x: self.select_action('semis'))

        self.recolte_btn = Button(
            text="Récoltes", font_size='14sp',
            background_normal='', background_color=(0.9, 0.9, 0.9, 1), color=Theme.TEXT_DARK
        )
        self.recolte_btn.bind(on_release=lambda x: self.select_action('recolte'))

        action_box.add_widget(self.semis_btn)
        action_box.add_widget(self.recolte_btn)
        layout.add_widget(action_box)

        # Horizontal Scroll Area for Months Selector
        months_scroll = ScrollView(size_hint_y=None, height=50, do_scroll_y=False)
        months_box = BoxLayout(size_hint_x=None, height=45, padding=[10, 5, 10, 5], spacing=8)
        months_box.bind(minimum_width=months_box.setter('width'))

        self.month_buttons = {}
        for m in MONTHS:
            btn = Button(
                text=m, font_size='13sp', size_hint_x=None, width=95,
                background_normal='',
                background_color=Theme.BROWN_MAIN if m == self.selected_month else Theme.CARD_BG,
                color=Theme.TEXT_LIGHT if m == self.selected_month else Theme.TEXT_DARK
            )
            btn.bind(on_release=lambda instance, month_name=m: self.select_month(month_name))
            self.month_buttons[m] = btn
            months_box.add_widget(btn)

        months_scroll.add_widget(months_box)
        layout.add_widget(months_scroll)

        # Content Results Scroll Area
        scroll = ScrollView()
        self.results_container = BoxLayout(orientation='vertical', size_hint_y=None, padding=15, spacing=15)
        self.results_container.bind(minimum_height=self.results_container.setter('height'))
        scroll.add_widget(self.results_container)

        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self):
        self.load_calendar_results()

    def select_action(self, action):
        self.selected_action = action
        if action == 'semis':
            self.semis_btn.background_color = Theme.PRIMARY_MAIN
            self.semis_btn.color = Theme.TEXT_LIGHT
            self.recolte_btn.background_color = (0.9, 0.9, 0.9, 1)
            self.recolte_btn.color = Theme.TEXT_DARK
        else:
            self.recolte_btn.background_color = Theme.PRIMARY_MAIN
            self.recolte_btn.color = Theme.TEXT_LIGHT
            self.semis_btn.background_color = (0.9, 0.9, 0.9, 1)
            self.semis_btn.color = Theme.TEXT_DARK

        self.load_calendar_results()

    def select_month(self, month_name):
        self.selected_month = month_name
        for m, btn in self.month_buttons.items():
            if m == month_name:
                btn.background_color = Theme.BROWN_MAIN
                btn.color = Theme.TEXT_LIGHT
            else:
                btn.background_color = Theme.CARD_BG
                btn.color = Theme.TEXT_DARK

        self.load_calendar_results()

    def load_calendar_results(self):
        self.results_container.clear_widgets()
        res = self.glossary_service.get_vegetables()

        if not res.get('success'):
            err = Label(text="⚠️ Impossible de charger les données du calendrier.", color=Theme.TEXT_MUTED, font_size='15sp', size_hint_y=None, height=50)
            self.results_container.add_widget(err)
            return

        base_root = Config.API_BASE_URL.replace('/api', '')
        vegetables = res.get('data', [])

        # DRF pagination wrapper check
        if isinstance(vegetables, dict) and 'results' in vegetables:
            vegetables = vegetables['results']

        matching_vegs = []
        target_month_lower = self.selected_month.lower()

        for veg in vegetables:
            sowing_txt = (veg.get('sowing_period') or '').lower()
            harvest_txt = (veg.get('harvest_period') or '').lower()

            if self.selected_action == 'semis':
                if (
                    target_month_lower[:3] in sowing_txt
                    or target_month_lower in sowing_txt
                    or "toute l'année" in sowing_txt
                    or "toute l'annee" in sowing_txt
                    or "toute l’année" in sowing_txt
                ):
                    matching_vegs.append(veg)
            else:
                if (
                    target_month_lower[:3] in harvest_txt
                    or target_month_lower in harvest_txt
                    or "toute l'année" in harvest_txt
                    or "toute l'annee" in harvest_txt
                    or "toute l’année" in harvest_txt
                ):
                    matching_vegs.append(veg)

        # Header Status Label
        action_name = "Semer / Planter" if self.selected_action == 'semis' else "Récolter"
        status_lbl = Label(
            text=f"[b]Légumes à {action_name} en {self.selected_month} ({len(matching_vegs)}) :[/b]",
            markup=True, font_size='16sp', color=Theme.PRIMARY_DARK,
            size_hint_y=None, height=35, halign='left'
        )
        status_lbl.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        self.results_container.add_widget(status_lbl)

        if not matching_vegs:
            empty_lbl = Label(
                text=f"Aucun légume répertorié pour {action_name.lower()} spécifique en {self.selected_month}.",
                color=Theme.TEXT_MUTED, font_size='14sp', size_hint_y=None, height=40, halign='left'
            )
            empty_lbl.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
            self.results_container.add_widget(empty_lbl)
            return

        for veg in matching_vegs:
            card = CardWidget(bg_color=Theme.CARD_BG)

            v_title = Label(
                text=f"[b]{veg['name']}[/b] [i]({veg.get('scientific_name', '')})[/i]",
                markup=True, font_size='17sp', color=Theme.PRIMARY_DARK,
                size_hint_y=None, height=35, halign='left'
            )
            v_title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
            card.add_widget(v_title)

            img_url = veg.get('image')
            if img_url:
                if img_url.startswith('/'):
                    img_url = f"{base_root}{img_url}"
                img_widget = AsyncImage(
                    source=img_url,
                    size_hint_y=None,
                    height=130
                )
                card.add_widget(img_widget)

            sow = Label(
                text=f"[b]Semis :[/b] {veg.get('sowing_period', 'N/A')}",
                markup=True, color=Theme.TEXT_DARK, font_size='14sp', size_hint_y=None, height=25, halign='left'
            )
            sow.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
            card.add_widget(sow)

            harvest = Label(
                text=f"[b]Récolte :[/b] {veg.get('harvest_period', 'N/A')}",
                markup=True, color=Theme.BROWN_MAIN, font_size='14sp', size_hint_y=None, height=25, halign='left'
            )
            harvest.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
            card.add_widget(harvest)

            if veg.get('tropical_season_display') or veg.get('cycle_duration_days'):
                trop_desc = []
                if veg.get('tropical_season_display'):
                    trop_desc.append(f"Saison : {veg['tropical_season_display']}")
                if veg.get('cycle_duration_days'):
                    trop_desc.append(f"Cycle : {veg['cycle_duration_days']} j")
                trop_lbl = Label(
                    text=f"[b]Profil tropical :[/b] {' | '.join(trop_desc)}",
                    markup=True, color=Theme.PRIMARY_DARK, font_size='13sp', size_hint_y=None, height=25, halign='left'
                )
                trop_lbl.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
                card.add_widget(trop_lbl)

            tips = Label(
                text=f"[b]Conseils :[/b] {veg.get('care_tips', '')}",
                markup=True, color=Theme.TEXT_DARK, font_size='13sp', size_hint_y=None, halign='left', valign='top'
            )
            tips.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
            tips.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
            card.add_widget(tips)

            self.results_container.add_widget(card)

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
