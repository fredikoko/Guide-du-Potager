from .api_client import APIClient

class SubscriptionService:
    def __init__(self):
        self.api = APIClient()

    def get_status(self):
        return self.api.get('subscriptions/status/')

    def pay_mobile(self, plan_type, payment_method, phone_number):
        data = {
            'plan_type': plan_type,
            'payment_method': payment_method,
            'phone_number': phone_number
        }
        return self.api.post('subscriptions/mobile-payment/', data)

    def pay_stripe(self, plan_type):
        data = {'plan_type': plan_type}
        return self.api.post('subscriptions/create/', data)

    def initiate_chariow_checkout(self, plan_type, redirect_url=None):
        data = {'plan_type': plan_type}
        if redirect_url:
            data['redirect_url'] = redirect_url
        return self.api.post('subscriptions/chariow/checkout/', data)
