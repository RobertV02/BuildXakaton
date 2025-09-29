from django.urls import path
from . import views

app_name = 'objects'

urlpatterns = [
    path('', views.object_list, name='list'),
    path('<int:pk>/', views.object_detail, name='detail'),
    path('<int:pk>/checklist/submit/', views.checklist_submit, name='checklist_submit'),
    path('<int:pk>/checklist/approve/', views.checklist_approve, name='checklist_approve'),
    path('<int:pk>/checklist/reject/', views.checklist_reject, name='checklist_reject'),
    path('<int:pk>/deliveries/new/', views.delivery_new, name='delivery_new'),
    path('<int:pk>/remarks/new/', views.remark_new, name='remark_new'),
    path('<int:pk>/plan/', views.object_plan, name='plan'),
    path('<int:pk>/request-activation/', views.object_request_activation, name='request_activation'),
    path('<int:pk>/activate/', views.object_activate, name='activate'),
    path('<int:pk>/close/', views.object_close, name='close'),
]
