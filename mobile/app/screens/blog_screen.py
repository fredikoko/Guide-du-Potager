from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, Rectangle
from ..styles.themes import Theme
from ..services.blog_service import BlogService
from ..components.cards import CardWidget
from ..components.search_bar import SearchBar
from ..components.navigation_drawer import NavigationDrawer
from ..utils.config import Config

class BlogScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.blog_service = BlogService()
        self.drawer = None
        self.selected_category_id = None
        self.categories = []

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
            text="[b]Blog & Actualités[/b]", markup=True, font_size='18sp',
            color=Theme.TEXT_LIGHT, halign='left', valign='middle'
        )
        title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

        header.add_widget(menu_btn)
        header.add_widget(title)
        layout.add_widget(header)

        # Search bar
        search_box = BoxLayout(size_hint_y=None, height=55, padding=[15, 8, 15, 0])
        search_bar = SearchBar(on_search_callback=self.filter_posts, placeholder="Chercher un article...")
        search_box.add_widget(search_bar)
        layout.add_widget(search_box)

        # Category Horizontal Selector
        cat_scroll = ScrollView(size_hint_y=None, height=48, do_scroll_y=False)
        self.cat_box = BoxLayout(size_hint_x=None, height=42, padding=[10, 3, 10, 3], spacing=8)
        self.cat_box.bind(minimum_width=self.cat_box.setter('width'))
        cat_scroll.add_widget(self.cat_box)
        layout.add_widget(cat_scroll)

        # Scrollable Articles List
        scroll = ScrollView()
        self.posts_container = BoxLayout(orientation='vertical', size_hint_y=None, padding=15, spacing=15)
        self.posts_container.bind(minimum_height=self.posts_container.setter('height'))
        scroll.add_widget(self.posts_container)

        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self):
        self.load_categories()
        self.load_posts()

    def load_categories(self):
        self.cat_box.clear_widgets()
        res = self.blog_service.get_categories()
        if not res.get('success'):
            return

        cats = res.get('data', [])
        if isinstance(cats, dict) and 'results' in cats:
            cats = cats['results']

        self.categories = cats

        # Bouton "Toutes" (avec largeur dynamique)
        all_btn = Button(
            text="Toutes",
            font_size='13sp',
            size_hint=(None, None),
            height=36,
            background_normal='',
            background_color=Theme.BROWN_MAIN if self.selected_category_id is None else Theme.CARD_BG,
            color=Theme.TEXT_LIGHT if self.selected_category_id is None else Theme.TEXT_DARK,
            halign='center',
            valign='middle'
        )
        all_btn.bind(texture_size=lambda instance, val: setattr(instance, 'width', max(70, val[0] + 24)) if val[0] > 0 else None)
        all_btn.width = 75
        all_btn.bind(on_release=lambda x: self.select_category(None))
        self.cat_box.add_widget(all_btn)

        # Boutons des Catégories avec largeur automatique adaptée à chaque libellé
        for c in cats:
            c_id = c['id']
            cat_name = c['name']
            btn = Button(
                text=cat_name,
                font_size='13sp',
                size_hint=(None, None),
                height=36,
                background_normal='',
                background_color=Theme.BROWN_MAIN if self.selected_category_id == c_id else Theme.CARD_BG,
                color=Theme.TEXT_LIGHT if self.selected_category_id == c_id else Theme.TEXT_DARK,
                halign='center',
                valign='middle'
            )
            # Adapte dynamiquement la largeur du bouton au rendu textuel réel + marges intérieures
            btn.bind(texture_size=lambda instance, val: setattr(instance, 'width', max(80, val[0] + 28)) if val[0] > 0 else None)
            btn.width = max(80, len(cat_name) * 9 + 28)
            btn.bind(on_release=lambda instance, category_id=c_id: self.select_category(category_id))
            self.cat_box.add_widget(btn)

    def select_category(self, category_id):
        self.selected_category_id = category_id
        self.load_categories()
        self.load_posts()

    def filter_posts(self, query):
        self.load_posts(search=query)

    def load_posts(self, search=None):
        self.posts_container.clear_widgets()
        res = self.blog_service.get_posts(category=self.selected_category_id, search=search)

        if not res.get('success'):
            err = Label(text="⚠️ Erreur de chargement des articles.", color=Theme.TEXT_MUTED, font_size='15sp', size_hint_y=None, height=50)
            self.posts_container.add_widget(err)
            return

        base_root = Config.API_BASE_URL.replace('/api', '')
        posts = res.get('data', [])
        if isinstance(posts, dict) and 'results' in posts:
            posts = posts['results']

        if not posts:
            empty_lbl = Label(text="Aucun article trouvé.", color=Theme.TEXT_MUTED, font_size='14sp', size_hint_y=None, height=40)
            self.posts_container.add_widget(empty_lbl)
            return

        for post in posts:
            card = CardWidget(bg_color=Theme.CARD_BG)

            # Main Cover Image at top of card
            cover = post.get('cover_image')
            if cover:
                if cover.startswith('/'):
                    cover = f"{base_root}{cover}"
                img_widget = AsyncImage(
                    source=cover,
                    size_hint_y=None,
                    height=160
                )
                card.add_widget(img_widget)

            # Article Title & Premium Badge
            badge = " [PREMIUM]" if post.get('is_premium') else ""
            p_title = Label(
                text=f"[b]{post['title']}[/b][color=E8AB26]{badge}[/color]",
                markup=True, font_size='17sp', color=Theme.PRIMARY_DARK,
                size_hint_y=None, halign='left', valign='top'
            )
            p_title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
            p_title.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
            card.add_widget(p_title)

            # Category badge & Meta
            cat_name = post.get('category_name') or 'Général'
            date_str = (post.get('created_at') or '')[:10]
            views = post.get('views_count', 0)

            meta_lbl = Label(
                text=f"[color=855E42][b][{cat_name}][/b][/color]  •  {date_str}  •  Vues: {views}",
                markup=True, font_size='12sp', color=Theme.TEXT_MUTED,
                size_hint_y=None, halign='left', valign='top'
            )
            meta_lbl.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
            meta_lbl.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
            card.add_widget(meta_lbl)

            # Excerpt text
            excerpt_text = post.get('excerpt', '')
            if excerpt_text:
                excerpt_lbl = Label(
                    text=excerpt_text,
                    color=Theme.TEXT_DARK, font_size='13sp', size_hint_y=None, halign='left', valign='top'
                )
                excerpt_lbl.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                excerpt_lbl.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
                card.add_widget(excerpt_lbl)

            # Read Article Button
            pid = post['id']
            read_btn = Button(
                text="Lire l'article →",
                font_size='14sp',
                size_hint_y=None,
                height=42,
                background_normal='',
                background_color=Theme.PRIMARY_MAIN,
                color=Theme.TEXT_LIGHT
            )
            read_btn.bind(on_release=lambda instance, post_id=pid: self.open_post_detail(post_id))
            card.add_widget(read_btn)

            self.posts_container.add_widget(card)

    def open_post_detail(self, post_id):
        detail_screen = self.manager.get_screen('post_detail')
        detail_screen.load_post(post_id)
        self.manager.current = 'post_detail'

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
