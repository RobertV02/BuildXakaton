from django.urls import path
from .views import PhotoUploadView, photo_test_view

app_name = 'playground'

urlpatterns = [
    path('api/test/photo/', PhotoUploadView.as_view(), name='photo_upload_api'),
    path('test/', photo_test_view, name='photo_test_page'),
]
