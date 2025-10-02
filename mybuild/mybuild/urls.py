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
from django.shortcuts import render, redirect
from django.contrib import messages

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
        'memberships': request.user.memberships.select_related('org').all(),
    })

# Временные заглушки для недостающих URL
@login_required
def reports_dashboard(request):
    messages.info(request, 'Раздел отчетов находится в разработке')
    return redirect('dashboard')

@login_required
def remarks_create_stub(request):
    messages.info(request, 'Создание нарушений находится в разработке')
    return redirect('dashboard')

@login_required
def analytics_overview(request):
    messages.info(request, 'Раздел аналитики находится в разработке')
    return redirect('dashboard')

@login_required
def schedules_list(request):
    messages.info(request, 'Календарь проверок находится в разработке')
    return redirect('dashboard')

@login_required
def materials_deliveries(request):
    return redirect('deliveries_list')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/profile/', user_profile, name='profile'),
	path('', include('dashboard.urls')),
    path('playground/', include('playground.urls')),
    path('objects/', include(('objects.urls', 'objects'), namespace='objects')),
    path('deliveries/', delivery_list, name='deliveries_list'),
    path('remarks/', remarks_list, name='remarks_list'),
    path('remarks/create/', remarks_create_stub, name='remarks_create'),
    path('issues/', include(('issues.urls', 'issues'), namespace='issues')),
    path('checklists/', checklists_list, name='checklists_list'),
    
    # Временные заглушки
    path('reports/dashboard/', reports_dashboard, name='reports_dashboard'),
    path('analytics/overview/', analytics_overview, name='analytics_overview'),
    path('schedules/', schedules_list, name='schedules_list'),
    path('materials/deliveries/', materials_deliveries, name='materials_deliveries'),
    
    path('api/', include(core_api.router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

