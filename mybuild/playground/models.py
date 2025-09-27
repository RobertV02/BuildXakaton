from django.db import models

class PhotoTest(models.Model):
    image = models.ImageField(upload_to='test_photos/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo taken at {self.created_at}"

