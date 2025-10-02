import uuid
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from core.models import BaseModel, OfflineFieldsMixin
from objects.models import ConstructionObject

class PresenceMethod(models.TextChoices):
    QR = 'QR', 'QR-код'
    NFC = 'NFC', 'NFC-метка'
    GPS = 'GPS', 'GPS-координаты'

class PresenceStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Черновик'
    CONFIRMED = 'CONFIRMED', 'Подтверждено'

class PresenceToken(BaseModel):
    object = models.ForeignKey(ConstructionObject, on_delete=models.CASCADE, related_name='presence_tokens', db_index=True)
    method = models.CharField(max_length=10, choices=PresenceMethod.choices)
    token = models.CharField(max_length=64, unique=True, default=uuid.uuid4, db_index=True)
    expires_at = models.DateTimeField()
    is_revoked = models.BooleanField(default=False, db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_tokens')

    class Meta:
        verbose_name = 'Токен присутствия'
        verbose_name_plural = 'Токены присутствия'

    def is_valid(self):
        return not self.is_revoked and timezone.now() <= self.expires_at

    def __str__(self):
        return f'Токен для {self.object.name} ({self.get_method_display()})'

class InspectionVisit(BaseModel, OfflineFieldsMixin):
    object = models.ForeignKey(ConstructionObject, on_delete=models.CASCADE, related_name='inspection_visits', db_index=True)
    inspector = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inspection_visits', db_index=True)
    started_at = models.DateTimeField(auto_now_add=True, db_index=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    gps_accuracy_m = models.FloatField(null=True, blank=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Инспекционный визит'
        verbose_name_plural = 'Инспекционные визиты'

    def __str__(self):
        return f'Визит {self.inspector.username} на {self.object.name} в {self.started_at}'

class PresenceConfirmation(BaseModel, OfflineFieldsMixin):
    visit = models.OneToOneField(InspectionVisit, on_delete=models.CASCADE, related_name='presence_confirmation')
    status = models.CharField(max_length=20, choices=PresenceStatus.choices, default=PresenceStatus.DRAFT, db_index=True)
    method = models.CharField(max_length=10, choices=PresenceMethod.choices)
    token = models.ForeignKey(PresenceToken, on_delete=models.SET_NULL, null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    draft_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Подтверждение присутствия'
        verbose_name_plural = 'Подтверждения присутствия'

    def __str__(self):
        return f'Подтверждение для визита {self.visit.id}'
