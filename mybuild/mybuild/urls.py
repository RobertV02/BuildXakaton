"""
URL configuration for mybuild project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from materials.views import delivery_list
from issues.views import remarks_list, checklists_list
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from core import api as core_api
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def user_profile(request):
    # Calculate statistics
    activated_objects_count = request.user.activated_objects.count()
    filled_checklists_count = request.user.filled_checklists.count()
    active_assignments_count = request.user.object_assignments.filter(is_active=True).count()
    
    return render(request, 'registration/profile.html', {
        'user': request.user,
        'activated_objects_count': activated_objects_count,
        'filled_checklists_count': filled_checklists_count,
        'active_assignments_count': active_assignments_count,
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/profile/', user_profile, name='profile'),
	path('', include('dashboard.urls')),
    path('playground/', include('playground.urls')),
    path('objects/', include(('objects.urls', 'objects'), namespace='objects')),
    path('deliveries/', delivery_list, name='deliveries_list'),
    path('remarks/', remarks_list, name='remarks_list'),
    path('issues/', include(('issues.urls', 'issues'), namespace='issues')),
    path('checklists/', checklists_list, name='checklists_list'),
    path('api/', include(core_api.router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

