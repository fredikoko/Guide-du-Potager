from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from ..styles.themes import Theme

class OTPVerificationPopup(Popup):
    def __init__(self, email, on_confirm_callback, on_resend_callback=None, title_text="Code de Confirmation E-mail", purpose="registration", **kwargs):
        super().__init__(**kwargs)
        self.email = email
        self.on_confirm_callback = on_confirm_callback
        self.on_resend_callback = on_resend_callback
        self.purpose = purpose

        self.title = title_text
        self.title_size = '17sp'
        self.title_color = Theme.TEXT_LIGHT
        self.background_color = (0.1, 0.22, 0.13, 0.95)
        self.size_hint = (0.9, None)
        self.height = 360
        self.auto_dismiss = False

        layout = BoxLayout(orientation='vertical', padding=16, spacing=12)
        with layout.canvas.before:
            Color(*Theme.BG_CREAM)
            self.rect = RoundedRectangle(size=layout.size, pos=layout.pos, radius=[8, 8, 8, 8])
        layout.bind(size=self._update_rect, pos=self._update_rect)

        # Info message
        self.info_lbl = Label(
            text=f"Un code de validation à [b]6 chiffres[/b] a été envoyé à l'adresse :\n[color=1E592E][b]{self.email}[/b][/color]\n(Valable 15 minutes)",
            markup=True,
            color=Theme.TEXT_DARK,
            font_size='13sp',
            halign='center',
            size_hint_y=None,
            height=60
        )
        self.info_lbl.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        layout.add_widget(self.info_lbl)

        # Code TextInput
        self.code_input = TextInput(
            hint_text="Entrez le code à 6 chiffres",
            multiline=False,
            font_size='20sp',
            size_hint_y=None,
            height=48,
            halign='center'
        )
        layout.add_widget(self.code_input)

        # Status / Feedback label
        self.status_lbl = Label(
            text="",
            markup=True,
            font_size='13sp',
            size_hint_y=None,
            height=26,
            halign='center'
        )
        layout.add_widget(self.status_lbl)

        # Confirm Button
        confirm_btn = Button(
            text="Valider la confirmation",
            font_size='15sp',
            size_hint_y=None,
            height=46,
            background_normal='',
            background_color=Theme.PRIMARY_MAIN,
            color=Theme.TEXT_LIGHT
        )
        confirm_btn.bind(on_release=self._handle_confirm)
        layout.add_widget(confirm_btn)

        # Resend & Cancel Buttons row
        actions_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)

        resend_btn = Button(
            text="Renvoyer le code",
            font_size='13sp',
            background_normal='',
            background_color=Theme.BROWN_MAIN,
            color=Theme.TEXT_LIGHT
        )
        resend_btn.bind(on_release=self._handle_resend)

        cancel_btn = Button(
            text="Fermer",
            font_size='13sp',
            background_normal='',
            background_color=(0.7, 0.7, 0.7, 1),
            color=Theme.TEXT_DARK
        )
        cancel_btn.bind(on_release=lambda x: self.dismiss())

        actions_box.add_widget(resend_btn)
        actions_box.add_widget(cancel_btn)
        layout.add_widget(actions_box)

        self.content = layout

    def set_error(self, message):
        self.status_lbl.text = f"[color=B32626]⚠️ {message}[/color]"

    def set_success(self, message):
        self.status_lbl.text = f"[color=1E592E]✅ {message}[/color]"

    def _handle_confirm(self, instance):
        code = self.code_input.text.strip()
        if not code:
            self.set_error("Veuillez saisir le code reçu.")
            return
        if len(code) != 6 or not code.isdigit():
            self.set_error("Le code doit comporter 6 chiffres.")
            return
        if self.on_confirm_callback:
            self.on_confirm_callback(code, self)

    def _handle_resend(self, instance):
        if self.on_resend_callback:
            self.on_resend_callback(self.email, self.purpose, self)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
