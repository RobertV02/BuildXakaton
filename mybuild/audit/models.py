from django.contrib.auth.models import User
from django.db import models
from core.models import BaseModel

class AuditLog(BaseModel):
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    action = models.CharField(max_length=128, db_index=True)
    model = models.CharField(max_length=128, db_index=True)
    object_id = models.CharField(max_length=64, db_index=True)
    context = models.JSONField(default=dict)
    client_created_at = models.DateTimeField(null=True, blank=True, db_index=True)
    client_lat = models.FloatField(null=True, blank=True)
    client_lon = models.FloatField(null=True, blank=True)
    offline_batch_id = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    was_offline = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ("can_view_auditlog", "Может просматривать аудит"),
        ]

    def __str__(self):
        return f'{self.action} on {self.model} ({self.object_id}) by {self.actor}'
