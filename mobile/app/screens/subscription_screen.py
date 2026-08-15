from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
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
        self.selected_method = 'orange_money'

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
            text="[b]★ Passez à l'expérience Premium ![/b]", markup=True, font_size='18sp',
            color=Theme.GOLD_PREMIUM, size_hint_y=None, height=35, halign='left'
        ))
        features_text = (
            "✓ Accès intégral aux Parties 2 et 3\n"
            "✓ Fiches complètes des Maladies et Insectes\n"
            "✓ Traitements Bio et Solutions préventives\n"
            "✓ Guide des Outils Maraîchers de précision"
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

        # Payment Method Selection (Mobile Payment Afrique de l'Ouest & Stripe)
        pay_card = CardWidget(bg_color=Theme.CARD_BG)
        pay_card.add_widget(Label(
            text="[b]2. Moyen de paiement :[/b]", markup=True, font_size='16sp',
            color=Theme.PRIMARY_DARK, size_hint_y=None, height=30, halign='left'
        ))

        methods = [
            ("Orange Money", "orange_money"),
            ("Wave", "wave"),
            ("MTN Money", "mtn_money"),
            ("Carte Bancaire / Stripe", "stripe"),
        ]

        self.method_buttons = {}
        for title, key in methods:
            btn = Button(
                text=title, font_size='14sp', size_hint_y=None, height=44,
                background_normal='',
                background_color=Theme.PRIMARY_MAIN if key == self.selected_method else (0.9, 0.9, 0.9, 1),
                color=Theme.TEXT_LIGHT if key == self.selected_method else Theme.TEXT_DARK
            )
            btn.bind(on_release=lambda instance, k=key: self.select_method(k))
            self.method_buttons[key] = btn
            pay_card.add_widget(btn)

        # Phone input for mobile payment
        self.phone_input = TextInput(
            hint_text="Numéro de téléphone mobile payment (ex: 771234567)",
            multiline=False, font_size='15sp', size_hint_y=None, height=48,
            background_normal='', background_color=(1, 1, 1, 1), foreground_color=Theme.TEXT_DARK, padding=[10, 12, 10, 12]
        )
        pay_card.add_widget(self.phone_input)

        self.status_msg = Label(
            text="", color=(0.8, 0.2, 0.2, 1), font_size='14sp', size_hint_y=None, height=30
        )
        pay_card.add_widget(self.status_msg)

        confirm_btn = Button(
            text="Confirmer et Payer le Premium", font_size='16sp', size_hint_y=None, height=52,
            background_normal='', background_color=Theme.GOLD_PREMIUM, color=Theme.TEXT_LIGHT
        )
        confirm_btn.bind(on_release=self.process_payment)
        pay_card.add_widget(confirm_btn)

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

    def select_method(self, method):
        self.selected_method = method
        for k, btn in self.method_buttons.items():
            if k == method:
                btn.background_color = Theme.PRIMARY_MAIN
                btn.color = Theme.TEXT_LIGHT
            else:
                btn.background_color = (0.9, 0.9, 0.9, 1)
                btn.color = Theme.TEXT_DARK

        if method == 'stripe':
            self.phone_input.opacity = 0
            self.phone_input.disabled = True
        else:
            self.phone_input.opacity = 1
            self.phone_input.disabled = False

    def process_payment(self, instance):
        if self.selected_method != 'stripe':
            phone = self.phone_input.text.strip()
            if not phone:
                self.status_msg.color = (0.8, 0.2, 0.2, 1)
                self.status_msg.text = "Veuillez entrer votre numéro de téléphone."
                return
            res = self.sub_service.pay_mobile(self.selected_plan, self.selected_method, phone)
        else:
            res = self.sub_service.pay_stripe(self.selected_plan)

        if res.get('success'):
            self.status_msg.color = (0.2, 0.7, 0.3, 1)
            self.status_msg.text = "🎉 Paiement confirmé ! Votre abonnement est actif."
            from ..services.auth_service import AuthService
            AuthService().get_profile()  # Refresh local profile state
        else:
            self.status_msg.color = (0.8, 0.2, 0.2, 1)
            self.status_msg.text = str(res.get('error', 'Échec du traitement du paiement.'))

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
