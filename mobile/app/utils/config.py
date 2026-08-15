import os

class Config:
    API_BASE_URL = os.environ.get('API_BASE_URL', 'http://127.0.0.1:8000/api')
    TIMEOUT = 10.0
