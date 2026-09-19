from .api_client import APIClient

class BlogService:
    def __init__(self):
        self.api = APIClient()

    def get_categories(self):
        return self.api.get('/api/blog/categories/')

    def get_posts(self, category=None, search=None):
        endpoint = '/api/blog/posts/?page_size=all'
        if category:
            endpoint += f'&category={category}'
        if search:
            endpoint += f'&search={search}'
        return self.api.get(endpoint)

    def get_post_detail(self, post_id):
        return self.api.get(f'/api/blog/posts/{post_id}/')

    def add_comment(self, post_id, content):
        return self.api.post(f'/api/blog/posts/{post_id}/comments/', data={'content': content})
