from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from ..styles.themes import Theme
from ..services.content_service import ContentService
from ..components.cards import CardWidget
from ..components.search_bar import SearchBar
from ..components.navigation_drawer import NavigationDrawer
from ..utils.config import Config

class GuideScreen(Screen):
    """
    Écran mobile du Sommaire du Guide du Potager Tropical.
    Présente l'ensemble des chapitres sous forme de cartes d'articles avec :
    - Barre de recherche en temps réel
    - Sélecteur horizontal par grande partie
    - Image de couverture, temps de lecture estimé, badges d'accès et extrait
    - Navigation fluide vers le chapitre sélectionné
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_service = ContentService()
        self.drawer = None
        self.selected_part_id = None
        self.parts = []
        self.current_search = None

        with self.canvas.before:
            Color(*Theme.BG_CREAM)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        layout = BoxLayout(orientation='vertical')

        # Top App Bar
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, padding=10, spacing=10)
        with header.canvas.before:
            Color(*Theme.HEADER_BG)
            self.header_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=self._update_header_rect, pos=self._update_header_rect)

        menu_btn = Button(
            text="☰ MENU", font_size='13sp', size_hint_x=None, width=75,
            background_normal='', background_color=(0, 0, 0, 0), color=Theme.TEXT_LIGHT
        )
        menu_btn.bind(on_release=self.toggle_drawer)

        title = Label(
            text="[b]Sommaire du Guide[/b]", markup=True, font_size='18sp',
            color=Theme.TEXT_LIGHT, halign='left', valign='middle'
        )
        title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

        home_icon = Button(
            text="🏠 ACCUEIL", font_size='11sp', size_hint_x=None, width=80,
            background_normal='', background_color=(0, 0, 0, 0), color=Theme.TEXT_LIGHT
        )
        home_icon.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))

        header.add_widget(menu_btn)
        header.add_widget(title)
        header.add_widget(home_icon)
        layout.add_widget(header)

        # Barre de recherche
        search_box = BoxLayout(size_hint_y=None, height=55, padding=[15, 8, 15, 0])
        search_bar = SearchBar(on_search_callback=self.filter_chapters, placeholder="Chercher un chapitre, une technique...")
        search_box.add_widget(search_bar)
        layout.add_widget(search_box)

        # Sélecteur horizontal des Grandes Parties (Boutons filtres)
        part_scroll = ScrollView(size_hint_y=None, height=48, do_scroll_y=False)
        self.part_box = BoxLayout(size_hint_x=None, height=42, padding=[10, 3, 10, 3], spacing=8)
        self.part_box.bind(minimum_width=self.part_box.setter('width'))
        part_scroll.add_widget(self.part_box)
        layout.add_widget(part_scroll)

        # Liste scrollable des Chapitres
        self.scroll = ScrollView()
        self.chapters_container = BoxLayout(orientation='vertical', size_hint_y=None, padding=15, spacing=15)
        self.chapters_container.bind(minimum_height=self.chapters_container.setter('height'))
        self.scroll.add_widget(self.chapters_container)

        layout.add_widget(self.scroll)
        self.add_widget(layout)

    def reset_scroll(self, *args):
        if hasattr(self, 'scroll') and self.scroll:
            self.scroll.scroll_y = 1.0
            self.scroll.scroll_x = 0.0

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.reset_scroll()

    def on_enter(self):
        self.reset_scroll()
        self.load_parts()
        self.load_chapters()
        Clock.schedule_once(self.reset_scroll, 0)
        Clock.schedule_once(self.reset_scroll, 0.05)

    def on_leave(self, *args):
        super().on_leave(*args)
        self.close_drawer()
        self.reset_scroll()

    def load_parts(self):
        self.part_box.clear_widgets()
        res = self.content_service.get_parts()
        if not res.get('success'):
            return

        parts_data = res.get('data', [])
        if isinstance(parts_data, dict) and 'results' in parts_data:
            parts_data = parts_data['results']

        self.parts = parts_data

        # Bouton "Toutes les parties"
        all_btn = Button(
            text="Toutes",
            font_size='13sp',
            size_hint=(None, None),
            height=36,
            background_normal='',
            background_color=Theme.BROWN_MAIN if self.selected_part_id is None else Theme.CARD_BG,
            color=Theme.TEXT_LIGHT if self.selected_part_id is None else Theme.TEXT_DARK,
            halign='center',
            valign='middle'
        )
        all_btn.bind(texture_size=lambda instance, val: setattr(instance, 'width', max(70, val[0] + 24)) if val[0] > 0 else None)
        all_btn.width = 75
        all_btn.bind(on_release=lambda x: self.select_part(None))
        self.part_box.add_widget(all_btn)

        # Boutons pour chaque Partie avec adaptation dynamique de la largeur
        for p in self.parts:
            p_id = p['id']
            p_order = p.get('order', '')
            p_title = p.get('title', '')
            btn_label = f"Partie {p_order}" if len(p_title) > 20 else f"P{p_order} : {p_title}"

            btn = Button(
                text=btn_label,
                font_size='13sp',
                size_hint=(None, None),
                height=36,
                background_normal='',
                background_color=Theme.BROWN_MAIN if self.selected_part_id == p_id else Theme.CARD_BG,
                color=Theme.TEXT_LIGHT if self.selected_part_id == p_id else Theme.TEXT_DARK,
                halign='center',
                valign='middle'
            )
            btn.bind(texture_size=lambda instance, val: setattr(instance, 'width', max(80, val[0] + 28)) if val[0] > 0 else None)
            btn.width = max(80, len(btn_label) * 9 + 28)
            btn.bind(on_release=lambda instance, part_id=p_id: self.select_part(part_id))
            self.part_box.add_widget(btn)

    def select_part(self, part_id):
        self.selected_part_id = part_id
        self.load_parts()
        self.load_chapters(search=self.current_search)

    def filter_chapters(self, query):
        self.current_search = query.strip() if query else None
        self.load_chapters(search=self.current_search)

    def load_chapters(self, search=None):
        self.reset_scroll()
        self.chapters_container.clear_widgets()
        res = self.content_service.get_chapters(part_id=self.selected_part_id, search=search)

        if not res.get('success'):
            err = Label(text="⚠️ Erreur de chargement des chapitres.", color=Theme.TEXT_MUTED, font_size='15sp', size_hint_y=None, height=50)
            self.chapters_container.add_widget(err)
            Clock.schedule_once(self.reset_scroll, 0)
            return

        base_root = Config.API_BASE_URL.replace('/api', '')
        chapters = res.get('data', [])
        if isinstance(chapters, dict) and 'results' in chapters:
            chapters = chapters['results']

        if not chapters:
            empty_lbl = Label(text="Aucun chapitre trouvé pour cette recherche.", color=Theme.TEXT_MUTED, font_size='14sp', size_hint_y=None, height=50)
            self.chapters_container.add_widget(empty_lbl)
            Clock.schedule_once(self.reset_scroll, 0)
            return

        for ch in chapters:
            card = CardWidget(bg_color=Theme.CARD_BG)

            # Image de couverture si présente
            cover = ch.get('cover_image')
            if cover:
                if cover.startswith('/'):
                    cover = f"{base_root}{cover}"
                img_widget = AsyncImage(
                    source=cover,
                    size_hint_y=None,
                    height=160
                )
                card.add_widget(img_widget)

            # Titre du Chapitre avec Étoile Exclusif
            is_prem = bool(ch.get('is_premium'))
            star_indicator = " [color=47C26B]★[/color]" if is_prem else ""
            ch_title = Label(
                text=f"[b]{ch['title']}[/b]{star_indicator}",
                markup=True, font_size='16sp',
                color=Theme.ACCENT_EXCLUSIVE if is_prem else Theme.PRIMARY_DARK,
                size_hint_y=None, halign='left', valign='top'
            )
            ch_title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
            ch_title.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
            card.add_widget(ch_title)

            # Badge Partie & Statut d'accès
            part_name = ch.get('part_title') or f"Partie {ch.get('part_order', ch.get('part', ''))}"
            prem_txt = "  •  [color=47C26B]★ Exclusif[/color]" if is_prem else "  •  Accès libre"

            meta_lbl = Label(
                text=f"[color=855E42][b][{part_name}][/b][/color]{prem_txt}",
                markup=True, font_size='12sp', color=Theme.TEXT_MUTED,
                size_hint_y=None, halign='left', valign='top'
            )
            meta_lbl.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
            meta_lbl.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
            card.add_widget(meta_lbl)

            # Extrait textuel du contenu
            excerpt_text = ch.get('excerpt', '')
            if excerpt_text:
                excerpt_lbl = Label(
                    text=excerpt_text,
                    color=Theme.TEXT_DARK, font_size='13sp', size_hint_y=None, halign='left', valign='top'
                )
                excerpt_lbl.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                excerpt_lbl.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
                card.add_widget(excerpt_lbl)

            # Bouton de Consultation du Chapitre
            cid = ch['id']
            read_btn = Button(
                text="Consulter le chapitre →",
                font_size='14sp',
                size_hint_y=None,
                height=42,
                background_normal='',
                background_color=Theme.ACCENT_EXCLUSIVE if is_prem else Theme.PRIMARY_MAIN,
                color=Theme.TEXT_LIGHT
            )
            read_btn.bind(on_release=lambda instance, chapter_id=cid: self.open_chapter(chapter_id))
            card.add_widget(read_btn)

            self.chapters_container.add_widget(card)

        Clock.schedule_once(self.reset_scroll, 0)
        Clock.schedule_once(self.reset_scroll, 0.05)

    def open_chapter(self, chapter_id):
        chapter_screen = self.manager.get_screen('chapter')
        chapter_screen.load_chapter(chapter_id, from_screen='guide')
        self.manager.current = 'chapter'

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
