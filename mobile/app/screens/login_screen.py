from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from ..styles.themes import Theme
from ..services.auth_service import AuthService

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = AuthService()

        with self.canvas.before:
            Color(*Theme.BG_CREAM)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)

        # Title / Header
        title = Label(
            text="[b]Guide du Potager[/b]",
            markup=True,
            font_size='28sp',
            color=Theme.PRIMARY_DARK,
            size_hint_y=None,
            height=60
        )
        subtitle = Label(
            text="Connectez-vous pour accéder au guide",
            font_size='15sp',
            color=Theme.TEXT_MUTED,
            size_hint_y=None,
            height=30
        )
        layout.add_widget(title)
        layout.add_widget(subtitle)

        # Inputs
        self.email_input = TextInput(
            hint_text="Adresse Email",
            multiline=False,
            font_size='16sp',
            size_hint_y=None,
            height=50,
            background_normal='',
            background_color=(1, 1, 1, 1),
            foreground_color=Theme.TEXT_DARK,
            padding=[12, 14, 12, 14]
        )
        self.password_input = TextInput(
            hint_text="Mot de passe",
            password=True,
            multiline=False,
            font_size='16sp',
            size_hint_y=None,
            height=50,
            background_normal='',
            background_color=(1, 1, 1, 1),
            foreground_color=Theme.TEXT_DARK,
            padding=[12, 14, 12, 14]
        )

        layout.add_widget(self.email_input)
        layout.add_widget(self.password_input)

        # Error Message Label
        self.error_label = Label(
            text="",
            color=(0.8, 0.2, 0.2, 1),
            font_size='14sp',
            size_hint_y=None,
            height=30
        )
        layout.add_widget(self.error_label)

        # Login Button
        login_btn = Button(
            text="Se Connecter",
            font_size='17sp',
            size_hint_y=None,
            height=52,
            background_normal='',
            background_color=Theme.PRIMARY_MAIN,
            color=Theme.TEXT_LIGHT
        )
        login_btn.bind(on_release=self.handle_login)
        layout.add_widget(login_btn)

        # Register & Forgot Links
        links_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=80)

        forgot_btn = Button(
            text="Mot de passe oublié ?",
            font_size='14sp',
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=Theme.BROWN_MAIN
        )
        forgot_btn.bind(on_release=self.show_forgot_msg)

        register_link = Button(
            text="Pas encore de compte ? [b]Créer un compte[/b]",
            markup=True,
            font_size='15sp',
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=Theme.PRIMARY_DARK
        )
        register_link.bind(on_release=lambda x: setattr(self.manager, 'current', 'register'))

        links_layout.add_widget(forgot_btn)
        links_layout.add_widget(register_link)
        layout.add_widget(links_layout)

        self.add_widget(layout)

    def handle_login(self, instance):
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()

        if not email or not password:
            self.error_label.text = "Veuillez remplir tous les champs."
            return

        res = self.auth_service.login(email, password)
        if res['success']:
            self.error_label.text = ""
            self.manager.current = 'home'
        else:
            self.error_label.text = "Email ou mot de passe incorrect."

    def show_forgot_msg(self, instance):
        self.error_label.text = "Un email de réinitialisation vous sera envoyé."

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
