from django.contrib.auth.models import User
from django.db import models

from core.models import BaseModel
from orgs.models import Organization, RoleType


class ObjectStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Черновик'
    PENDING_ACTIVATION = 'PENDING_ACTIVATION', 'Ожидает активации'
    ACTIVE = 'ACTIVE', 'Активен'
    COMPLETED = 'COMPLETED', 'Завершен'


class OpeningChecklistStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Черновик'
    SUBMITTED = 'SUBMITTED', 'Отправлено'
    APPROVED = 'APPROVED', 'Одобрено'
    REJECTED = 'REJECTED', 'Отклонено'


class ConstructionObject(BaseModel):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='objects', db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    polygon = models.JSONField()
    status = models.CharField(max_length=20, choices=ObjectStatus.choices, default=ObjectStatus.DRAFT, db_index=True)
    plan_start = models.DateField(null=True, blank=True, db_index=True)
    plan_end = models.DateField(null=True, blank=True, db_index=True)

    def __str__(self):
        return self.name


class ObjectAssignment(BaseModel):
    object = models.ForeignKey(ConstructionObject, on_delete=models.CASCADE, related_name='assignments', db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='object_assignments', db_index=True)
    role = models.CharField(max_length=20, choices=RoleType.choices, db_index=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_roles')
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        unique_together = ('object', 'user', 'role')

    def __str__(self):
        return f'{self.user.username} на {self.object.name} как {self.get_role_display()}'


class OpeningChecklist(BaseModel):
    object = models.OneToOneField(ConstructionObject, on_delete=models.CASCADE, related_name='opening_checklist')
    filled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='filled_checklists', db_index=True)
    data = models.JSONField()
    status = models.CharField(max_length=20, choices=OpeningChecklistStatus.choices, default=OpeningChecklistStatus.DRAFT, db_index=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_checklists')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Чек-лист для {self.object.name}'


class OpeningAct(BaseModel):
    object = models.OneToOneField(ConstructionObject, on_delete=models.CASCADE, related_name='opening_act')
    file = models.ForeignKey('documents.Attachment', on_delete=models.PROTECT)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_acts')

    def __str__(self):
        return f'Акт открытия для {self.object.name}'
