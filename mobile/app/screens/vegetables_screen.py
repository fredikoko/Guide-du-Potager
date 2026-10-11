from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.uix.image import AsyncImage
from kivy.clock import Clock
from ..styles.themes import Theme
from ..services.glossary_service import GlossaryService
from ..services.auth_service import AuthService
from ..components.cards import CardWidget
from ..components.search_bar import SearchBar
from ..components.navigation_drawer import NavigationDrawer
from ..components.detail_popup import DetailPopup
from ..utils.config import Config
from ..utils.html_parser import HTMLParser

class VegetablesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glossary_service = GlossaryService()
        self.auth_service = AuthService()
        self.current_family_id = None
        self.current_family_name = None
        self.drawer = None
        self.loaded_vegetables = []

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
        self.scroll = ScrollView()
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, padding=15, spacing=15)
        self.container.bind(minimum_height=self.container.setter('height'))
        self.scroll.add_widget(self.container)

        layout.add_widget(self.scroll)
        self.add_widget(layout)

    def reset_scroll(self, *args):
        if hasattr(self, 'scroll') and self.scroll:
            self.scroll.scroll_y = 1.0
            self.scroll.scroll_x = 0.0

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
            self.reset_scroll()
            if self.manager:
                self.manager.current = 'families'
        else:
            self.toggle_drawer()

    def filter_vegetables(self, query):
        self.load_vegetables(family_id=self.current_family_id, family_name=self.current_family_name, search=query)

    def load_vegetables(self, family_id=None, family_name=None, search=None):
        self.reset_scroll()
        self.current_family_id = family_id
        self.current_family_name = family_name
        self._refresh_header_button()

        if family_name:
            self.title_label.text = f"[b]Légumes : {family_name}[/b]"
        else:
            self.title_label.text = "[b]Fiches Légumes[/b]"

        self.container.clear_widgets()
        Clock.schedule_once(self.reset_scroll, 0)
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

        self.loaded_vegetables = sorted(vegetables, key=lambda v: v.get('name', '').lower())

        if not self.loaded_vegetables:
            empty_msg = "Aucun légume ne correspond à votre recherche." if search else "Aucune fiche légume disponible pour le moment."
            empty_lbl = Label(
                text=empty_msg,
                color=Theme.TEXT_MUTED, font_size='15sp', size_hint_y=None, height=60,
                halign='center'
            )
            self.container.add_widget(empty_lbl)
            return

        base_root = Config.API_BASE_URL.replace('/api', '')
        for veg in self.loaded_vegetables:
            card = CardWidget(bg_color=Theme.CARD_BG)
            is_prem = bool(veg.get('is_premium'))

            # Titre du légume + Nom botanique + Etoile Premium
            title_parts = [f"[b]{veg['name']}[/b]"]
            if is_prem:
                title_parts.append("[color=47C26B]★[/color]")
            if veg.get('scientific_name'):
                title_parts.append(f"[size=13sp][i]({veg['scientific_name']})[/i][/size]")

            v_title = Label(
                text=" ".join(title_parts),
                markup=True, font_size='17sp',
                color=Theme.ACCENT_EXCLUSIVE if is_prem else Theme.PRIMARY_DARK,
                size_hint_y=None, height=32, halign='left', valign='middle'
            )
            v_title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
            card.add_widget(v_title)

            # Badge famille botanique
            if veg.get('family_name'):
                fam_lbl = Label(
                    text=f"[color=3D7A42][b]🌱 {veg['family_name']}[/b][/color]",
                    markup=True, font_size='12sp', size_hint_y=None, height=20, halign='left'
                )
                fam_lbl.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
                card.add_widget(fam_lbl)

            # Image du légume
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

            # Calendrier : Semis et Récolte
            cal_text = f"[b]Semis :[/b] {veg.get('sowing_period', 'N/A')}  •  [b]Récolte :[/b] {veg.get('harvest_period', 'N/A')}"
            cal_lbl = Label(
                text=cal_text,
                markup=True, color=Theme.TEXT_DARK, font_size='13sp', size_hint_y=None, height=24, halign='left'
            )
            cal_lbl.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
            card.add_widget(cal_lbl)

            # Paramètres agro-climatiques succincts
            trop_parts = []
            if veg.get('tropical_season_display'):
                trop_parts.append(f"Saison : {veg['tropical_season_display']}")
            if veg.get('cycle_duration_days'):
                trop_parts.append(f"Cycle : {veg['cycle_duration_days']} j")
            if veg.get('water_requirement_display'):
                trop_parts.append(f"Eau : {veg['water_requirement_display']}")

            if trop_parts:
                trop_info = Label(
                    text="[color=855E42][b]• " + " | ".join(trop_parts) + "[/b][/color]",
                    markup=True, font_size='12sp', size_hint_y=None, height=22, halign='left'
                )
                trop_info.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
                card.add_widget(trop_info)

            # Extrait des conseils de culture
            care_raw = veg.get('rendered_care_tips') or veg.get('care_tips')
            if care_raw:
                clean_care = HTMLParser.to_markup(str(care_raw)).strip()
                # Nettoyer les balises pour l'aperçu textuel
                clean_preview = clean_care.replace('[b]', '').replace('[/b]', '').replace('[i]', '').replace('[/i]', '')
                if len(clean_preview) > 110:
                    clean_preview = clean_preview[:110] + "..."
                preview_lbl = Label(
                    text=f"[color=555555]{clean_preview}[/color]",
                    markup=True, font_size='13sp', size_hint_y=None, height=36, halign='left', valign='top'
                )
                preview_lbl.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
                card.add_widget(preview_lbl)

            # Bouton d'ouverture du détail en Popup
            vid = veg['id']
            detail_btn = Button(
                text="Voir les détails →",
                font_size='14sp',
                size_hint_y=None,
                height=42,
                background_normal='',
                background_color=Theme.ACCENT_EXCLUSIVE if is_prem else Theme.PRIMARY_MAIN,
                color=Theme.TEXT_LIGHT
            )
            detail_btn.bind(on_release=lambda instance, vegetable_id=vid, i_url=img_url: self.open_vegetable_detail(vegetable_id, i_url))
            card.add_widget(detail_btn)

            self.container.add_widget(card)

    def open_vegetable_detail(self, vegetable_id, fallback_img=None):
        """Ouvre une fiche détaillée complète du légume dans une popup interactive."""
        # 1. Tenter la récupération via l'API / cache
        res = self.glossary_service.get_vegetable_detail(vegetable_id)
        if res.get('success') and res.get('data'):
            data = res['data']
        else:
            # Fallback sur les données déjà chargées dans l'écran
            data = next((v for v in self.loaded_vegetables if v.get('id') == vegetable_id), None)
            if not data:
                return

        is_prem = bool(data.get('is_premium'))
        is_sub = self.auth_service.is_subscribed()
        is_locked = data.get('is_locked', False) or (is_prem and not is_sub)

        base_root = Config.API_BASE_URL.replace('/api', '')
        img_url = data.get('image') or fallback_img
        if img_url and img_url.startswith('/'):
            img_url = f"{base_root}{img_url}"

        if is_locked:
            fields = [
                (
                    "Fiche de culture agronomique",
                    "🔒 La fiche agronomique complète, les protocoles de semis et repiquage, ainsi que les conseils de fertilisation et d'entretien sont réservés aux abonnés.",
                    Theme.TEXT_MUTED
                ),
            ]
        else:
            fields = []

            # 1. Nom botanique & Famille
            if data.get('scientific_name'):
                fields.append(("Nom botanique", f"[i]{data['scientific_name']}[/i]", Theme.TEXT_MUTED))
            if data.get('family_name'):
                fields.append(("Famille botanique", f"🌱 {data['family_name']}", Theme.PRIMARY_MAIN))

            # 2. Périodes culturales
            fields.append(("Période de semis", data.get('sowing_period', 'Non spécifié'), Theme.PRIMARY_DARK))
            fields.append(("Période de récolte", data.get('harvest_period', 'Non spécifié'), Theme.BROWN_MAIN))

            # 3. Paramètres agro-climatiques tropicaux
            agro_lines = []
            if data.get('tropical_season_display') or data.get('tropical_season'):
                agro_lines.append(f"• Saison optimale : {data.get('tropical_season_display') or data.get('tropical_season')}")
            if data.get('cycle_duration_days'):
                agro_lines.append(f"• Durée du cycle : {data['cycle_duration_days']} jours")
            if data.get('heat_tolerance_display') or data.get('heat_tolerance'):
                agro_lines.append(f"• Tolérance à la chaleur : {data.get('heat_tolerance_display') or data.get('heat_tolerance')}")
            if data.get('water_requirement_display') or data.get('water_requirement'):
                agro_lines.append(f"• Besoins en eau / irrigation : {data.get('water_requirement_display') or data.get('water_requirement')}")
            if data.get('sun_exposure_display') or data.get('sun_exposure'):
                agro_lines.append(f"• Exposition au soleil : {data.get('sun_exposure_display') or data.get('sun_exposure')}")

            if agro_lines:
                fields.append(("Conditions de culture tropicale", "\n".join(agro_lines), (0.85, 0.45, 0.15, 1)))

            # 4. Variétés tropicales recommandées
            if data.get('tropical_varieties'):
                fields.append(("Variétés adaptées au climat tropical", data['tropical_varieties'], Theme.BROWN_MAIN))

            # 5. Conseils de culture et entretien (Markdown / HTML complet)
            care_text = data.get('rendered_care_tips') or data.get('care_tips')
            if care_text:
                fields.append(("Conseils de culture & Entretien", care_text, Theme.PRIMARY_DARK))

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
        AuthService().logout()
        self.close_drawer()
        self.manager.current = 'login'

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
