from django.contrib.auth.models import User
from django.db import models

from core.models import BaseModel
from objects.models import ConstructionObject


class ChangeRequestStatus(models.TextChoices):
    PENDING = 'PENDING', 'В ожидании'
    APPROVED = 'APPROVED', 'Одобрено'
    REJECTED = 'REJECTED', 'Отклонено'


class ScheduleRevision(BaseModel):
    object = models.ForeignKey(
        ConstructionObject,
        on_delete=models.CASCADE,
        related_name='schedule_revisions',
        db_index=True
    )
    version = models.PositiveIntegerField()
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_revisions'
    )
    note = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False, db_index=True)

    class Meta:
        unique_together = ('object', 'version')
        ordering = ['-version']

    def __str__(self):
        return f'Ревизия {self.version} для {self.object.name}'


class WorkItem(BaseModel):
    revision = models.ForeignKey(
        ScheduleRevision,
        on_delete=models.CASCADE,
        related_name='work_items',
        db_index=True
    )
    name = models.CharField(max_length=255)
    start_planned = models.DateField(db_index=True)
    end_planned = models.DateField(db_index=True)
    progress_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    dependencies = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        permissions = [
            ("can_set_actual", "Может устанавливать фактические показатели работы"),
        ]


class ChangeRequest(BaseModel):
    object = models.ForeignKey(
        ConstructionObject,
        on_delete=models.CASCADE,
        related_name='change_requests',
        db_index=True
    )
    proposed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='proposed_changes',
        db_index=True
    )
    diff = models.JSONField()
    status = models.CharField(
        max_length=20,
        choices=ChangeRequestStatus.choices,
        default=ChangeRequestStatus.PENDING,
        db_index=True
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_changes'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Запрос на изменение для {self.object.name} от {self.proposed_by.username}'
