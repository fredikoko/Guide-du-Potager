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
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, padding=20, spacing=15)
        self.container.bind(minimum_height=self.container.setter('height'))
        scroll.add_widget(self.container)

        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self):
        self.load_profile_info()

    def load_profile_info(self):
        self.container.clear_widgets()

        user = self.auth_service.get_current_user()
        if not user:
            res = self.auth_service.get_profile()
            user = res.get('user', {})

        profile = user.get('profile', {}) if isinstance(user, dict) else {}

        # 1. Card Informations Personnelles
        card_user = CardWidget(bg_color=Theme.CARD_BG)
        card_user.add_widget(Label(
            text="[b]◆ Informations Personnelles[/b]", markup=True, font_size='17sp',
            color=Theme.PRIMARY_DARK, size_hint_y=None, height=35, halign='left'
        ))

        email_text = user.get('email', 'N/A') if isinstance(user, dict) else 'N/A'
        username_text = user.get('username', 'N/A') if isinstance(user, dict) else 'N/A'
        phone_text = profile.get('phone_number', '')

        card_user.add_widget(Label(
            text=f"[b]Email :[/b] {email_text}", markup=True, font_size='15sp',
            color=Theme.TEXT_DARK, size_hint_y=None, height=30, halign='left'
        ))
        card_user.add_widget(Label(
            text=f"[b]Nom d'utilisateur :[/b] {username_text}", markup=True, font_size='15sp',
            color=Theme.TEXT_DARK, size_hint_y=None, height=30, halign='left'
        ))

        self.container.add_widget(card_user)

        # 2. Card Statut Abonnement
        card_sub = CardWidget(bg_color=Theme.CARD_BG)
        card_sub.add_widget(Label(
            text="[b]⭐ Statut de l'Abonnement[/b]", markup=True, font_size='17sp',
            color=Theme.PRIMARY_DARK, size_hint_y=None, height=35, halign='left'
        ))

        is_sub = profile.get('subscription_active', False)
        sub_status_text = "[color=8AB86C][b]ACTIF (Premium)[/b][/color]" if is_sub else "[color=855E42][b]INACTIF (Accès Gratuit)[/b][/color]"
        end_date = profile.get('subscription_end_date', 'N/A')

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

        # 3. Card Modification Mot de passe & Déconnexion
        card_actions = CardWidget(bg_color=Theme.CARD_BG)
        card_actions.add_widget(Label(
            text="[b]⚙️ Sécurité & Compte[/b]", markup=True, font_size='17sp',
            color=Theme.PRIMARY_DARK, size_hint_y=None, height=35, halign='left'
        ))

        logout_btn = Button(
            text="Déconnexion", font_size='15sp', size_hint_y=None, height=46,
            background_normal='', background_color=Theme.BROWN_MAIN, color=Theme.TEXT_LIGHT
        )
        logout_btn.bind(on_release=lambda x: self.handle_logout())
        card_actions.add_widget(logout_btn)

        self.container.add_widget(card_actions)

    def toggle_drawer(self, instance):
        if not self.drawer:
            self.drawer = NavigationDrawer(screen_manager=self.manager, logout_callback=self.handle_logout)
            self.add_widget(self.drawer)
        else:
            self.remove_widget(self.drawer)
            self.drawer = None

    def handle_logout(self):
        self.auth_service.logout()
        if self.drawer:
            self.remove_widget(self.drawer)
            self.drawer = None
        self.manager.current = 'login'

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
