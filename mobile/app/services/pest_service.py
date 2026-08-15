from .api_client import APIClient

class PestService:
    def __init__(self):
        self.api = APIClient()

    def get_diseases(self, search=None):
        params = {'search': search} if search else None
        return self.api.get('pests/diseases/', params=params)

    def get_disease_detail(self, disease_id):
        return self.api.get(f'pests/diseases/{disease_id}/')

    def get_insects(self, search=None):
        params = {'search': search} if search else None
        return self.api.get('pests/insects/', params=params)

    def get_insect_detail(self, insect_id):
        return self.api.get(f'pests/insects/{insect_id}/')
