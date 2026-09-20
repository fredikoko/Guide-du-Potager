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
            text="[b]Abonnement Premium[/b]", markup=True, font_size='18sp',
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
            text="[b]Passez à l'expérience Premium ![/b]", markup=True, font_size='18sp',
            color=Theme.GOLD_PREMIUM, size_hint_y=None, height=35, halign='left'
        ))
        features_text = (
            "• Accès intégral aux Parties 2 et 3\n"
            "• Fiches complètes des Maladies et Insectes\n"
            "• Traitements Bio et Solutions préventives\n"
            "• Guide des Outils Maraîchers de précision"
        )
        banner_card.add_widget(Label(
            text=features_text, color=Theme.TEXT_LIGHT, font_size='14sp', size_hint_y=None, height=90, halign='left'
        ))
        self.container.add_widget(banner_card)

        # Plan Selection
        plan_card = CardWidget(bg_color=Theme.CARD_BG)
        plan_card.add_widget(Label(
            text="[b]1. Choisir votre formule :[/b]", markup=True, font_size='16sp',
            color=Theme.PRIMARY_DARK, size_hint_y=None, height=30, halign='left'
        ))

        plans_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)

        self.monthly_btn = Button(
            text="Mensuel\n2 500 XOF (~4€)", font_size='13sp', halign='center',
            background_normal='', background_color=Theme.PRIMARY_MAIN, color=Theme.TEXT_LIGHT
        )
        self.monthly_btn.bind(on_release=lambda x: self.select_plan('monthly'))

        self.yearly_btn = Button(
            text="Annuel (-30%)\n20 000 XOF (~30€)", font_size='13sp', halign='center',
            background_normal='', background_color=Theme.CARD_BG, color=Theme.TEXT_DARK
        )
        self.yearly_btn.bind(on_release=lambda x: self.select_plan('yearly'))

        plans_layout.add_widget(self.monthly_btn)
        plans_layout.add_widget(self.yearly_btn)
        plan_card.add_widget(plans_layout)
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
            text="Payer avec Chariow (Sécurisé)", font_size='16sp', size_hint_y=None, height=52,
            background_normal='', background_color=Theme.GOLD_PREMIUM, color=Theme.TEXT_LIGHT
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
        if plan == 'monthly':
            self.monthly_btn.background_color = Theme.PRIMARY_MAIN
            self.monthly_btn.color = Theme.TEXT_LIGHT
            self.yearly_btn.background_color = (0.9, 0.9, 0.9, 1)
            self.yearly_btn.color = Theme.TEXT_DARK
        else:
            self.yearly_btn.background_color = Theme.PRIMARY_MAIN
            self.yearly_btn.color = Theme.TEXT_LIGHT
            self.monthly_btn.background_color = (0.9, 0.9, 0.9, 1)
            self.monthly_btn.color = Theme.TEXT_DARK

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
            self.status_msg.text = "🎉 Félicitations ! Votre abonnement Premium est maintenant actif !"
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
