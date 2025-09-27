from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PhotoTestSerializer
from .models import PhotoTest
from PIL import Image
from PIL.ExifTags import TAGS
import datetime
import exifread
from fractions import Fraction


def _convert_to_degrees(values):
    """Helper: convert GPS coordinates stored as rationals to float degrees."""
    try:
        d = float(Fraction(values[0]))
        m = float(Fraction(values[1]))
        s = float(Fraction(values[2]))
        return d + (m / 60.0) + (s / 3600.0)
    except Exception:
        return None


def parse_exif_with_exifread(path):
    """Attempt to parse EXIF using exifread for richer metadata."""
    data = {}
    gps_lat = gps_lon = None
    try:
        with open(path, 'rb') as f:
            tags = exifread.process_file(f, details=False)
            for tag, value in tags.items():
                # Convert value to string for JSON safety
                data[str(tag)] = str(value)

            # GPS extraction
            gps_lat_tag = tags.get('GPS GPSLatitude')
            gps_lat_ref = tags.get('GPS GPSLatitudeRef')
            gps_lon_tag = tags.get('GPS GPSLongitude')
            gps_lon_ref = tags.get('GPS GPSLongitudeRef')
            if gps_lat_tag and gps_lon_tag:
                lat_vals = [Fraction(v.num, v.den) if hasattr(v, 'num') else Fraction(str(v)) for v in gps_lat_tag.values]
                lon_vals = [Fraction(v.num, v.den) if hasattr(v, 'num') else Fraction(str(v)) for v in gps_lon_tag.values]
                lat = _convert_to_degrees(lat_vals)
                lon = _convert_to_degrees(lon_vals)
                if lat is not None and lon is not None:
                    if gps_lat_ref and str(gps_lat_ref.values).upper().startswith('S'):
                        lat = -lat
                    if gps_lon_ref and str(gps_lon_ref.values).upper().startswith('W'):
                        lon = -lon
                    gps_lat, gps_lon = lat, lon
    except Exception as e:
        # Silent fallback; we will try Pillow after
        print(f"exifread parse error: {e}")
    return data, gps_lat, gps_lon


def parse_exif_with_pillow(path):
    data = {}
    gps_lat = gps_lon = None
    try:
        img = Image.open(path)
        exif = getattr(img, '_getexif', lambda: None)()
        if exif:
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8', errors='ignore')
                    except Exception:
                        value = repr(value)
                data[str(tag)] = str(value)
    except Exception as e:
        print(f"Pillow EXIF parse error: {e}")
    return data, gps_lat, gps_lon


def get_exif_full(path):
    """
    Unified EXIF parser combining exifread + Pillow fallback.
    Returns: (exif_dict, gps_lat, gps_lon)
    """
    exif_data, lat, lon = parse_exif_with_exifread(path)
    if not exif_data:  # fallback if exifread found nothing
        exif_data, lat2, lon2 = parse_exif_with_pillow(path)
        if lat is None:
            lat = lat2
        if lon is None:
            lon = lon2
    return exif_data, lat, lon

class PhotoUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PhotoTestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        photo_instance = serializer.save()

        exif_data, gps_lat, gps_lon = get_exif_full(photo_instance.image.path)
        has_exif = bool(exif_data)

        server_time = datetime.datetime.now().isoformat()

        response_data = {
            'image_url': request.build_absolute_uri(photo_instance.image.url),
            'exif_data': exif_data,              # нормализованный словарь (строки)
            'exif_raw_size': len(exif_data),
            'has_exif': has_exif,
            'gps_latitude': gps_lat,
            'gps_longitude': gps_lon,
            'gps_source': 'exif' if gps_lat is not None and gps_lon is not None else None,
            'server_time': server_time,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

def photo_test_view(request):
    return render(request, 'playground/photo_test.html')

