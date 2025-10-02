from django.contrib.auth.models import User
from django.db import models
from core.models import BaseModel

class Attachment(BaseModel):
    name = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField(upload_to='attachments/')
    content_type = models.CharField(max_length=128, blank=True, null=True)
    size = models.BigIntegerField(default=0)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_files')
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'

    def __str__(self):
        return self.name or str(self.id)
