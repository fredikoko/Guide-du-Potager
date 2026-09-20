from .api_client import APIClient
from ..utils.storage import LocalStorage

class SubscriptionService:
    def __init__(self):
        self.api = APIClient()
        self.storage = LocalStorage()

    def get_status(self):
        return self.api.get('subscriptions/status/')

    def get_plans(self):
        res = self.api.get('subscriptions/plans/?page_size=all')
        if res.get('success'):
            self.storage.save('cache_subscription_plans', res['data'])
            return res
        cached = self.storage.get('cache_subscription_plans')
        if cached:
            return {'success': True, 'data': cached, 'from_cache': True}
        return res

    def initiate_chariow_checkout(self, plan_type, redirect_url=None):
        data = {'plan_type': plan_type}
        if redirect_url:
            data['redirect_url'] = redirect_url
        return self.api.post('subscriptions/chariow/checkout/', data)
