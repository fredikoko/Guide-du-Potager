from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from ..styles.themes import Theme
from ..services.auth_service import AuthService
from ..services.subscription_service import SubscriptionService
from ..components.cards import CardWidget
from ..components.navigation_drawer import NavigationDrawer

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = AuthService()
        self.sub_service = SubscriptionService()
        self.drawer = None

        with self.canvas.before:
            Color(*Theme.BG_CREAM)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        layout = BoxLayout(orientation='vertical')

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, padding=10, spacing=10)
        with header.canvas.before:
            Color(*Theme.HEADER_BG)
            self.header_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=self._update_header_rect, pos=self._update_header_rect)

        menu_btn = Button(
            text="≡", font_size='26sp', size_hint_x=None, width=50,
            background_normal='', background_color=(0, 0, 0, 0), color=Theme.TEXT_LIGHT
        )
        menu_btn.bind(on_release=self.toggle_drawer)

        title = Label(
            text="[b]Mon Profil & Paramètres[/b]", markup=True, font_size='18sp',
            color=Theme.TEXT_LIGHT, halign='left', valign='middle'
        )
        title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

        header.add_widget(menu_btn)
        header.add_widget(title)
        layout.add_widget(header)

        scroll = ScrollView()
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, padding=18, spacing=15)
        self.container.bind(minimum_height=self.container.setter('height'))
        scroll.add_widget(self.container)

        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self):
        self.load_profile_info()

    def load_profile_info(self):
        self.container.clear_widgets()

        res = self.auth_service.get_profile()
        if res.get('success'):
            user = res.get('user', {})
        else:
            user = self.auth_service.get_current_user()
            if not user:
                self.manager.current = 'login'
                return

        profile = user.get('profile', {}) if isinstance(user, dict) else {}

        # 1. Card Édition du Profil
        card_user = CardWidget(bg_color=Theme.CARD_BG)
        card_user.add_widget(Label(
            text="[b]👤 Modifier mes Informations[/b]", markup=True, font_size='17sp',
            color=Theme.PRIMARY_DARK, size_hint_y=None, height=35, halign='left'
        ))

        email_text = user.get('email', '') if isinstance(user, dict) else ''
        username_text = user.get('username', '') if isinstance(user, dict) else ''
        first_name_text = user.get('first_name', '') if isinstance(user, dict) else ''
        last_name_text = user.get('last_name', '') if isinstance(user, dict) else ''
        phone_text = profile.get('phone_number', '') if isinstance(profile, dict) else ''

        # Email (Lecture seule)
        card_user.add_widget(Label(
            text=f"[b]Adresse E-mail :[/b] {email_text}", markup=True, font_size='14sp',
            color=Theme.TEXT_MUTED, size_hint_y=None, height=28, halign='left'
        ))

        # Username
        card_user.add_widget(Label(
            text="[b]Nom d'utilisateur :[/b]", markup=True, font_size='14sp',
            color=Theme.TEXT_DARK, size_hint_y=None, height=24, halign='left'
        ))
        self.username_input = TextInput(
            text=username_text, multiline=False, font_size='14sp', size_hint_y=None, height=42
        )
        card_user.add_widget(self.username_input)

        # Prénom
        card_user.add_widget(Label(
            text="[b]Prénom :[/b]", markup=True, font_size='14sp',
            color=Theme.TEXT_DARK, size_hint_y=None, height=24, halign='left'
        ))
        self.first_name_input = TextInput(
            text=first_name_text, multiline=False, font_size='14sp', size_hint_y=None, height=42
        )
        card_user.add_widget(self.first_name_input)

        # Nom
        card_user.add_widget(Label(
            text="[b]Nom :[/b]", markup=True, font_size='14sp',
            color=Theme.TEXT_DARK, size_hint_y=None, height=24, halign='left'
        ))
        self.last_name_input = TextInput(
            text=last_name_text, multiline=False, font_size='14sp', size_hint_y=None, height=42
        )
        card_user.add_widget(self.last_name_input)

        # Téléphone
        card_user.add_widget(Label(
            text="[b]Numéro de téléphone :[/b]", markup=True, font_size='14sp',
            color=Theme.TEXT_DARK, size_hint_y=None, height=24, halign='left'
        ))
        self.phone_input = TextInput(
            text=phone_text, multiline=False, font_size='14sp', size_hint_y=None, height=42
        )
        card_user.add_widget(self.phone_input)

        # Feedback Label pour Mise à jour du Profil
        self.profile_msg_lbl = Label(
            text="", markup=True, font_size='13sp', size_hint_y=None, height=0, halign='left'
        )
        card_user.add_widget(self.profile_msg_lbl)

        # Bouton Sauvegarder
        save_btn = Button(
            text="Enregistrer le profil", font_size='15sp', size_hint_y=None, height=46,
            background_normal='', background_color=Theme.PRIMARY_MAIN, color=Theme.TEXT_LIGHT
        )
        save_btn.bind(on_release=self.save_profile_changes)
        card_user.add_widget(save_btn)

        self.container.add_widget(card_user)

        # 2. Card Statut Abonnement
        card_sub = CardWidget(bg_color=Theme.CARD_BG)
        card_sub.add_widget(Label(
            text="[b]⭐ Statut de l'Abonnement[/b]", markup=True, font_size='17sp',
            color=Theme.PRIMARY_DARK, size_hint_y=None, height=35, halign='left'
        ))

        is_sub = profile.get('subscription_active', False) if isinstance(profile, dict) else False
        sub_status_text = "[color=8AB86C][b]ACTIF (Premium)[/b][/color]" if is_sub else "[color=855E42][b]INACTIF (Accès Gratuit)[/b][/color]"
        end_date = profile.get('subscription_end_date', 'N/A') if isinstance(profile, dict) else 'N/A'

        card_sub.add_widget(Label(
            text=f"Statut : {sub_status_text}", markup=True, font_size='15sp',
            color=Theme.TEXT_DARK, size_hint_y=None, height=30, halign='left'
        ))
        if is_sub:
            card_sub.add_widget(Label(
                text=f"Date d'expiration : {end_date[:10] if end_date else 'N/A'}", markup=True, font_size='14sp',
                color=Theme.TEXT_MUTED, size_hint_y=None, height=25, halign='left'
            ))

        sub_btn = Button(
            text="Gérer / Obtenir l'Abonnement Premium", font_size='15sp', size_hint_y=None, height=46,
            background_normal='', background_color=Theme.GOLD_PREMIUM, color=Theme.TEXT_LIGHT
        )
        sub_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'subscription'))
        card_sub.add_widget(sub_btn)

        self.container.add_widget(card_sub)

        # 3. Card Sécurité & Changer le Mot de Passe
        card_sec = CardWidget(bg_color=Theme.CARD_BG)
        card_sec.add_widget(Label(
            text="[b]🔒 Sécurité (Changer de mot de passe)[/b]", markup=True, font_size='17sp',
            color=Theme.PRIMARY_DARK, size_hint_y=None, height=35, halign='left'
        ))

        card_sec.add_widget(Label(
            text="[b]Mot de passe actuel :[/b]", markup=True, font_size='14sp',
            color=Theme.TEXT_DARK, size_hint_y=None, height=24, halign='left'
        ))
        self.old_pass_input = TextInput(
            password=True, multiline=False, font_size='14sp', size_hint_y=None, height=42
        )
        card_sec.add_widget(self.old_pass_input)

        card_sec.add_widget(Label(
            text="[b]Nouveau mot de passe :[/b]", markup=True, font_size='14sp',
            color=Theme.TEXT_DARK, size_hint_y=None, height=24, halign='left'
        ))
        self.new_pass_input = TextInput(
            password=True, multiline=False, font_size='14sp', size_hint_y=None, height=42
        )
        card_sec.add_widget(self.new_pass_input)

        # Feedback Label Password
        self.pass_msg_lbl = Label(
            text="", markup=True, font_size='13sp', size_hint_y=None, height=0, halign='left'
        )
        card_sec.add_widget(self.pass_msg_lbl)

        pass_btn = Button(
            text="Modifier le mot de passe", font_size='15sp', size_hint_y=None, height=46,
            background_normal='', background_color=Theme.PRIMARY_DARK, color=Theme.TEXT_LIGHT
        )
        pass_btn.bind(on_release=self.change_user_password)
        card_sec.add_widget(pass_btn)

        self.container.add_widget(card_sec)

        # 4. Card Déconnexion
        card_actions = CardWidget(bg_color=Theme.CARD_BG)
        logout_btn = Button(
            text="Se déconnecter", font_size='15sp', size_hint_y=None, height=46,
            background_normal='', background_color=Theme.BROWN_MAIN, color=Theme.TEXT_LIGHT
        )
        logout_btn.bind(on_release=lambda x: self.handle_logout())
        card_actions.add_widget(logout_btn)

        self.container.add_widget(card_actions)

    def save_profile_changes(self, instance):
        username = self.username_input.text.strip()
        first_name = self.first_name_input.text.strip()
        last_name = self.last_name_input.text.strip()
        phone_number = self.phone_input.text.strip()

        if not username:
            self.profile_msg_lbl.text = "[color=B32626]⚠️ Le nom d'utilisateur est obligatoire.[/color]"
            self.profile_msg_lbl.height = 25
            return

        res = self.auth_service.update_profile(
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number
        )

        if res.get('success'):
            self.profile_msg_lbl.text = "[color=1E592E]✅ Profil mis à jour avec succès ![/color]"
            self.profile_msg_lbl.height = 25
        else:
            err = res.get('error', 'Erreur de mise à jour.')
            self.profile_msg_lbl.text = f"[color=B32626]⚠️ {err}[/color]"
            self.profile_msg_lbl.height = 25

    def change_user_password(self, instance):
        old_pass = self.old_pass_input.text.strip()
        new_pass = self.new_pass_input.text.strip()

        if not old_pass or not new_pass:
            self.pass_msg_lbl.text = "[color=B32626]⚠️ Veuillez remplir les deux champs de mot de passe.[/color]"
            self.pass_msg_lbl.height = 25
            return

        res = self.auth_service.change_password(old_pass, new_pass)

        if res.get('success'):
            self.old_pass_input.text = ""
            self.new_pass_input.text = ""
            self.pass_msg_lbl.text = "[color=1E592E]✅ Mot de passe modifié avec succès ![/color]"
            self.pass_msg_lbl.height = 25
        else:
            err = res.get('error', 'Échec de la modification du mot de passe.')
            self.pass_msg_lbl.text = f"[color=B32626]⚠️ {err}[/color]"
            self.pass_msg_lbl.height = 25

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
        self.auth_service.logout()
        self.close_drawer()
        self.manager.current = 'login'

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
