from django.contrib.auth.models import User
from django.db import models
from core.models import BaseModel

class RoleType(models.TextChoices):
    ADMIN = 'ADMIN', 'Администратор'
    CLIENT = 'CLIENT', 'Заказчик'
    FOREMAN = 'FOREMAN', 'Прораб'
    INSPECTOR = 'INSPECTOR', 'Инспектор'

class Organization(BaseModel):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Membership(BaseModel):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='memberships', db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships', db_index=True)
    role = models.CharField(max_length=20, choices=RoleType.choices, db_index=True)

    class Meta:
        unique_together = ('org', 'user', 'role')
        verbose_name = "Членство в организации"
        verbose_name_plural = "Членства в организациях"


    def __str__(self):
        return f'{self.user.username} в {self.org.name} как {self.get_role_display()}'
