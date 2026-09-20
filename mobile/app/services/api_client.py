import httpx
from ..utils.config import Config
from ..utils.storage import LocalStorage

class APIClient:
    def __init__(self):
        self.base_url = Config.API_BASE_URL
        self.storage = LocalStorage()

    def _build_url(self, endpoint):
        return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    def _get_headers(self):
        headers = {'Content-Type': 'application/json'}
        token = self.storage.get('access_token')
        if token:
            headers['Authorization'] = f'Bearer {token}'
        return headers

    def _refresh_token(self):
        refresh = self.storage.get('refresh_token')
        if not refresh:
            return False
        try:
            url = self._build_url('auth/refresh/')
            with httpx.Client(timeout=Config.TIMEOUT) as client:
                res = client.post(url, json={'refresh': refresh})
                if res.status_code == 200:
                    data = res.json()
                    self.storage.save('access_token', data['access'])
                    return True
        except Exception:
            pass
        # Refresh failed: clear stale tokens
        self.storage.clear()
        return False

    def get(self, endpoint, params=None, retry_on_401=True):
        url = self._build_url(endpoint)
        try:
            with httpx.Client(timeout=Config.TIMEOUT) as client:
                response = client.get(url, headers=self._get_headers(), params=params)
                if response.status_code in [200, 201]:
                    return {'success': True, 'data': response.json()}
                elif response.status_code == 401 and retry_on_401:
                    if self._refresh_token():
                        return self.get(endpoint, params=params, retry_on_401=False)
                    self.storage.clear()
                return {'success': False, 'status_code': response.status_code, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def post(self, endpoint, data=None, retry_on_401=True):
        url = self._build_url(endpoint)
        try:
            with httpx.Client(timeout=Config.TIMEOUT) as client:
                response = client.post(url, headers=self._get_headers(), json=data or {})
                if response.status_code in [200, 201]:
                    return {'success': True, 'data': response.json()}
                elif response.status_code == 401 and retry_on_401 and not endpoint.lstrip('/').startswith('auth/'):
                    if self._refresh_token():
                        return self.post(endpoint, data=data, retry_on_401=False)
                    self.storage.clear()
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.json() if 'json' in response.headers.get('content-type', '') else response.text
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def put(self, endpoint, data=None, retry_on_401=True):
        url = self._build_url(endpoint)
        try:
            with httpx.Client(timeout=Config.TIMEOUT) as client:
                response = client.put(url, headers=self._get_headers(), json=data or {})
                if response.status_code in [200, 201]:
                    return {'success': True, 'data': response.json()}
                elif response.status_code == 401 and retry_on_401 and not endpoint.lstrip('/').startswith('auth/'):
                    if self._refresh_token():
                        return self.put(endpoint, data=data, retry_on_401=False)
                    self.storage.clear()
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.json() if 'json' in response.headers.get('content-type', '') else response.text
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def patch(self, endpoint, data=None, retry_on_401=True):
        url = self._build_url(endpoint)
        try:
            with httpx.Client(timeout=Config.TIMEOUT) as client:
                response = client.patch(url, headers=self._get_headers(), json=data or {})
                if response.status_code in [200, 201]:
                    return {'success': True, 'data': response.json()}
                elif response.status_code == 401 and retry_on_401 and not endpoint.lstrip('/').startswith('auth/'):
                    if self._refresh_token():
                        return self.patch(endpoint, data=data, retry_on_401=False)
                    self.storage.clear()
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.json() if 'json' in response.headers.get('content-type', '') else response.text
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def delete(self, endpoint, retry_on_401=True):
        url = self._build_url(endpoint)
        try:
            with httpx.Client(timeout=Config.TIMEOUT) as client:
                response = client.delete(url, headers=self._get_headers())
                if response.status_code in [200, 204]:
                    return {'success': True}
                elif response.status_code == 401 and retry_on_401:
                    if self._refresh_token():
                        return self.delete(endpoint, retry_on_401=False)
                    self.storage.clear()
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
