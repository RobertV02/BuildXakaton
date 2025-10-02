from django.urls import path
from . import views

app_name = 'objects'

urlpatterns = [
    path('create/', views.object_create, name='create'),
    path('<uuid:pk>/edit/', views.object_edit, name='edit'),
    path('', views.object_list, name='list'),
    path('<uuid:pk>/', views.object_detail, name='detail'),
    path('<uuid:pk>/checklist/submit/', views.checklist_submit, name='checklist_submit'),
    path('<uuid:pk>/checklist/create/', views.checklist_create, name='checklist_create'),
    path('<uuid:pk>/checklist/edit/', views.checklist_edit, name='checklist_edit'),
    path('<uuid:pk>/checklist/delete/', views.checklist_delete, name='checklist_delete'),
    path('<uuid:pk>/checklist/approve/', views.checklist_approve, name='checklist_approve'),
    path('<uuid:pk>/checklist/reject/', views.checklist_reject, name='checklist_reject'),
    path('<uuid:pk>/daily-checklist/create/', views.daily_checklist_create, name='daily_checklist_create'),
    path('daily-checklist/<uuid:pk>/edit/', views.daily_checklist_edit, name='daily_checklist_edit'),
    path('daily-checklist/<uuid:pk>/view/', views.daily_checklist_view, name='daily_checklist_view'),
    path('daily-checklist/<uuid:pk>/submit/', views.daily_checklist_submit, name='daily_checklist_submit'),
    path('daily-checklist/<uuid:pk>/confirm/', views.daily_checklist_confirm, name='daily_checklist_confirm'),
    path('<uuid:pk>/plan/', views.object_plan, name='plan'),
    path('<uuid:pk>/request-activation/', views.object_request_activation, name='request_activation'),
    path('<uuid:pk>/activate/', views.object_activate, name='activate'),
    path('<uuid:pk>/close/', views.object_close, name='close'),
]
