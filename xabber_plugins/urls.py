from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('custom_auth/', include(('xabber_plugins.custom_auth.urls', 'custom_auth'), namespace='custom_auth')),
    path('api/v1/', include(('xabber_plugins.api.urls', 'api'), namespace='api')),
    path('', include(('xabber_plugins.plugins.urls', 'plugins'), namespace='plugins')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)