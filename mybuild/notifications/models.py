from django.contrib.auth.models import User
from django.db import models
from core.models import BaseModel

class Notification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', db_index=True)
    kind = models.CharField(max_length=64, db_index=True)
    payload = models.JSONField(default=dict)
    is_read = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Уведомление для {self.user.username} ({self.kind})'
