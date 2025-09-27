import uuid
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from core.models import BaseModel
from orgs.models import Organization, RoleType

class InvitationStatus(models.TextChoices):
    PENDING = 'PENDING', 'В ожидании'
    ACCEPTED = 'ACCEPTED', 'Принято'
    EXPIRED = 'EXPIRED', 'Истекло'
    REVOKED = 'REVOKED', 'Отозвано'

class Invitation(BaseModel):
    email = models.EmailField(db_index=True)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='invitations', db_index=True)
    role = models.CharField(max_length=20, choices=RoleType.choices, db_index=True)
    object = models.ForeignKey('objects.ConstructionObject', on_delete=models.CASCADE, null=True, blank=True, related_name='invitations', db_index=True)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_invitations')
    token = models.CharField(max_length=64, unique=True, default=uuid.uuid4, db_index=True)
    expires_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=InvitationStatus.choices, default=InvitationStatus.PENDING, db_index=True)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f'Приглашение для {self.email} в {self.org.name}'
