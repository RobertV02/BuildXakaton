from django.contrib.auth.models import User
from django.db import models
from core.models import BaseModel

class AuditLog(BaseModel):
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    action = models.CharField(max_length=128, db_index=True)
    model = models.CharField(max_length=128, db_index=True)
    object_id = models.CharField(max_length=64, db_index=True)
    context = models.JSONField(default=dict)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.action} on {self.model} ({self.object_id}) by {self.actor}'
