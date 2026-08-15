from .api_client import APIClient
from ..utils.storage import LocalStorage

class AuthService:
    def __init__(self):
        self.api = APIClient()
        self.storage = LocalStorage()

    def is_authenticated(self):
        token = self.storage.get('access_token')
        return bool(token)

    def get_current_user(self):
        return self.storage.get('current_user')

    def login(self, email, password):
        res = self.api.post('auth/login/', {'email': email, 'password': password})
        if res.get('success'):
            data = res['data']
            self.storage.save('access_token', data['access'])
            self.storage.save('refresh_token', data['refresh'])
            self.storage.save('current_user', data['user'])
            return {'success': True, 'user': data['user']}
        return {'success': False, 'error': res.get('error', 'Échec de connexion.')}

    def register(self, email, username, password, phone_number=''):
        data = {
            'email': email,
            'username': username,
            'password': password,
            'password_confirm': password,
            'phone_number': phone_number
        }
        res = self.api.post('auth/register/', data)
        if res.get('success'):
            return {'success': True, 'user': res['data'].get('user')}
        return {'success': False, 'error': res.get('error', 'Échec d\'inscription.')}

    def logout(self):
        self.storage.clear()
        return True

    def get_profile(self):
        res = self.api.get('users/profile/')
        if res.get('success'):
            user_data = res['data']
            self.storage.save('current_user', user_data)
            return {'success': True, 'user': user_data}
        return {'success': False, 'error': res.get('error')}
