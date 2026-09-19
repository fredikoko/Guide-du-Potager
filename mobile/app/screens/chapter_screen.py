from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, Rectangle
from ..styles.themes import Theme
from ..services.content_service import ContentService
from ..utils.html_parser import HTMLParser
from ..utils.config import Config

class ChapterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.content_service = ContentService()
        self.html_parser = HTMLParser()

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
            text="← Retour",
            font_size='16sp',
            size_hint_x=None,
            width=90,
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=Theme.TEXT_LIGHT
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))

        self.title_label = Label(
            text="[b]Chapitre[/b]",
            markup=True,
            font_size='18sp',
            color=Theme.TEXT_LIGHT,
            halign='left',
            valign='middle'
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

    def load_chapter(self, chapter_id):
        self.body_container.clear_widgets()
        res = self.content_service.get_chapter(chapter_id)

        if not res.get('success'):
            err_label = Label(
                text="⚠️ Impossible de charger ce chapitre.",
                color=Theme.TEXT_MUTED, font_size='16sp', size_hint_y=None, height=50
            )
            self.body_container.add_widget(err_label)
            return

        data = res['data']
        self.title_label.text = f"[b]{data['title']}[/b]"

        # Base URL for relative media image URLs
        base_root = Config.API_BASE_URL.replace('/api', '')

        # Parse chapter content into sequential text and embedded image blocks
        blocks = self.html_parser.parse_blocks(data['content'], base_url=base_root)

        for block in blocks:
            if block['type'] == 'text':
                content_label = Label(
                    text=block['content'],
                    markup=True,
                    font_size='16sp',
                    color=Theme.TEXT_DARK,
                    size_hint_y=None,
                    halign='left',
                    valign='top'
                )
                content_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
                content_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
                self.body_container.add_widget(content_label)

            elif block['type'] == 'image':
                img_widget = AsyncImage(
                    source=block['url'],
                    size_hint_y=None,
                    height=240
                )
                self.body_container.add_widget(img_widget)

        # Check if premium locked, display Upgrade Button
        if data.get('is_locked'):
            upgrade_btn = Button(
                text="★ Débloquer avec l'Abonnement Premium",
                font_size='16sp',
                size_hint_y=None,
                height=54,
                background_normal='',
                background_color=Theme.GOLD_PREMIUM,
                color=Theme.TEXT_LIGHT
            )
            upgrade_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'subscription'))
            self.body_container.add_widget(upgrade_btn)

        # Render extra attached chapter images if present (only if not already embedded in content)
        content_html = data.get('content', '')
        for img_data in data.get('images', []):
            img_url = img_data.get('image')
            if img_url:
                img_filename = img_url.split('?')[0].split('/')[-1]
                if img_filename and img_filename in content_html:
                    continue  # Skip image if already displayed inline in content

                if img_url.startswith('/'):
                    img_url = f"{base_root}{img_url}"

                img_widget = AsyncImage(
                    source=img_url,
                    size_hint_y=None,
                    height=240
                )
                self.body_container.add_widget(img_widget)
                if img_data.get('caption'):
                    cap_label = Label(
                        text=f"[i]{img_data['caption']}[/i]",
                        markup=True,
                        color=Theme.TEXT_MUTED, font_size='13sp', size_hint_y=None, height=25
                    )
                    self.body_container.add_widget(cap_label)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
