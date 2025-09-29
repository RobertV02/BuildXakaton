from django.urls import path
from . import views

app_name = 'objects'

urlpatterns = [
    path('', views.object_list, name='list'),
    path('<uuid:pk>/', views.object_detail, name='detail'),
    path('<uuid:pk>/checklist/submit/', views.checklist_submit, name='checklist_submit'),
    path('<uuid:pk>/checklist/approve/', views.checklist_approve, name='checklist_approve'),
    path('<uuid:pk>/checklist/reject/', views.checklist_reject, name='checklist_reject'),
    path('<uuid:pk>/deliveries/new/', views.delivery_new, name='delivery_new'),
    path('<uuid:pk>/remarks/new/', views.remark_new, name='remark_new'),
    path('<uuid:pk>/plan/', views.object_plan, name='plan'),
    path('<uuid:pk>/request-activation/', views.object_request_activation, name='request_activation'),
    path('<uuid:pk>/activate/', views.object_activate, name='activate'),
    path('<uuid:pk>/close/', views.object_close, name='close'),
]
