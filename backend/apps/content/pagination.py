from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class FlexiblePageNumberPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        page_size = request.query_params.get(self.page_size_query_param)
        if page_size == 'all':
            return None
        return super().paginate_queryset(queryset, request, view)
