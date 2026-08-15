from .api_client import APIClient

class GlossaryService:
    def __init__(self):
        self.api = APIClient()

    def get_tools(self, category=None, search=None):
        params = {}
        if category:
            params['category'] = category
        if search:
            params['search'] = search
        return self.api.get('glossary/tools/', params=params)

    def get_families(self):
        return self.api.get('glossary/families/')

    def get_vegetables(self, family_id=None, search=None):
        params = {}
        if family_id:
            params['family'] = family_id
        if search:
            params['search'] = search
        return self.api.get('glossary/vegetables/', params=params)
