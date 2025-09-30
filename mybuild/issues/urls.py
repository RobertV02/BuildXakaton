from django.urls import path
from . import views

app_name = 'issues'

urlpatterns = [
    path('remarks/<uuid:pk>/', views.remark_detail, name='remark_detail'),
]