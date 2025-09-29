import uuid
from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class OfflineFieldsMixin(models.Model):
    """Абстрактный миксин полей для офлайн-событий.

    Используется в тех моделях, где требуется учитывать время создания на клиенте
    и идемпотентность по batch-id.
    """
    client_created_at = models.DateTimeField(null=True, blank=True, db_index=True)
    client_lat = models.FloatField(null=True, blank=True)
    client_lon = models.FloatField(null=True, blank=True)
    offline_batch_id = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    was_offline = models.BooleanField(default=False, db_index=True)

    class Meta:
        abstract = True
