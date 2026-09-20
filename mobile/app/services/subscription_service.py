from .api_client import APIClient

class SubscriptionService:
    def __init__(self):
        self.api = APIClient()

    def get_status(self):
        return self.api.get('subscriptions/status/')

    def initiate_chariow_checkout(self, plan_type, redirect_url=None):
        data = {'plan_type': plan_type}
        if redirect_url:
            data['redirect_url'] = redirect_url
        return self.api.post('subscriptions/chariow/checkout/', data)
