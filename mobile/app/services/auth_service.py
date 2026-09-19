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

    def update_profile(self, username=None, first_name=None, last_name=None, phone_number=None):
        payload = {}
        if username:
            payload['username'] = username
        if first_name is not None:
            payload['first_name'] = first_name
        if last_name is not None:
            payload['last_name'] = last_name
        if phone_number is not None:
            payload['phone_number'] = phone_number

        res = self.api.put('users/profile/', payload)
        if res.get('success'):
            user_data = res['data']
            self.storage.save('current_user', user_data)
            return {'success': True, 'user': user_data}
        return {'success': False, 'error': res.get('error', 'Échec de mise à jour du profil.')}

    def change_password(self, old_password, new_password):
        res = self.api.post('auth/change-password/', {
            'old_password': old_password,
            'new_password': new_password
        })
        if res.get('success'):
            return {'success': True, 'message': res['data'].get('message', 'Mot de passe modifié.')}
        return {'success': False, 'error': res.get('error', 'Échec du changement de mot de passe.')}
