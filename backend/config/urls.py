from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/users/', include('apps.accounts.profile_urls')),
    path('api/content/', include('apps.content.urls')),
    path('api/glossary/', include('apps.glossary.urls')),
    path('api/pests/', include('apps.pests.urls')),
    path('api/subscriptions/', include('apps.subscriptions.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
