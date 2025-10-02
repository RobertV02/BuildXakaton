from django.contrib.auth.models import User
from django.db import models
from core.models import BaseModel
from orgs.models import Organization

class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, related_name='profile')
    phone = models.CharField(max_length=32, blank=True, null=True, db_index=True)
    position = models.CharField(max_length=128, blank=True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Организация')

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return self.user.username
