from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle, Line
from ..styles.themes import Theme

class CardWidget(BoxLayout):
    def __init__(self, bg_color=Theme.CARD_BG, radius=[10], **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 8
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=radius)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class PartHeaderLabel(Label):
    def __init__(self, title, is_premium=False, **kwargs):
        super().__init__(**kwargs)
        star = " [color=47C26B]★[/color]" if is_premium else ""
        self.text = f"[b]{title}[/b]{star}"
        self.markup = True
        self.font_size = '18sp'
        self.color = Theme.ACCENT_EXCLUSIVE if is_premium else Theme.PRIMARY_DARK
        self.size_hint_y = None
        self.height = 40
        self.halign = 'left'
        self.valign = 'middle'
        self.bind(size=self._update_size)

    def _update_size(self, instance, value):
        self.text_size = (self.width, None)

class ChapterButton(Button):
    def __init__(self, title, is_premium=False, **kwargs):
        super().__init__(**kwargs)
        prefix = "★" if is_premium else "•"
        self.text = f"  {prefix}  {title}"
        self.font_size = '15sp'
        self.size_hint_y = None
        self.height = 50
        self.background_normal = ''
        self.background_color = Theme.ACCENT_EXCLUSIVE if is_premium else Theme.PRIMARY_MAIN
        self.color = Theme.TEXT_LIGHT
        self.halign = 'left'
        self.valign = 'middle'
        self.bind(size=self._update_size)

    def _update_size(self, instance, value):
        self.text_size = (self.width - 20, None)

class ClickableRow(ButtonBehavior, BoxLayout):
    pass

class FAQAccordionCard(BoxLayout):
    """
    Composant FAQ rétractable (Accordéon / Collapsible) similaire à <details><summary>.
    Permet à l'utilisateur d'afficher ou de masquer la réponse au toucher de la question.
    """
    def __init__(self, question, answer, bg_color=Theme.CARD_BG, radius=[10], **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [14, 12, 14, 12]
        self.spacing = 8
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))

        self.is_expanded = False
        self.question = question
        self.answer = answer
        self.radius_val = radius

        # Arrière-plan carte avec coins arrondis et bordure élégante
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=radius)
            Color(0.85, 0.88, 0.85, 1.0)
            self.border_line = Line(rounded_rectangle=[self.pos[0], self.pos[1], self.size[0], self.size[1], radius[0]], width=1)

        self.bind(size=self._update_graphics, pos=self._update_graphics)

        # En-tête cliquable (Question + Chevron)
        self.header_btn = ClickableRow(orientation='horizontal', size_hint_y=None, spacing=8)
        self.header_btn.bind(minimum_height=self.header_btn.setter('height'))
        self.header_btn.bind(on_release=self.toggle)

        # Label Question
        self.q_label = Label(
            text=f"[b][color=1E592E]Q.[/color]  {self.question}[/b]",
            markup=True,
            font_size='15sp',
            color=Theme.PRIMARY_DARK,
            size_hint_x=0.9,
            size_hint_y=None,
            halign='left',
            valign='middle'
        )
        self.q_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        self.q_label.bind(texture_size=lambda s, v: setattr(s, 'height', max(28, v[1])))

        # Chevron indicateur (▼ replié, ▲ déplié)
        self.icon_label = Label(
            text="▼",
            font_size='13sp',
            color=Theme.PRIMARY_MAIN,
            size_hint=(None, None),
            size=(28, 28),
            halign='center',
            valign='middle'
        )

        self.header_btn.add_widget(self.q_label)
        self.header_btn.add_widget(self.icon_label)
        self.add_widget(self.header_btn)

        # Boîte de réponse (dépliée lors du clic)
        self.answer_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=6, padding=[0, 6, 0, 2])
        self.answer_box.bind(minimum_height=self.answer_box.setter('height'))

        self.a_label = Label(
            text=f"[b][color=47C26B]R.[/color][/b]  {self.answer}",
            markup=True,
            font_size='14sp',
            color=Theme.TEXT_DARK,
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        self.a_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        self.a_label.bind(texture_size=lambda s, v: setattr(s, 'height', v[1]))

        self.answer_box.add_widget(self.a_label)

    def toggle(self, *args):
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            self.icon_label.text = "▲"
            self.icon_label.color = Theme.ACCENT_EXCLUSIVE
            self.add_widget(self.answer_box)
        else:
            self.icon_label.text = "▼"
            self.icon_label.color = Theme.PRIMARY_MAIN
            if self.answer_box in self.children:
                self.remove_widget(self.answer_box)

    def _update_graphics(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size
        r = self.radius_val[0] if self.radius_val else 10
        self.border_line.rounded_rectangle = [self.pos[0], self.pos[1], self.size[0], self.size[1], r]

class TableWidget(BoxLayout):
    """
    Composant Tableau Mobile structuré et responsive.
    Affiche un vrai tableau avec :
    - En-têtes verts foncés (#1E592E) et texte en gras.
    - Lignes alternées (zébrage pour une lisibilité optimale).
    - Bordures arrondies avec séparateurs fins.
    - Colonnes équilibrées et wrapping automatique.
    """
    def __init__(self, headers=None, rows=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.spacing = 1
        self.padding = [0, 6, 0, 8]
        self.bind(minimum_height=self.setter('height'))

        headers = headers or []
        rows = rows or []

        num_cols = max(len(headers), max((len(r) for r in rows), default=0))
        if num_cols == 0:
            return

        with self.canvas.before:
            Color(*Theme.CARD_BG)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[8])
            Color(0.85, 0.88, 0.85, 1.0)
            self.border_line = Line(rounded_rectangle=[self.pos[0], self.pos[1], self.size[0], self.size[1], 8], width=1)
        self.bind(size=self._update_graphics, pos=self._update_graphics)

        col_weight = 1.0 / num_cols

        # 1. En-têtes du tableau
        if headers:
            header_row = BoxLayout(orientation='horizontal', size_hint_y=None, spacing=2, padding=[8, 8, 8, 8])
            header_row.bind(minimum_height=header_row.setter('height'))
            with header_row.canvas.before:
                Color(*Theme.PRIMARY_DARK)
                header_row.bg_rect = RoundedRectangle(size=header_row.size, pos=header_row.pos, radius=[8, 8, 0, 0])
            header_row.bind(
                size=lambda inst, val: setattr(inst.bg_rect, 'size', val),
                pos=lambda inst, val: setattr(inst.bg_rect, 'pos', val)
            )

            padded_headers = list(headers) + [''] * (num_cols - len(headers))
            for h in padded_headers:
                h_text = f"[b]{h}[/b]" if not h.startswith('[b]') else h
                h_lbl = Label(
                    text=h_text,
                    markup=True,
                    font_size='13sp',
                    color=Theme.TEXT_LIGHT,
                    size_hint_x=col_weight,
                    size_hint_y=None,
                    halign='center',
                    valign='middle'
                )
                h_lbl.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
                h_lbl.bind(texture_size=lambda s, v: setattr(s, 'height', max(28, v[1])))
                header_row.add_widget(h_lbl)

            self.add_widget(header_row)

        # 2. Lignes de données
        for idx, row in enumerate(rows):
            is_even = (idx % 2 == 0)
            bg = (0.96, 0.98, 0.96, 1.0) if is_even else (1.0, 1.0, 1.0, 1.0)
            radius = [0, 0, 8, 8] if idx == len(rows) - 1 else [0]

            data_row = BoxLayout(orientation='horizontal', size_hint_y=None, spacing=2, padding=[8, 8, 8, 8])
            data_row.bind(minimum_height=data_row.setter('height'))
            with data_row.canvas.before:
                Color(*bg)
                data_row.bg_rect = RoundedRectangle(size=data_row.size, pos=data_row.pos, radius=radius)
            data_row.bind(
                size=lambda inst, val: setattr(inst.bg_rect, 'size', val),
                pos=lambda inst, val: setattr(inst.bg_rect, 'pos', val)
            )

            padded_row = list(row) + [''] * (num_cols - len(row))
            for cell_text in padded_row:
                c_lbl = Label(
                    text=str(cell_text),
                    markup=True,
                    font_size='13sp',
                    color=Theme.TEXT_DARK,
                    size_hint_x=col_weight,
                    size_hint_y=None,
                    halign='left',
                    valign='middle'
                )
                c_lbl.bind(size=lambda s, v: setattr(s, 'text_size', (max(20, s.width - 4), None)))
                c_lbl.bind(texture_size=lambda s, v: setattr(s, 'height', max(24, v[1])))
                data_row.add_widget(c_lbl)

            self.add_widget(data_row)

    def _update_graphics(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.border_line.rounded_rectangle = [self.pos[0], self.pos[1], self.size[0], self.size[1], 8]

