from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from ..styles.themes import Theme
from ..services.subscription_service import SubscriptionService
from ..components.cards import CardWidget

class SubscriptionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sub_service = SubscriptionService()
        self.selected_plan = 'seasonal'  # Défaut recommandé
        self.plan_buttons = {}
        self.plans_data = {}
        self.confirm_btn = None
        self.refresh_btn = None
        self.status_msg = None

        with self.canvas.before:
            Color(*Theme.BG_CREAM)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        layout = BoxLayout(orientation='vertical')

        # Header bar avec adaptation responsive
        self.header = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, padding=[10, 5, 10, 5], spacing=10)
        with self.header.canvas.before:
            Color(*Theme.HEADER_BG)
            self.header_rect = Rectangle(size=self.header.size, pos=self.header.pos)
        self.header.bind(size=self._update_header_rect, pos=self._update_header_rect)

        back_btn = Button(
            text="← Retour", font_size='15sp', size_hint_x=None, width=85,
            background_normal='', background_color=(0, 0, 0, 0), color=Theme.TEXT_LIGHT
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))

        title = Label(
            text="[b]Abonnement & Pass VIP[/b]", markup=True, font_size='18sp',
            color=Theme.TEXT_LIGHT, halign='left', valign='middle'
        )
        title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

        self.header.add_widget(back_btn)
        self.header.add_widget(title)
        layout.add_widget(self.header)

        # Scrollview avec conteneur responsive
        scroll = ScrollView()
        self.container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[12, 12, 12, 24],
            spacing=15
        )
        self.container.bind(minimum_height=self.container.setter('height'))
        scroll.add_widget(self.container)

        layout.add_widget(scroll)
        self.add_widget(layout)

    def _create_responsive_label(self, text, font_size='13sp', color=None, is_markup=True, halign='left'):
        """Crée un label Kivy dont la hauteur s'adapte automatiquement au wrapping du texte."""
        if color is None:
            color = Theme.TEXT_DARK
        lbl = Label(
            text=text,
            markup=is_markup,
            font_size=font_size,
            color=color,
            size_hint_y=None,
            halign=halign,
            valign='top'
        )
        lbl.bind(width=lambda s, val: setattr(s, 'text_size', (val, None)))
        lbl.bind(texture_size=lambda s, val: setattr(s, 'height', max(val[1] + 6, 20)))
        return lbl

    def _on_status_msg_texture(self, instance, val):
        """Ajuste dynamiquement la hauteur du message de statut."""
        if instance.text.strip():
            instance.height = max(val[1] + 16, 38)
        else:
            instance.height = 0

    def on_enter(self):
        self.build_subscription_view()

    def build_subscription_view(self):
        self.container.clear_widgets()

        # ======================================================================
        # 0. ÉTAT D'ABONNEMENT ACTIF (Si l'utilisateur est déjà abonné)
        # ======================================================================
        try:
            status_res = self.sub_service.get_status()
            if status_res.get('subscription_active'):
                end_raw = status_res.get('subscription_end_date', '')
                date_str = f" jusqu'au {end_raw[:10]}" if end_raw else ""
                active_card = CardWidget(bg_color=(0.12, 0.42, 0.22, 1.0))
                active_title = self._create_responsive_label(
                    f"[b]⭐ Votre Pass Maraîcher est ACTIF{date_str} ![/b]",
                    font_size='16sp', color=Theme.ACCENT_EXCLUSIVE
                )
                active_desc = self._create_responsive_label(
                    "Vous bénéficiez de l'accès illimité à tous les chapitres avancés, fiches et simulateur. "
                    "Vous pouvez renouveler ou prolonger votre formule ci-dessous :",
                    font_size='12sp', color=Theme.BG_CREAM
                )
                active_card.add_widget(active_title)
                active_card.add_widget(active_desc)
                self.container.add_widget(active_card)
        except Exception:
            pass

        # ======================================================================
        # 1. BANNIÈRE HERO RESPONSIVE
        # ======================================================================
        banner_card = CardWidget(bg_color=Theme.PRIMARY_DARK)

        banner_title = self._create_responsive_label(
            "[b]Accédez à l'expérience intégrale ![/b]",
            font_size='17sp', color=Theme.ACCENT_EXCLUSIVE
        )
        banner_subtitle = self._create_responsive_label(
            "Sécurisez vos récoltes, optimisez vos fertilisations et protégez vos cultures maraîchères sous climat tropical.",
            font_size='12sp', color=Theme.BG_CREAM
        )
        features_text = (
            "• [b]Chapitres complets[/b] du manuel technique (Parties 2 et 3)\n"
            "• [b]Articles exclusifs[/b] du Blog & protocoles conventionnels raisonnés\n"
            "• [b]Fiches détaillées[/b] des Maladies & Insectes ravageurs tropicaux\n"
            "• [b]Biopesticides locaux[/b] & recettes bio au neem\n"
            "• [b]Guide des Outils[/b] de précision & fiches consultables hors-ligne\n\n"
            "[color=47C26B][b]💡 Rentabilisez votre pass dès votre première récolte en évitant les pertes ![/b][/color]"
        )
        features_lbl = self._create_responsive_label(
            features_text, font_size='13sp', color=Theme.TEXT_LIGHT
        )

        banner_card.add_widget(banner_title)
        banner_card.add_widget(banner_subtitle)
        banner_card.add_widget(features_lbl)
        self.container.add_widget(banner_card)

        # ======================================================================
        # 2. CHOIX DE LA FORMULE (Boutons-Cartes responsives)
        # ======================================================================
        plan_card = CardWidget(bg_color=Theme.CARD_BG)
        sec1_title = self._create_responsive_label(
            "[b]1. Choisissez votre formule :[/b]",
            font_size='16sp', color=Theme.PRIMARY_DARK
        )
        plan_card.add_widget(sec1_title)

        plans_res = self.sub_service.get_plans()
        plans = []
        if plans_res.get('success'):
            raw = plans_res.get('data', [])
            plans = raw.get('results', raw) if isinstance(raw, dict) else raw

        if not plans:
            # Fallback par défaut si hors-ligne sans cache
            plans = [
                {'plan_type': 'monthly', 'name': 'Pass 1 Mois', 'price': '2500.00', 'formatted_price': '2 500', 'currency': 'XOF', 'approx_eur': '~4€', 'discount_badge': '', 'duration_days': 30, 'description': 'Découverte sans engagement', 'is_featured': False},
                {'plan_type': 'seasonal', 'name': 'Pass Saison (3 Mois)', 'price': '5000.00', 'formatted_price': '5 000', 'currency': 'XOF', 'approx_eur': '~8€', 'discount_badge': '⭐ Recommandé', 'duration_days': 90, 'description': '1 cycle complet de culture maraîchère', 'is_featured': True},
                {'plan_type': 'yearly', 'name': 'Pass Annuel', 'price': '15000.00', 'formatted_price': '15 000', 'currency': 'XOF', 'approx_eur': '~23€', 'discount_badge': '-50%', 'duration_days': 365, 'description': 'Accès illimité toute l\'année', 'is_featured': False},
            ]

        # Sélectionner la formule recommandée par défaut si disponible
        featured_plan = next((p['plan_type'] for p in plans if p.get('is_featured')), None)
        if featured_plan:
            self.selected_plan = featured_plan
        elif plans and self.selected_plan not in [p['plan_type'] for p in plans]:
            self.selected_plan = plans[0]['plan_type']

        self.plan_buttons = {}
        self.plans_data = {p['plan_type']: p for p in plans}

        plans_container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        plans_container.bind(minimum_height=plans_container.setter('height'))

        for p in plans:
            pt = p['plan_type']
            btn = Button(
                markup=True,
                font_size='13sp',
                halign='left',
                valign='middle',
                size_hint_y=None,
                background_normal=''
            )
            # Liaison pour adaptation responsive de la largeur du texte et de la hauteur du bouton
            btn.bind(width=lambda s, val: setattr(s, 'text_size', (val - 26, None)))
            btn.bind(texture_size=lambda s, val: setattr(s, 'height', max(val[1] + 24, 72)))
            btn.bind(on_release=lambda instance, plan_code=pt: self.select_plan(plan_code))

            self.plan_buttons[pt] = btn
            plans_container.add_widget(btn)

        plan_card.add_widget(plans_container)
        self.container.add_widget(plan_card)

        # ======================================================================
        # 3. PAIEMENT SÉCURISÉ AVEC CHARIOW
        # ======================================================================
        pay_card = CardWidget(bg_color=Theme.CARD_BG)
        sec2_title = self._create_responsive_label(
            "[b]2. Paiement sécurisé via Chariow :[/b]",
            font_size='16sp', color=Theme.PRIMARY_DARK
        )
        pay_card.add_widget(sec2_title)

        info_text = (
            "Réglez en toute sécurité via la passerelle officielle Chariow par Mobile Money ou Carte bancaire :"
        )
        pay_desc = self._create_responsive_label(info_text, font_size='13sp', color=Theme.TEXT_DARK)
        pay_card.add_widget(pay_desc)

        # Badges des modes de paiement supportés
        methods_label = self._create_responsive_label(
            "[b]📱 Mobile Money :[/b] Wave • Orange Money • MTN MoMo • Moov\n"
            "[b]💳 Cartes :[/b] Visa • Mastercard internationales",
            font_size='12sp', color=Theme.PRIMARY_DARK
        )
        pay_card.add_widget(methods_label)

        # Message de statut dynamique (hauteur 0 quand vide pour ne pas créer de blanc)
        self.status_msg = Label(
            text="",
            markup=True,
            font_size='13sp',
            color=(0.85, 0.2, 0.2, 1),
            size_hint_y=None,
            height=0,
            halign='center',
            valign='middle'
        )
        self.status_msg.bind(width=lambda s, val: setattr(s, 'text_size', (val - 20, None)))
        self.status_msg.bind(texture_size=self._on_status_msg_texture)
        pay_card.add_widget(self.status_msg)

        # Bouton principal de paiement responsive avec montant dynamique
        self.confirm_btn = Button(
            text=self._get_confirm_btn_text(),
            markup=True,
            font_size='14sp',
            size_hint_y=None,
            height=52,
            background_normal='',
            background_color=Theme.ACCENT_EXCLUSIVE,
            color=Theme.TEXT_LIGHT,
            halign='center',
            valign='middle'
        )
        self.confirm_btn.bind(width=lambda s, val: setattr(s, 'text_size', (val - 20, None)))
        self.confirm_btn.bind(texture_size=lambda s, val: setattr(s, 'height', max(val[1] + 22, 52)))
        self.confirm_btn.bind(on_release=self.process_payment)
        pay_card.add_widget(self.confirm_btn)

        # Bouton de rafraîchissement (caché à hauteur 0 tant qu'aucun paiement n'est initié)
        self.refresh_btn = Button(
            text="🔄 Actualiser mon statut d'abonnement",
            markup=True,
            font_size='13sp',
            size_hint_y=None,
            height=0,
            opacity=0,
            disabled=True,
            background_normal='',
            background_color=Theme.PRIMARY_MAIN,
            color=Theme.TEXT_LIGHT,
            halign='center',
            valign='middle'
        )
        self.refresh_btn.bind(width=lambda s, val: setattr(s, 'text_size', (val - 20, None)))
        self.refresh_btn.bind(on_release=self.refresh_status)
        pay_card.add_widget(self.refresh_btn)

        self.container.add_widget(pay_card)

        # Mise à jour graphique des boutons de formules
        self._update_plan_buttons_ui()

    def _get_confirm_btn_text(self):
        selected_data = self.plans_data.get(self.selected_plan, {})
        price = selected_data.get('formatted_price', selected_data.get('price', ''))
        curr = selected_data.get('currency', 'XOF')
        if price:
            return f"[b]Payer {price} {curr} avec Chariow →[/b]"
        return "[b]Payer avec Chariow (Mobile Money / Carte) →[/b]"

    def _update_plan_buttons_ui(self):
        for pt, btn in self.plan_buttons.items():
            p = self.plans_data.get(pt, {})
            name = p.get('name', pt.capitalize())
            badge = p.get('discount_badge', '')
            approx = f" ({p.get('approx_eur')})" if p.get('approx_eur') else ""
            price_txt = f"{p.get('formatted_price', p.get('price', ''))} {p.get('currency', 'XOF')}{approx}"
            duration = p.get('duration_days')
            duration_str = f" • {duration} jours" if duration else ""
            desc = p.get('description', '')

            is_selected = (pt == self.selected_plan)

            if is_selected:
                badge_str = f"  [color=47C26B][b][{badge}][/b][/color]" if badge else ""
                desc_str = f"\n[size=11sp][color=E8F5E9]{desc}[/color][/size]" if desc else ""
                btn.text = (
                    f"[b][color=FFFFFF]✔ {name}[/color][/b]{badge_str}\n"
                    f"[size=15sp][b][color=47C26B]{price_txt}[/color][/b][/size][size=11sp][color=D0E8D7]{duration_str}[/color][/size]"
                    f"{desc_str}"
                )
                btn.background_color = Theme.PRIMARY_DARK
                btn.color = Theme.TEXT_LIGHT
            else:
                badge_str = f"  [color=3D7A42][b][{badge}][/b][/color]" if badge else ""
                desc_str = f"\n[size=11sp][color=555555]{desc}[/color][/size]" if desc else ""
                btn.text = (
                    f"[b][color=1E592E]○ {name}[/color][/b]{badge_str}\n"
                    f"[size=14sp][b][color=1E592E]{price_txt}[/color][/b][/size][size=11sp][color=777777]{duration_str}[/color][/size]"
                    f"{desc_str}"
                )
                if p.get('is_featured'):
                    btn.background_color = (0.95, 0.98, 0.95, 1.0)
                else:
                    btn.background_color = (0.93, 0.94, 0.93, 1.0)
                btn.color = Theme.TEXT_DARK

    def select_plan(self, plan_code):
        self.selected_plan = plan_code
        self._update_plan_buttons_ui()
        if hasattr(self, 'confirm_btn') and self.confirm_btn:
            self.confirm_btn.text = self._get_confirm_btn_text()

    def process_payment(self, instance):
        self.status_msg.color = (0.2, 0.5, 0.8, 1)
        self.status_msg.text = "Génération du lien sécurisé Chariow..."

        res = self.sub_service.initiate_chariow_checkout(self.selected_plan)
        if res.get('success') and res.get('checkout_url'):
            import webbrowser
            webbrowser.open(res['checkout_url'])
            self.status_msg.color = (0.1, 0.6, 0.2, 1)
            self.status_msg.text = "Lien de paiement Chariow ouvert dans votre navigateur.\nUne fois validé, cliquez ci-dessous pour actualiser :"
            self.refresh_btn.height = 46
            self.refresh_btn.opacity = 1
            self.refresh_btn.disabled = False
        elif res.get('step') == 'completed':
            self.status_msg.color = (0.1, 0.6, 0.2, 1)
            self.status_msg.text = "🎉 Félicitations ! Votre abonnement a été activé avec succès !"
            from ..services.auth_service import AuthService
            AuthService().get_profile()
        else:
            self.status_msg.color = (0.85, 0.2, 0.2, 1)
            err_msg = res.get('error', 'Erreur d\'initialisation du paiement Chariow.')
            self.status_msg.text = f"⚠️ {err_msg}"

    def refresh_status(self, instance):
        from ..services.auth_service import AuthService
        AuthService().get_profile()
        status_res = self.sub_service.get_status()
        if status_res.get('subscription_active'):
            self.status_msg.color = (0.1, 0.6, 0.2, 1)
            self.status_msg.text = "🎉 Félicitations ! Votre abonnement VIP est désormais actif !"
            self.refresh_btn.height = 0
            self.refresh_btn.opacity = 0
            self.refresh_btn.disabled = True
            self.build_subscription_view()
        else:
            self.status_msg.color = (0.85, 0.45, 0.1, 1)
            self.status_msg.text = "Paiement en cours de confirmation. Patientez quelques secondes et réessayez."

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
