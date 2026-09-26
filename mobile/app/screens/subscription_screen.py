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
        self.selected_plan = 'monthly'

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

        back_btn = Button(
            text="← Retour", font_size='16sp', size_hint_x=None, width=90,
            background_normal='', background_color=(0, 0, 0, 0), color=Theme.TEXT_LIGHT
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))

        title = Label(
            text="[b]Abonnement & Pass[/b]", markup=True, font_size='18sp',
            color=Theme.TEXT_LIGHT, halign='left', valign='middle'
        )
        title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

        header.add_widget(back_btn)
        header.add_widget(title)
        layout.add_widget(header)

        scroll = ScrollView()
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, padding=20, spacing=15)
        self.container.bind(minimum_height=self.container.setter('height'))
        scroll.add_widget(self.container)

        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self):
        self.build_subscription_view()

    def build_subscription_view(self):
        self.container.clear_widgets()

        # Banner Card
        banner_card = CardWidget(bg_color=Theme.PRIMARY_DARK)
        banner_card.add_widget(Label(
            text="[b]Accédez à l'expérience intégrale ![/b]", markup=True, font_size='18sp',
            color=Theme.ACCENT_EXCLUSIVE, size_hint_y=None, height=35, halign='left'
        ))
        features_text = (
            "• Accès intégral aux chapitres avancés (Parties 2 et 3)\n"
            "• Articles exclusifs du Blog & analyses maraîchères d'experts\n"
            "• Fiches complètes des Maladies et Insectes ravageurs\n"
            "• Soins conventionnels raisonnés, Biopesticides & Recettes locales\n"
            "• Guide des Outils Maraîchers de précision & fiches hors-ligne\n"
            "\n"
            "[color=47C26B][b]💡 Rentabilisez votre pass dès votre première récolte en évitant les pertes ![/b][/color]"
        )
        banner_card.add_widget(Label(
            text=features_text, markup=True, color=Theme.TEXT_LIGHT, font_size='13sp', size_hint_y=None, height=140, halign='left'
        ))
        self.container.add_widget(banner_card)

        # Plan Selection (Chargement dynamique des prix et formules configurés dans l'admin Django)
        plan_card = CardWidget(bg_color=Theme.CARD_BG)
        plan_card.add_widget(Label(
            text="[b]1. Choisir votre formule :[/b]", markup=True, font_size='16sp',
            color=Theme.PRIMARY_DARK, size_hint_y=None, height=30, halign='left'
        ))

        plans_res = self.sub_service.get_plans()
        plans = []
        if plans_res.get('success'):
            raw = plans_res.get('data', [])
            plans = raw.get('results', raw) if isinstance(raw, dict) else raw

        if not plans:
            # Fallback par défaut si hors-ligne sans cache
            plans = [
                {'plan_type': 'monthly', 'name': 'Pass 1 Mois', 'price': '2500.00', 'currency': 'XOF', 'approx_eur': '~4€', 'discount_badge': '', 'description': 'Découverte sans engagement', 'is_featured': False},
                {'plan_type': 'seasonal', 'name': 'Pass Saison (3 Mois)', 'price': '5000.00', 'currency': 'XOF', 'approx_eur': '~8€', 'discount_badge': '⭐ Recommandé', 'description': '1 cycle complet de culture maraîchère', 'is_featured': True},
                {'plan_type': 'yearly', 'name': 'Pass Annuel', 'price': '15000.00', 'currency': 'XOF', 'approx_eur': '~23€', 'discount_badge': '-50%', 'description': 'Accès illimité toute l\'année', 'is_featured': False},
            ]

        # Sélectionner par défaut la formule recommandée si disponible
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
            name = p.get('name', pt.capitalize())
            badge = p.get('discount_badge', '')
            approx = f" ({p.get('approx_eur')})" if p.get('approx_eur') else ""
            price_txt = f"{p.get('formatted_price', p.get('price', ''))} {p.get('currency', 'XOF')}{approx}"
            desc = p.get('description', '')

            badge_str = f"  [b][color=47C26B]{badge}[/color][/b]" if badge else ""
            desc_str = f"  •  [size=12sp]{desc}[/size]" if desc else ""
            btn_label = f"[b]{name}[/b]{badge_str}\n[b]{price_txt}[/b]{desc_str}"

            btn = Button(
                text=btn_label, markup=True, font_size='13sp', halign='center', valign='middle',
                size_hint_y=None, height=62, background_normal='',
                background_color=Theme.PRIMARY_MAIN if pt == self.selected_plan else (0.92, 0.94, 0.92, 1),
                color=Theme.TEXT_LIGHT if pt == self.selected_plan else Theme.TEXT_DARK
            )
            btn.bind(on_release=lambda instance, plan_code=pt: self.select_plan(plan_code))
            self.plan_buttons[pt] = btn
            plans_container.add_widget(btn)

        plan_card.add_widget(plans_container)
        self.container.add_widget(plan_card)

        # Payment Card (Chariow Exclusive)
        pay_card = CardWidget(bg_color=Theme.CARD_BG)
        pay_card.add_widget(Label(
            text="[b]2. Paiement sécurisé avec Chariow :[/b]", markup=True, font_size='16sp',
            color=Theme.PRIMARY_DARK, size_hint_y=None, height=30, halign='left'
        ))

        info_text = (
            "Réglez en toute sécurité via la passerelle officielle Chariow :\n"
            "• Mobile Money (Afrique de l'Ouest & Centrale) : Wave, Orange Money, MTN MoMo, Moov\n"
            "• Carte bancaire internationale (Visa, Mastercard)"
        )
        pay_card.add_widget(Label(
            text=info_text, font_size='13sp', color=Theme.TEXT_DARK, size_hint_y=None, height=65, halign='left'
        ))

        self.status_msg = Label(
            text="", color=(0.8, 0.2, 0.2, 1), font_size='14sp', size_hint_y=None, height=45
        )
        pay_card.add_widget(self.status_msg)

        confirm_btn = Button(
            text="Payer avec Chariow (Mobile Money / Carte)", font_size='15sp', size_hint_y=None, height=52,
            background_normal='', background_color=Theme.ACCENT_EXCLUSIVE, color=Theme.TEXT_LIGHT
        )
        confirm_btn.bind(on_release=self.process_payment)
        pay_card.add_widget(confirm_btn)

        self.refresh_btn = Button(
            text="🔄 Actualiser mon statut d'abonnement", font_size='14sp', size_hint_y=None, height=44,
            background_normal='', background_color=Theme.PRIMARY_MAIN, color=Theme.TEXT_LIGHT,
            opacity=0, disabled=True
        )
        self.refresh_btn.bind(on_release=self.refresh_status)
        pay_card.add_widget(self.refresh_btn)

        self.container.add_widget(pay_card)

    def select_plan(self, plan):
        self.selected_plan = plan
        for pt, btn in self.plan_buttons.items():
            if pt == plan:
                btn.background_color = Theme.PRIMARY_MAIN
                btn.color = Theme.TEXT_LIGHT
            else:
                p_data = self.plans_data.get(pt, {})
                # Si recommandé mais non sélectionné, léger fond chaleureux
                bg = (0.97, 0.95, 0.90, 1) if p_data.get('is_featured') else (0.92, 0.94, 0.92, 1)
                btn.background_color = bg
                btn.color = Theme.TEXT_DARK

    def process_payment(self, instance):
        res = self.sub_service.initiate_chariow_checkout(self.selected_plan)
        if res.get('success') and res.get('checkout_url'):
            import webbrowser
            webbrowser.open(res['checkout_url'])
            self.status_msg.color = (0.2, 0.7, 0.3, 1)
            self.status_msg.text = "Lien de paiement Chariow ouvert.\nUne fois validé, cliquez ci-dessous pour actualiser votre profil."
            self.refresh_btn.opacity = 1
            self.refresh_btn.disabled = False
        elif res.get('step') == 'completed':
            self.status_msg.color = (0.2, 0.7, 0.3, 1)
            self.status_msg.text = "🎉 Abonnement activé avec succès !"
            from ..services.auth_service import AuthService
            AuthService().get_profile()
        else:
            self.status_msg.color = (0.8, 0.2, 0.2, 1)
            self.status_msg.text = str(res.get('error', 'Erreur d\'initialisation Chariow.'))

    def refresh_status(self, instance):
        from ..services.auth_service import AuthService
        AuthService().get_profile()
        status_res = self.sub_service.get_status()
        if status_res.get('subscription_active'):
            self.status_msg.color = (0.2, 0.7, 0.3, 1)
            self.status_msg.text = "🎉 Félicitations ! Votre abonnement est maintenant actif !"
            self.refresh_btn.opacity = 0
            self.refresh_btn.disabled = True
        else:
            self.status_msg.color = (0.8, 0.5, 0.1, 1)
            self.status_msg.text = "Paiement non détecté. Patientez quelques secondes et réessayez."

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
