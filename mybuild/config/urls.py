from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import api as core_api

urlpatterns = [
	path('admin/', admin.site.urls),
	path('', include('dashboard.urls')),
	path('playground/', include('playground.urls')),
	path('api/', include(core_api.router.urls)),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
