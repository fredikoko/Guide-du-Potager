from .api_client import APIClient
from ..utils.storage import LocalStorage

class CacheService:
    def __init__(self):
        self.storage = LocalStorage()

    def get_cache(self, key):
        return self.storage.get(f"cache_{key}")

    def set_cache(self, key, value):
        self.storage.save(f"cache_{key}", value)

class ContentService:
    def __init__(self):
        self.api = APIClient()
        self.cache = CacheService()

    def get_parts(self):
        res = self.api.get('content/parts/')
        if res.get('success'):
            self.cache.set_cache('parts', res['data'])
            return {'success': True, 'data': res['data']}
        # Fallback to local cache for offline mode
        cached = self.cache.get_cache('parts')
        if cached:
            return {'success': True, 'data': cached, 'from_cache': True}
        return {'success': False, 'error': res.get('error', 'Erreur réseau.')}

    def get_chapter(self, chapter_id):
        res = self.api.get(f'content/chapters/{chapter_id}/')
        if res.get('success'):
            self.cache.set_cache(f'chapter_{chapter_id}', res['data'])
            return {'success': True, 'data': res['data']}
        cached = self.cache.get_cache(f'chapter_{chapter_id}')
        if cached:
            return {'success': True, 'data': cached, 'from_cache': True}
        return {'success': False, 'error': res.get('error', 'Chapitre indisponible.')}
