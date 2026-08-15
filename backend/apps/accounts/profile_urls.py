from django.urls import path
from .views import UserProfileView, UserHistoryView

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('history/', UserHistoryView.as_view(), name='user_history'),
]
