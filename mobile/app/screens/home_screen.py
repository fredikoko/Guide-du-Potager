from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from ..styles.themes import Theme
from ..services.content_service import ContentService
from ..services.blog_service import BlogService
from ..components.cards import PartHeaderLabel, ChapterButton, CardWidget
from ..components.navigation_drawer import NavigationDrawer

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_service = ContentService()
        self.blog_service = BlogService()
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
            text="☰ MENU",
            font_size='13sp',
            size_hint_x=None,
            width=75,
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=Theme.TEXT_LIGHT
        )
        menu_btn.bind(on_release=self.toggle_drawer)

        app_title = Label(
            text="[b]Guide du Potager Tropical[/b]",
            markup=True,
            font_size='17sp',
            color=Theme.TEXT_LIGHT,
            halign='left',
            valign='middle'
        )
        app_title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

        profile_icon = Button(
            text="👤 PROFIL",
            font_size='11sp',
            size_hint_x=None,
            width=70,
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
        self.load_dashboard()

    def _create_auto_label(self, text, font_size='13sp', color=None, is_markup=True):
        if color is None:
            color = Theme.TEXT_DARK
        lbl = Label(
            text=text,
            markup=is_markup,
            font_size=font_size,
            color=color,
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        lbl.bind(width=lambda s, val: setattr(s, 'text_size', (val, None)))
        lbl.bind(texture_size=lambda s, val: setattr(s, 'height', max(val[1] + 6, 24)))
        return lbl

    def load_dashboard(self):
        self.content_container.clear_widgets()

        # ======================================================================
        # 1. HERO BANNER CARD (Parité avec web home.html)
        # ======================================================================
        hero_card = CardWidget(bg_color=Theme.PRIMARY_DARK)

        hero_badge = self._create_auto_label(
            "[color=47C26B][b]🌱 Maraîchage Tropical : Conventionnel & Bio[/b][/color]",
            font_size='12sp'
        )
        hero_title = self._create_auto_label(
            "[b]Guide Pratique du Potager Tropical[/b]",
            font_size='18sp', color=Theme.TEXT_LIGHT
        )
        hero_desc = self._create_auto_label(
            "Itinéraires techniques, fertilisation raisonnée, protection des cultures, biopesticides locaux et calendrier cultural complet.",
            font_size='13sp', color=Theme.BG_CREAM
        )

        hero_card.add_widget(hero_badge)
        hero_card.add_widget(hero_title)
        hero_card.add_widget(hero_desc)

        # 3 Quick Action Buttons
        btn_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=44, spacing=8)
        
        btn_cal = Button(
            text="📅 Simulateur",
            font_size='12sp',
            background_normal='',
            background_color=Theme.PRIMARY_MAIN,
            color=Theme.TEXT_LIGHT
        )
        btn_cal.bind(on_release=lambda x: setattr(self.manager, 'current', 'calendar'))

        btn_veg = Button(
            text="🥕 Légumes",
            font_size='12sp',
            background_normal='',
            background_color=Theme.PRIMARY_MAIN,
            color=Theme.TEXT_LIGHT
        )
        btn_veg.bind(on_release=lambda x: setattr(self.manager, 'current', 'vegetables'))

        btn_blog = Button(
            text="📰 Blog",
            font_size='12sp',
            background_normal='',
            background_color=Theme.ACCENT_EXCLUSIVE,
            color=Theme.TEXT_LIGHT
        )
        btn_blog.bind(on_release=lambda x: setattr(self.manager, 'current', 'blog'))

        btn_box.add_widget(btn_cal)
        btn_box.add_widget(btn_veg)
        btn_box.add_widget(btn_blog)
        hero_card.add_widget(btn_box)

        self.content_container.add_widget(hero_card)

        # ======================================================================
        # 2. ACCÈS RAPIDE AUX MODULES (Parité avec web home.html)
        # ======================================================================
        sec_modules = self._create_auto_label(
            "[b]🚀 Accès Rapide aux Modules :[/b]",
            font_size='16sp', color=Theme.PRIMARY_DARK
        )
        self.content_container.add_widget(sec_modules)

        modules = [
            ("📅 Simulateur Cultural", "Que semer et récolter ce mois-ci selon la saison tropicale.", "calendar", Theme.CARD_BG),
            ("🩺 Maladies & Soins [color=47C26B]★[/color]", "Identifier les attaques, traitements raisonnés et soins bio au neem.", "diseases", Theme.CARD_BG),
            ("🐛 Insectes & Biocontrôle [color=47C26B]★[/color]", "Lutte phytosanitaire raisonnée, barrières et répulsifs naturels.", "insects", Theme.CARD_BG),
            ("🛠️ Outils Maraîchers [color=47C26B]★[/color]", "Grelinettes, semoirs, goutte-à-goutte et équipement de précision.", "tools", Theme.CARD_BG),
        ]

        for mod_title, mod_desc, screen_target, bg_col in modules:
            m_card = CardWidget(bg_color=bg_col)
            lbl_title = self._create_auto_label(f"[b]{mod_title}[/b]", font_size='15sp', color=Theme.PRIMARY_MAIN)
            lbl_desc = self._create_auto_label(mod_desc, font_size='12sp', color=Theme.TEXT_DARK)
            
            open_btn = Button(
                text="Ouvrir le module →",
                font_size='12sp',
                size_hint_y=None,
                height=34,
                background_normal='',
                background_color=(0.93, 0.95, 0.93, 1.0),
                color=Theme.PRIMARY_DARK
            )
            open_btn.bind(on_release=lambda instance, s=screen_target: setattr(self.manager, 'current', s))

            m_card.add_widget(lbl_title)
            m_card.add_widget(lbl_desc)
            m_card.add_widget(open_btn)
            self.content_container.add_widget(m_card)

        # ======================================================================
        # 3. SOMMAIRE DU MANUEL NUMÉRIQUE EBOOK
        # ======================================================================
        sec_guide = self._create_auto_label(
            "[b]📖 Sommaire du Manuel Ebook :[/b]",
            font_size='16sp', color=Theme.PRIMARY_DARK
        )
        self.content_container.add_widget(sec_guide)

        res = self.content_service.get_parts()
        if res.get('success'):
            parts = res.get('data', [])
            if isinstance(parts, dict) and 'results' in parts:
                parts = parts['results']

            for part in parts:
                part_card = CardWidget(bg_color=Theme.CARD_BG)

                # Header Label for Part (Non-clickable)
                part_label = PartHeaderLabel(title=part['title'], is_premium=part.get('is_premium', False))
                part_card.add_widget(part_label)

                if part.get('description'):
                    desc = self._create_auto_label(part['description'], font_size='12sp', color=Theme.TEXT_MUTED)
                    part_card.add_widget(desc)

                # Chapters List as clickable buttons
                for chapter in part.get('chapters', []):
                    chap_btn = ChapterButton(
                        title=chapter['title'],
                        is_premium=chapter.get('is_premium', False)
                    )
                    chap_id = chapter['id']
                    chap_btn.bind(on_release=lambda instance, cid=chap_id: self.open_chapter(cid))
                    part_card.add_widget(chap_btn)

                self.content_container.add_widget(part_card)
        else:
            err_label = Label(
                text="⚠️ Contenu disponible en cache ou hors-ligne.",
                color=Theme.TEXT_MUTED, font_size='13sp', size_hint_y=None, height=30
            )
            self.content_container.add_widget(err_label)

        # ======================================================================
        # 4. DERNIERS ARTICLES DU BLOG (Parité avec web home.html)
        # ======================================================================
        sec_blog = self._create_auto_label(
            "[b]📰 Derniers Articles du Blog :[/b]",
            font_size='16sp', color=Theme.PRIMARY_DARK
        )
        self.content_container.add_widget(sec_blog)

        blog_res = self.blog_service.get_posts()
        if blog_res.get('success'):
            posts_data = blog_res.get('data', [])
            posts = posts_data.get('results', posts_data) if isinstance(posts_data, dict) else posts_data
            
            # Afficher les 2 premiers articles récents
            for post in posts[:2]:
                post_card = CardWidget(bg_color=Theme.CARD_BG)
                
                is_prem = bool(post.get('is_premium'))
                star = " [color=47C26B]★[/color]" if is_prem else ""
                cat_name = post.get('category_name') or 'Actualités'
                
                p_cat = self._create_auto_label(f"[b][color=3D7A42]{cat_name.upper()}[/color][/b]", font_size='11sp')
                p_title = self._create_auto_label(f"[b]{post['title']}[/b]{star}", font_size='14sp', color=Theme.PRIMARY_DARK)
                
                read_btn = Button(
                    text="Lire l'article →",
                    font_size='12sp',
                    size_hint_y=None,
                    height=36,
                    background_normal='',
                    background_color=Theme.PRIMARY_MAIN,
                    color=Theme.TEXT_LIGHT
                )
                pid = post['id']
                read_btn.bind(on_release=lambda instance, p=pid: self.open_blog_post(p))

                post_card.add_widget(p_cat)
                post_card.add_widget(p_title)
                post_card.add_widget(read_btn)
                self.content_container.add_widget(post_card)

        # Bouton global voir tous les articles
        all_blog_btn = Button(
            text="Voir tous les articles du blog →",
            font_size='13sp',
            size_hint_y=None,
            height=44,
            background_normal='',
            background_color=Theme.BROWN_DARK,
            color=Theme.TEXT_LIGHT
        )
        all_blog_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'blog'))
        self.content_container.add_widget(all_blog_btn)

    def open_blog_post(self, post_id):
        post_screen = self.manager.get_screen('post_detail')
        post_screen.load_post(post_id)
        self.manager.current = 'post_detail'

    def open_chapter(self, chapter_id):
        chapter_screen = self.manager.get_screen('chapter')
        chapter_screen.load_chapter(chapter_id)
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

