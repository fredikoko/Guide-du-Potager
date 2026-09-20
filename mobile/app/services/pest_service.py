from .api_client import APIClient
from ..utils.storage import LocalStorage

class PestService:
    def __init__(self):
        self.api = APIClient()
        self.storage = LocalStorage()

    def get_diseases(self, search=None):
        params = {'page_size': 'all'}
        if search:
            params['search'] = search
        res = self.api.get('pests/diseases/', params=params)
        if res.get('success'):
            if not search:
                self.storage.save('cache_diseases_all', res['data'])
            return res
        if not search:
            cached = self.storage.get('cache_diseases_all')
            if cached:
                return {'success': True, 'data': cached, 'from_cache': True}
        return res

    def get_disease_detail(self, disease_id):
        res = self.api.get(f'pests/diseases/{disease_id}/')
        if res.get('success'):
            self.storage.save(f'cache_disease_{disease_id}', res['data'])
            return res
        cached = self.storage.get(f'cache_disease_{disease_id}')
        if cached:
            return {'success': True, 'data': cached, 'from_cache': True}
        return res

    def get_insects(self, search=None):
        params = {'page_size': 'all'}
        if search:
            params['search'] = search
        res = self.api.get('pests/insects/', params=params)
        if res.get('success'):
            if not search:
                self.storage.save('cache_insects_all', res['data'])
            return res
        if not search:
            cached = self.storage.get('cache_insects_all')
            if cached:
                return {'success': True, 'data': cached, 'from_cache': True}
        return res

    def get_insect_detail(self, insect_id):
        res = self.api.get(f'pests/insects/{insect_id}/')
        if res.get('success'):
            self.storage.save(f'cache_insect_{insect_id}', res['data'])
            return res
        cached = self.storage.get(f'cache_insect_{insect_id}')
        if cached:
            return {'success': True, 'data': cached, 'from_cache': True}
        return res
