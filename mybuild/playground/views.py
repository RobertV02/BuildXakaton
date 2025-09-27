from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PhotoTestSerializer
from .models import PhotoTest
from PIL import Image
from PIL.ExifTags import TAGS
import datetime

def get_exif_data(image):
    exif_data = {}
    try:
        img = Image.open(image)
        if hasattr(img, '_getexif'):
            exif_info = img._getexif()
            if exif_info:
                for tag, value in exif_info.items():
                    decoded = TAGS.get(tag, tag)
                    exif_data[decoded] = value
    except Exception as e:
        print(f"Error reading EXIF data: {e}")
    return exif_data

class PhotoUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PhotoTestSerializer(data=request.data)
        if serializer.is_valid():
            photo_instance = serializer.save()
            
            exif_data = get_exif_data(photo_instance.image.path)
            
            # Преобразуем байты в строки, если это возможно
            for key, value in exif_data.items():
                if isinstance(value, bytes):
                    try:
                        exif_data[key] = value.decode('utf-8', errors='ignore')
                    except:
                        exif_data[key] = repr(value)

            server_time = datetime.datetime.now().isoformat()

            response_data = {
                'image_url': request.build_absolute_uri(photo_instance.image.url),
                'exif_data': exif_data,
                'server_time': server_time,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def photo_test_view(request):
    return render(request, 'playground/photo_test.html')

