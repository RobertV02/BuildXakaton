from rest_framework import serializers
from .models import PhotoTest

class PhotoTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoTest
        fields = ('image',)
