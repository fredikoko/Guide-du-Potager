from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from ..styles.themes import Theme
from ..components.cards import CardWidget
from ..components.navigation_drawer import NavigationDrawer

class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drawer = None

        with self.canvas.before:
            Color(*Theme.BG_CREAM)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        layout = BoxLayout(orientation='vertical')

        # Header Bar
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
            text="[b]À Propos du Guide[/b]", markup=True, font_size='18sp',
            color=Theme.TEXT_LIGHT, halign='left', valign='middle'
        )
        title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

        home_btn = Button(
            text="ACCUEIL", font_size='12sp', size_hint_x=None, width=70,
            background_normal='', background_color=(0, 0, 0, 0), color=Theme.TEXT_LIGHT
        )
        home_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))

        header.add_widget(menu_btn)
        header.add_widget(title)
        header.add_widget(home_btn)
        layout.add_widget(header)

        # Scrollable Content
        scroll = ScrollView()
        container = BoxLayout(orientation='vertical', size_hint_y=None, padding=15, spacing=15)
        container.bind(minimum_height=container.setter('height'))

        # 1. Hero Card - Mission & Présentation
        hero_card = CardWidget(bg_color=Theme.PRIMARY_DARK)
        hero_title = Label(
            text="[b]🌿 Guide du Potager Tropical[/b]",
            markup=True, font_size='19sp', color=Theme.GOLD_PREMIUM,
            size_hint_y=None, height=35, halign='left'
        )
        hero_title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

        hero_subtitle = Label(
            text="L'application de référence pour le maraîchage agro-écologique & biologique en climat chaud, sahélien, côtier et insulaire.",
            font_size='14sp', color=Theme.TEXT_LIGHT,
            size_hint_y=None, height=55, halign='left'
        )
        hero_subtitle.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

        hero_card.add_widget(hero_title)
        hero_card.add_widget(hero_subtitle)
        container.add_widget(hero_card)

        # Section Header
        sec_label = Label(
            text="[b]✨ Panorama des Fonctionnalités :[/b]",
            markup=True, font_size='17sp', color=Theme.PRIMARY_DARK,
            size_hint_y=None, height=30, halign='left'
        )
        sec_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        container.add_widget(sec_label)

        # Features List
        features = [
            (
                "📖 Guide Pédagogique & Chapitres Détaillés",
                "Apprenez les bases solides du maraîchage tropical : préparation du sol vivant, gestion de l'eau, associations végétales favorables et techniques de fertilisation biologique adaptées aux fortes chaleurs."
            ),
            (
                "📰 Module Blog, Actualités & Conseils de Saison",
                "Restez connecté aux meilleures pratiques agro-écologiques grâce à des articles thématiques complets, des fiches techniques d'experts, des retours d'expérience et un espace d'échange en commentaires."
            ),
            (
                "📅 Simulateur Interactif de Calendrier de Culture",
                "Sélectionnez n'importe quel mois de l'année pour générer sur-mesure la liste des légumes à semer, planter ou récolter, avec filtrage instantané en mémoire (0 ms de latence)."
            ),
            (
                "🥕 Dictionnaire Maraîcher & Fiches Légumes",
                "Consultez les fiches détaillées de dizaines de variétés tropicales : tolérance thermique, besoins en eau, cycles végétatifs, périodes optimales et fiches familles botaniques."
            ),
            (
                "🛠️ Outils Maraîchers de Précision",
                "Guide pratique des équipements maraîchers ergonomiques et respectueux du sol (grelinette, transplantoir, semoirs de précision, toiles d'ombrage et paillage protecteur)."
            ),
            (
                "🩺 Clinique des Plantes : Maladies & Insectes Nuisibles",
                "Diagnostiquez rapidement les ravageurs et maladies tropicales courantes. Accédez à des solutions curatives bio locales : macérations de neem, piment, purins et méthodes de biocontrôle sans chimie de synthèse."
            ),
            (
                "📴 Mode Hors-Ligne Intégré",
                "Consultez l'ensemble du guide, vos légumes et le simulateur directement sur votre parcelle ou au champ, même sans connexion internet ni couverture réseau."
            ),
            (
                "💎 Formules d'Abonnement Premium Flexibles",
                "Débloquez les chapitres d'experts, fiches de traitement et articles exclusifs. Tarification administrable et règlement sécurisé par Mobile Money (Wave, Orange Money, MTN, Moov) ou Carte bancaire."
            )
        ]

        for feat_title, feat_desc in features:
            f_card = CardWidget(bg_color=Theme.CARD_BG)
            lbl_title = Label(
                text=f"[b]{feat_title}[/b]",
                markup=True, font_size='16sp', color=Theme.PRIMARY_MAIN,
                size_hint_y=None, height=28, halign='left'
            )
            lbl_title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

            lbl_desc = Label(
                text=feat_desc,
                font_size='13sp', color=Theme.TEXT_DARK,
                size_hint_y=None, height=58, halign='left'
            )
            lbl_desc.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

            f_card.add_widget(lbl_title)
            f_card.add_widget(lbl_desc)
            container.add_widget(f_card)

        # Call to Action Card
        cta_card = CardWidget(bg_color=Theme.BROWN_DARK)
        cta_lbl = Label(
            text="[b]Prêt à développer un potager résilient et productif ?[/b]",
            markup=True, font_size='16sp', color=Theme.TEXT_LIGHT,
            size_hint_y=None, height=35, halign='center'
        )
        cta_btn = Button(
            text="Explorer les Chapitres du Guide →",
            font_size='15sp', size_hint_y=None, height=48,
            background_normal='', background_color=Theme.GOLD_PREMIUM, color=Theme.TEXT_LIGHT
        )
        cta_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        cta_card.add_widget(cta_lbl)
        cta_card.add_widget(cta_btn)
        container.add_widget(cta_card)

        # Footer version
        footer_lbl = Label(
            text="Guide du Potager Tropical • Version 1.0.0\nDéveloppé pour les passionnés et professionnels du vivant 🌿",
            font_size='12sp', color=Theme.TEXT_MUTED, halign='center',
            size_hint_y=None, height=45
        )
        container.add_widget(footer_lbl)

        scroll.add_widget(container)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def toggle_drawer(self, instance):
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
