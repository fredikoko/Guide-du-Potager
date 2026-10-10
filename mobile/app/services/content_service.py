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
        res = self.api.get('content/parts/?page_size=all')
        if res.get('success'):
            self.cache.set_cache('parts', res['data'])
            return {'success': True, 'data': res['data']}
        # Fallback to local cache for offline mode
        cached = self.cache.get_cache('parts')
        if cached:
            return {'success': True, 'data': cached, 'from_cache': True}
        return {'success': False, 'error': res.get('error', 'Erreur réseau.')}

    def get_chapters(self, part_id=None, search=None):
        url = 'content/chapters/?'
        params = []
        if part_id is not None:
            params.append(f'part={part_id}')
        if search:
            import urllib.parse
            params.append(f'search={urllib.parse.quote(search)}')
        url += '&'.join(params)

        res = self.api.get(url)
        if res.get('success'):
            if part_id is None and not search:
                self.cache.set_cache('chapters', res['data'])
            return {'success': True, 'data': res['data']}

        # Fallback hors-ligne
        cached_chapters = self.cache.get_cache('chapters')
        if not cached_chapters:
            # Reconstitution depuis cache_parts
            cached_parts = self.cache.get_cache('parts') or []
            if isinstance(cached_parts, dict) and 'results' in cached_parts:
                cached_parts = cached_parts['results']
            flattened = []
            for p in cached_parts:
                for c in p.get('chapters', []):
                    item = dict(c)
                    item['part'] = p['id']
                    item['part_title'] = p['title']
                    item['part_order'] = p['order']
                    flattened.append(item)
            cached_chapters = flattened

        if cached_chapters:
            filtered = cached_chapters
            if isinstance(filtered, dict) and 'results' in filtered:
                filtered = filtered['results']
            if part_id is not None:
                filtered = [c for c in filtered if c.get('part') == part_id or c.get('part_id') == part_id]
            if search:
                s = search.lower()
                filtered = [c for c in filtered if s in (c.get('title') or '').lower() or s in (c.get('part_title') or '').lower()]
            return {'success': True, 'data': filtered, 'from_cache': True}

        return {'success': False, 'error': res.get('error', 'Chapitres indisponibles.')}

    def get_chapter(self, chapter_id):
        res = self.api.get(f'content/chapters/{chapter_id}/')
        if res.get('success'):
            self.cache.set_cache(f'chapter_{chapter_id}', res['data'])
            return {'success': True, 'data': res['data']}
        cached = self.cache.get_cache(f'chapter_{chapter_id}')
        if cached:
            return {'success': True, 'data': cached, 'from_cache': True}
        return {'success': False, 'error': res.get('error', 'Chapitre indisponible.')}

    def get_about(self):
        res = self.api.get('content/about/')
        if res.get('success'):
            self.cache.set_cache('about_page', res['data'])
            return {'success': True, 'data': res['data']}
        cached = self.cache.get_cache('about_page')
        if cached:
            return {'success': True, 'data': cached, 'from_cache': True}
        return {'success': False, 'error': res.get('error', 'Page À Propos indisponible.')}

