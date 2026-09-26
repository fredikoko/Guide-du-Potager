from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from ..styles.themes import Theme
from ..components.cards import CardWidget
from ..components.navigation_drawer import NavigationDrawer
from ..services.content_service import ContentService
from ..utils.html_parser import HTMLParser

class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drawer = None
        self.content_service = ContentService()

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
        self.scroll = ScrollView()
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, padding=15, spacing=15)
        self.container.bind(minimum_height=self.container.setter('height'))

        self.scroll.add_widget(self.container)
        layout.add_widget(self.scroll)
        self.add_widget(layout)

        # Affichage initial avec valeurs par défaut
        self.render_content(self._get_default_data())

    def on_enter(self):
        # Rafraîchir les données depuis l'API ou le cache hors-ligne
        self.load_data()

    def load_data(self):
        res = self.content_service.get_about()
        if res.get('success') and res.get('data'):
            self.render_content(res['data'])

    def _get_default_data(self):
        return {
            'title': "Guide du Potager Tropical",
            'subtitle': "L'application de référence pour le maraîchage tropical : pratiques conventionnelles, raisonnées & agro-écologiques.",
            'mission_title': "Notre Mission & Approche Maraîchère",
            'mission_text': (
                "Le Guide du Potager Tropical accompagne les maraîchers urbains, "
                "périurbains et ruraux vers une production performante, rentable et résiliente "
                "face aux réalités climatiques tropicales.\n\n"
                "Nos articles et fiches techniques intègrent l'ensemble des approches agronomiques : "
                "les itinéraires techniques conventionnels (gestion raisonnée des engrais minéraux NPK, protection "
                "phytosanitaire homologuée et conduite intensive) ainsi que les méthodes agro-écologiques et biologiques "
                "(amendements organiques, biopesticides locaux au neem, santé des sols vivants et paillage protecteur). "
                "Chaque producteur y trouve les protocoles, les dosages rigoureux et les conseils pratiques adaptés "
                "à ses objectifs de rendement."
            ),
            'pillar_1_title': "Gestion de l'Eau & Irrigation",
            'pillar_1_desc': "Goutte-à-goutte de précision, micro-aspersion, paillage protecteur et pilotage hydrique sous forte évapotranspiration.",
            'pillar_2_title': "Nutrition des Sols & Rendements",
            'pillar_2_desc': "Plans de fertilisation équilibrés combinant apports minéraux raisonnés (NPK, urée) et amendements organiques pour maximiser les récoltes.",
            'pillar_3_title': "Protection Raisonnée & Biocontrôle",
            'pillar_3_desc': "Stratégies de défense des cultures articulant traitements conventionnels homologués, barrières physiques et biopesticides locaux.",
            'contact_title': "Assistance & Communauté",
            'contact_text': "Pour toute question agronomique, assistance technique sur vos abonnements ou partenariat d'exploitation, notre équipe est à votre écoute :",
            'contact_email': "contact@guidedupotager.com",
            'contact_phone': "+221 77 000 00 00",
            'app_version': "1.0.0"
        }

    def _create_auto_label(self, text, font_size='13sp', color=None, is_bold=False, is_markup=True):
        if color is None:
            color = Theme.TEXT_DARK
        txt = f"[b]{text}[/b]" if (is_bold and not text.startswith('[b]')) else text
        lbl = Label(
            text=txt,
            markup=is_markup,
            font_size=font_size,
            color=color,
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        lbl.bind(width=lambda s, val: setattr(s, 'text_size', (val, None)))
        lbl.bind(texture_size=lambda s, val: setattr(s, 'height', max(val[1] + 8, 25)))
        return lbl

    def render_content(self, data):
        self.container.clear_widgets()

        # 1. Hero Card - Titre & Slogan de l'application
        hero_card = CardWidget(bg_color=Theme.PRIMARY_DARK)
        hero_title = self._create_auto_label(
            f"[b]🌿 {data.get('title', 'Guide du Potager Tropical')}[/b]",
            font_size='19sp', color=Theme.ACCENT_EXCLUSIVE
        )
        hero_subtitle = self._create_auto_label(
            data.get('subtitle', ''),
            font_size='14sp', color=Theme.TEXT_LIGHT
        )
        hero_card.add_widget(hero_title)
        hero_card.add_widget(hero_subtitle)
        self.container.add_widget(hero_card)

        # 2. Mission Card (Éditable depuis l'admin)
        mission_card = CardWidget(bg_color=Theme.CARD_BG)
        mission_title = self._create_auto_label(
            f"[b]🌱 {data.get('mission_title', 'Notre Mission')}[/b]",
            font_size='17sp', color=Theme.PRIMARY_MAIN
        )
        mission_content_markup = HTMLParser.to_markup(data.get('mission_text', ''))
        mission_text_lbl = self._create_auto_label(
            mission_content_markup,
            font_size='13sp', color=Theme.TEXT_DARK
        )
        mission_card.add_widget(mission_title)
        mission_card.add_widget(mission_text_lbl)
        self.container.add_widget(mission_card)

        # 3. Les 3 Piliers Agro-écologiques
        pillars_header = self._create_auto_label(
            "[b]🌾 Les 3 Piliers de notre Méthode :[/b]",
            font_size='16sp', color=Theme.PRIMARY_DARK
        )
        self.container.add_widget(pillars_header)

        pillars = [
            ("💧 " + data.get('pillar_1_title', "Gestion de l'Eau"), data.get('pillar_1_desc', '')),
            ("🪱 " + data.get('pillar_2_title', "Sols Vivants"), data.get('pillar_2_desc', '')),
            ("🛡️ " + data.get('pillar_3_title', "Zéro Chimique"), data.get('pillar_3_desc', '')),
        ]
        for p_title, p_desc in pillars:
            p_card = CardWidget(bg_color=Theme.CARD_BG)
            p_lbl_title = self._create_auto_label(p_title, font_size='15sp', color=Theme.PRIMARY_MAIN, is_bold=True)
            p_lbl_desc = self._create_auto_label(p_desc, font_size='13sp', color=Theme.TEXT_DARK)
            p_card.add_widget(p_lbl_title)
            p_card.add_widget(p_lbl_desc)
            self.container.add_widget(p_card)

        # 4. Panorama des Fonctionnalités
        sec_label = self._create_auto_label(
            "[b]✨ Panorama des Fonctionnalités :[/b]",
            font_size='16sp', color=Theme.PRIMARY_DARK
        )
        self.container.add_widget(sec_label)

        features = [
            (
                "📖 Guide Pédagogique & Chapitres Détaillés",
                "Apprenez les bases solides du maraîchage tropical : préparation du sol vivant, gestion de l'eau, associations végétales favorables et techniques de fertilisation biologique adaptées aux fortes chaleurs."
            ),
            (
                "📰 Module Blog, Actualités & Conseils de Saison",
                "Restez connecté aux meilleures pratiques maraîchères grâce à des articles thématiques complets : itinéraires conventionnels (engrais minéraux, produits homologués) et approches bio (biopesticides, composts)."
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
                "Diagnostiquez rapidement les ravageurs et maladies tropicales. Accédez aux protocoles de traitement conventionnels raisonnés ainsi qu'aux biopesticides locaux et méthodes de biocontrôle."
            ),
            (
                "📴 Mode Hors-Ligne Intégré",
                "Consultez l'ensemble du guide, vos légumes et le simulateur directement sur votre parcelle ou au champ, même sans connexion internet ni couverture réseau."
            ),
            (
                "💎 Formules d'Abonnement Flexibles",
                "Débloquez l'ensemble des chapitres d'experts, fiches de traitement et articles exclusifs. Tarification administrable et règlement sécurisé par Mobile Money (Wave, Orange Money, MTN, Moov) ou Carte bancaire."
            )
        ]

        for feat_title, feat_desc in features:
            f_card = CardWidget(bg_color=Theme.CARD_BG)
            lbl_title = self._create_auto_label(feat_title, font_size='15sp', color=Theme.PRIMARY_MAIN, is_bold=True)
            lbl_desc = self._create_auto_label(feat_desc, font_size='13sp', color=Theme.TEXT_DARK)
            f_card.add_widget(lbl_title)
            f_card.add_widget(lbl_desc)
            self.container.add_widget(f_card)

        # 5. Carte Assistance & Contact (Éditable depuis l'admin)
        contact_card = CardWidget(bg_color=Theme.CARD_BG)
        contact_title = self._create_auto_label(
            f"[b]📞 {data.get('contact_title', 'Assistance & Communauté')}[/b]",
            font_size='16sp', color=Theme.PRIMARY_MAIN
        )
        contact_desc = self._create_auto_label(
            data.get('contact_text', ''),
            font_size='13sp', color=Theme.TEXT_DARK
        )
        contact_email = self._create_auto_label(
            f"✉️ Email support : [b]{data.get('contact_email', 'contact@guidedupotager.com')}[/b]",
            font_size='13sp', color=Theme.PRIMARY_DARK
        )
        contact_phone = self._create_auto_label(
            f"💬 WhatsApp Maraîcher : [b]{data.get('contact_phone', '+221 77 000 00 00')}[/b]",
            font_size='13sp', color=Theme.ACCENT_EXCLUSIVE
        )
        contact_card.add_widget(contact_title)
        contact_card.add_widget(contact_desc)
        contact_card.add_widget(contact_email)
        contact_card.add_widget(contact_phone)
        self.container.add_widget(contact_card)

        # 6. Call to Action Card
        cta_card = CardWidget(bg_color=Theme.BROWN_DARK)
        cta_lbl = self._create_auto_label(
            "[b]Prêt à développer un potager résilient et productif ?[/b]",
            font_size='15sp', color=Theme.TEXT_LIGHT, is_bold=True
        )
        cta_btn = Button(
            text="Explorer les Chapitres du Guide →",
            font_size='14sp', size_hint_y=None, height=46,
            background_normal='', background_color=Theme.ACCENT_EXCLUSIVE, color=Theme.TEXT_LIGHT
        )
        cta_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        cta_card.add_widget(cta_lbl)
        cta_card.add_widget(cta_btn)
        self.container.add_widget(cta_card)

        # 7. Footer version
        version = data.get('app_version', '1.0.0')
        title_name = data.get('title', 'Guide du Potager Tropical')
        footer_lbl = Label(
            text=f"{title_name} • Version {version}\nDéveloppé pour les passionnés et professionnels du vivant 🌿",
            font_size='12sp', color=Theme.TEXT_MUTED, halign='center',
            size_hint_y=None, height=45
        )
        self.container.add_widget(footer_lbl)

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

