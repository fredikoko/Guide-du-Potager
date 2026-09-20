from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from ..styles.themes import Theme
from ..services.auth_service import AuthService
from ..components.otp_popup import OTPVerificationPopup

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = AuthService()

        with self.canvas.before:
            Color(*Theme.BG_CREAM)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        layout = BoxLayout(orientation='vertical', padding=30, spacing=12)

        title = Label(
            text="[b]Créer un Compte[/b]",
            markup=True,
            font_size='24sp',
            color=Theme.PRIMARY_DARK,
            size_hint_y=None,
            height=50
        )
        layout.add_widget(title)

        self.email_input = TextInput(
            hint_text="Email", multiline=False, font_size='15sp', size_hint_y=None, height=48,
            background_normal='', background_color=(1, 1, 1, 1), foreground_color=Theme.TEXT_DARK, padding=[10, 12, 10, 12]
        )
        self.username_input = TextInput(
            hint_text="Nom d'utilisateur", multiline=False, font_size='15sp', size_hint_y=None, height=48,
            background_normal='', background_color=(1, 1, 1, 1), foreground_color=Theme.TEXT_DARK, padding=[10, 12, 10, 12]
        )
        self.phone_input = TextInput(
            hint_text="Téléphone (ex: +221770000000)", multiline=False, font_size='15sp', size_hint_y=None, height=48,
            background_normal='', background_color=(1, 1, 1, 1), foreground_color=Theme.TEXT_DARK, padding=[10, 12, 10, 12]
        )
        self.password_input = TextInput(
            hint_text="Mot de passe", password=True, multiline=False, font_size='15sp', size_hint_y=None, height=48,
            background_normal='', background_color=(1, 1, 1, 1), foreground_color=Theme.TEXT_DARK, padding=[10, 12, 10, 12]
        )

        layout.add_widget(self.email_input)
        layout.add_widget(self.username_input)
        layout.add_widget(self.phone_input)
        layout.add_widget(self.password_input)

        self.status_label = Label(
            text="", color=(0.8, 0.2, 0.2, 1), font_size='14sp', size_hint_y=None, height=30
        )
        layout.add_widget(self.status_label)

        register_btn = Button(
            text="S'Inscrire", font_size='17sp', size_hint_y=None, height=52,
            background_normal='', background_color=Theme.PRIMARY_MAIN, color=Theme.TEXT_LIGHT
        )
        register_btn.bind(on_release=self.handle_register)
        layout.add_widget(register_btn)

        back_btn = Button(
            text="Déjà un compte ? [b]Se connecter[/b]", markup=True, font_size='15sp',
            background_normal='', background_color=(0, 0, 0, 0), color=Theme.BROWN_MAIN, size_hint_y=None, height=40
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'login'))
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def handle_register(self, instance):
        email = self.email_input.text.strip()
        username = self.username_input.text.strip()
        phone = self.phone_input.text.strip()
        password = self.password_input.text.strip()

        if not email or not username or not password:
            self.status_label.color = (0.8, 0.2, 0.2, 1)
            self.status_label.text = "Veuillez remplir les champs obligatoires."
            return

        self.status_label.color = Theme.PRIMARY_DARK
        self.status_label.text = "Création du compte et envoi du code..."

        res = self.auth_service.register(email, username, password, phone)
        if res.get('success'):
            self.status_label.text = ""
            self.open_otp_popup(email)
        else:
            err = res.get('error', 'Erreur d\'inscription.')
            if isinstance(err, dict):
                messages = []
                for k, v in err.items():
                    if isinstance(v, list):
                        messages.append(f"{v[0]}")
                    else:
                        messages.append(f"{v}")
                err = " ".join(messages)
            self.status_label.color = (0.8, 0.2, 0.2, 1)
            self.status_label.text = str(err)

    def open_otp_popup(self, email):
        popup = OTPVerificationPopup(
            email=email,
            on_confirm_callback=self.on_otp_confirm,
            on_resend_callback=self.on_otp_resend,
            title_text="Activation de votre compte",
            purpose="registration"
        )
        popup.open()

    def on_otp_confirm(self, code, popup):
        res = self.auth_service.verify_registration(popup.email, code)
        if res.get('success'):
            popup.dismiss()
            self.status_label.color = (0.2, 0.7, 0.3, 1)
            self.status_label.text = "Compte confirmé avec succès !"
            self.manager.current = 'home'
        else:
            err = res.get('error', 'Code invalide ou expiré.')
            if isinstance(err, dict):
                first_val = list(err.values())[0]
                err = first_val[0] if isinstance(first_val, list) else first_val
            popup.set_error(str(err))

    def on_otp_resend(self, email, purpose, popup):
        res = self.auth_service.resend_verification_code(email, purpose=purpose)
        if res.get('success'):
            popup.set_success("Nouveau code envoyé avec succès.")
        else:
            err = res.get('error', "Impossible de renvoyer le code.")
            popup.set_error(str(err))

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
