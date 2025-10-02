from django.urls import path
from . import views

app_name = 'issues'

urlpatterns = [
    path('remarks/new/<uuid:pk>/', views.remark_new, name='remark_new'),
    path('remarks/<uuid:pk>/', views.remark_detail, name='remark_detail'),
    path('remarks/<uuid:pk>/confirm-resolution/', views.confirm_resolution, name='confirm_resolution'),
    path('remarks/<uuid:pk>/confirm-closure/', views.confirm_closure, name='confirm_closure'),
]