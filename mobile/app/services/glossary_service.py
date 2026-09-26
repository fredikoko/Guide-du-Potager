from .api_client import APIClient
from ..utils.storage import LocalStorage

class GlossaryService:
    def __init__(self):
        self.api = APIClient()
        self.storage = LocalStorage()

    def get_tools(self, category=None, search=None):
        params = {'page_size': 'all'}
        if category:
            params['category'] = category
        if search:
            params['search'] = search
        res = self.api.get('glossary/tools/', params=params)
        if res.get('success'):
            if not category and not search:
                self.storage.save('cache_tools_all', res['data'])
            return res
        # Fallback hors-ligne
        if not category and not search:
            cached = self.storage.get('cache_tools_all')
            if cached:
                return {'success': True, 'data': cached, 'from_cache': True}
        return res

    def get_tool_detail(self, tool_id):
        res = self.api.get(f'glossary/tools/{tool_id}/')
        if res.get('success'):
            self.storage.save(f'cache_tool_{tool_id}', res['data'])
            return res
        cached = self.storage.get(f'cache_tool_{tool_id}')
        if cached:
            return {'success': True, 'data': cached, 'from_cache': True}
        return res

    def get_families(self):
        res = self.api.get('glossary/families/', params={'page_size': 'all'})
        if res.get('success'):
            self.storage.save('cache_families_all', res['data'])
            return res
        cached = self.storage.get('cache_families_all')
        if cached:
            return {'success': True, 'data': cached, 'from_cache': True}
        return res

    def get_vegetables(self, family_id=None, search=None):
        params = {'page_size': 'all'}
        if family_id:
            params['family'] = family_id
        if search:
            params['search'] = search
        res = self.api.get('glossary/vegetables/', params=params)
        if res.get('success'):
            if not family_id and not search:
                self.storage.save('cache_vegetables_all', res['data'])
            return res
        if not family_id and not search:
            cached = self.storage.get('cache_vegetables_all')
            if cached:
                return {'success': True, 'data': cached, 'from_cache': True}
        return res

    def get_calendar_entries(self, action=None, month=None, vegetable_id=None):
        params = {'page_size': 'all'}
        if action:
            params['action'] = action
        if month:
            params['month'] = month
        if vegetable_id:
            params['vegetable'] = vegetable_id
        res = self.api.get('glossary/calendar/', params=params)
        cache_key = f"cache_calendar_{action or 'all'}_{month or 'all'}"
        if res.get('success'):
            self.storage.save(cache_key, res['data'])
            return res
        cached = self.storage.get(cache_key)
        if cached:
            return {'success': True, 'data': cached, 'from_cache': True}
        return res

