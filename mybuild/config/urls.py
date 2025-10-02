from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import api as core_api
from materials.views import delivery_list
from issues.views import remarks_list, checklists_list

urlpatterns = [
	path('admin/', admin.site.urls),
	path('accounts/', include('django.contrib.auth.urls')),
	path('', include('dashboard.urls')),
	path('objects/', include(('objects.urls', 'objects'), namespace='objects')),
	path('issues/', include(('issues.urls', 'issues'), namespace='issues')),
	path('deliveries/', delivery_list, name='deliveries_list'),
	path('remarks/', remarks_list, name='remarks_list'),
	path('checklists/', checklists_list, name='checklists_list'),
	path('playground/', include('playground.urls')),
	path('api/', include(core_api.router.urls)),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
