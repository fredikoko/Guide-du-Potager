from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, Rectangle
from ..styles.themes import Theme
from ..services.blog_service import BlogService
from ..utils.html_parser import HTMLParser
from ..utils.config import Config
from ..components.cards import CardWidget

class PostDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.blog_service = BlogService()
        self.html_parser = HTMLParser()
        self.current_post_id = None

        with self.canvas.before:
            Color(*Theme.BG_CREAM)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        layout = BoxLayout(orientation='vertical')

        # Header Bar with Back Button
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, padding=10, spacing=10)
        with header.canvas.before:
            Color(*Theme.HEADER_BG)
            self.header_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=self._update_header_rect, pos=self._update_header_rect)

        back_btn = Button(
            text="← Retour", font_size='16sp', size_hint_x=None, width=90,
            background_normal='', background_color=(0, 0, 0, 0), color=Theme.TEXT_LIGHT
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'blog'))

        self.title_label = Label(
            text="[b]Article[/b]", markup=True, font_size='17sp',
            color=Theme.TEXT_LIGHT, halign='left', valign='middle'
        )
        self.title_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

        header.add_widget(back_btn)
        header.add_widget(self.title_label)
        layout.add_widget(header)

        # Body Scroll Area
        scroll = ScrollView()
        self.body_container = BoxLayout(orientation='vertical', size_hint_y=None, padding=20, spacing=15)
        self.body_container.bind(minimum_height=self.body_container.setter('height'))
        scroll.add_widget(self.body_container)

        layout.add_widget(scroll)
        self.add_widget(layout)

    def load_post(self, post_id):
        self.current_post_id = post_id
        self.body_container.clear_widgets()

        res = self.blog_service.get_post_detail(post_id)
        if not res.get('success'):
            err = Label(text="⚠️ Impossible de charger l'article.", color=Theme.TEXT_MUTED, font_size='16sp', size_hint_y=None, height=50)
            self.body_container.add_widget(err)
            return

        data = res['data']
        self.title_label.text = f"[b]{data['title']}[/b]"
        base_root = Config.API_BASE_URL.replace('/api', '')

        # Meta Header Card
        cat_name = data.get('category_name') or 'Général'
        author = data.get('author_name') or 'Rédaction'
        date_str = (data.get('created_at') or '')[:10]
        views = data.get('views_count', 0)

        meta_card = CardWidget(bg_color=Theme.PRIMARY_DARK)
        meta_card.add_widget(Label(
            text=f"[b]{data['title']}[/b]", markup=True, font_size='19sp',
            color=Theme.TEXT_LIGHT, size_hint_y=None, height=40, halign='left'
        ))
        meta_card.add_widget(Label(
            text=f"[color=E8AB26][b][{cat_name}][/b][/color]  •  Par {author}  •  {date_str}  •  Vues: {views}",
            markup=True, font_size='13sp', color=Theme.PRIMARY_LIGHT, size_hint_y=None, height=25, halign='left'
        ))
        self.body_container.add_widget(meta_card)

        # Cover Image
        cover = data.get('cover_image')
        if cover:
            if cover.startswith('/'):
                cover = f"{base_root}{cover}"
            img_widget = AsyncImage(
                source=cover, size_hint_y=None, height=220
            )
            self.body_container.add_widget(img_widget)

        # Render HTML Content blocks
        blocks = self.html_parser.parse_blocks(data['content'], base_url=base_root)
        for block in blocks:
            if block['type'] == 'text':
                lbl = Label(
                    text=block['content'], markup=True, font_size='16sp',
                    color=Theme.TEXT_DARK, size_hint_y=None, halign='left', valign='top'
                )
                lbl.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                lbl.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
                self.body_container.add_widget(lbl)

            elif block['type'] == 'image':
                img_widget = AsyncImage(
                    source=block['url'], size_hint_y=None, height=240
                )
                self.body_container.add_widget(img_widget)

        # Comments Section Header
        comments = data.get('comments', [])
        c_header = Label(
            text=f"[b]Commentaires ({len(comments)}) :[/b]",
            markup=True, font_size='17sp', color=Theme.PRIMARY_DARK,
            size_hint_y=None, height=35, halign='left'
        )
        c_header.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        self.body_container.add_widget(c_header)

        # Render Comments
        for c in comments:
            c_card = CardWidget(bg_color=Theme.CARD_BG)
            c_meta = Label(
                text=f"[b]{c['author_name']}[/b]  •  {(c.get('created_at') or '')[:10]}",
                markup=True, font_size='13sp', color=Theme.BROWN_MAIN, size_hint_y=None, height=25, halign='left'
            )
            c_meta.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

            c_text = Label(
                text=c['content'], font_size='14sp', color=Theme.TEXT_DARK,
                size_hint_y=None, halign='left', valign='top'
            )
            c_text.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
            c_text.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))

            c_card.add_widget(c_meta)
            c_card.add_widget(c_text)
            self.body_container.add_widget(c_card)

        # Add Comment Input Form
        form_card = CardWidget(bg_color=Theme.CARD_BG)
        form_card.add_widget(Label(
            text="[b]Laisser un commentaire :[/b]", markup=True, font_size='15sp',
            color=Theme.PRIMARY_DARK, size_hint_y=None, height=30, halign='left'
        ))

        self.comment_input = TextInput(
            hint_text="Écrivez votre commentaire ici...",
            multiline=True, font_size='14sp', size_hint_y=None, height=80
        )
        form_card.add_widget(self.comment_input)

        send_btn = Button(
            text="Publier le commentaire", font_size='14sp', size_hint_y=None, height=44,
            background_normal='', background_color=Theme.PRIMARY_MAIN, color=Theme.TEXT_LIGHT
        )
        send_btn.bind(on_release=self.send_comment)
        form_card.add_widget(send_btn)

        self.body_container.add_widget(form_card)

    def send_comment(self, instance):
        text = self.comment_input.text.strip()
        if not text or not self.current_post_id:
            return

        res = self.blog_service.add_comment(self.current_post_id, text)
        if res.get('success'):
            self.comment_input.text = ""
            self.load_post(self.current_post_id)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
