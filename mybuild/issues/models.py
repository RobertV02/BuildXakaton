from django.contrib.auth.models import User
from django.db import models
from core.models import BaseModel, OfflineFieldsMixin
from documents.models import Attachment
from objects.models import ConstructionObject

class IssuerType(models.TextChoices):
    CUSTOMER = 'CUSTOMER', 'Заказчик'
    INSPECTOR = 'INSPECTOR', 'Инспектор'

class IssueStatus(models.TextChoices):
    OPEN = 'OPEN', 'Открыто'
    IN_PROGRESS = 'IN_PROGRESS', 'В работе'
    RESOLVED = 'RESOLVED', 'Решено'
    ACCEPTED = 'ACCEPTED', 'Принято'
    REJECTED = 'REJECTED', 'Отклонено'

class Severity(models.TextChoices):
    LOW = 'LOW', 'Низкая'
    MEDIUM = 'MEDIUM', 'Средняя'
    HIGH = 'HIGH', 'Высокая'
    CRITICAL = 'CRITICAL', 'Критическая'

class Fixability(models.TextChoices):
    FIXABLE = 'FIXABLE', 'Устранимое'
    NON_FIXABLE = 'NON_FIXABLE', 'Неустранимое'

class IssueType(models.TextChoices):
    GROSS = 'GROSS', 'Грубое'
    SIMPLE = 'SIMPLE', 'Простое'

class IssueCategory(BaseModel):
    title = models.CharField(max_length=255, db_index=True)
    code = models.CharField(max_length=64, unique=True)
    issuer_type = models.CharField(max_length=20, choices=IssuerType.choices)

    def __str__(self):
        return self.title

class IssueBase(BaseModel, OfflineFieldsMixin):
    object = models.ForeignKey(ConstructionObject, on_delete=models.CASCADE, db_index=True)
    category = models.ForeignKey(IssueCategory, on_delete=models.PROTECT)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    status = models.CharField(max_length=20, choices=IssueStatus.choices, default=IssueStatus.OPEN, db_index=True)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MEDIUM, db_index=True)
    sla_due = models.DateTimeField(null=True, blank=True, db_index=True)
    photos = models.ManyToManyField(Attachment, blank=True, related_name='%(class)s_photos')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        abstract = True

class Remark(IssueBase):
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Наименование")
    fixability = models.CharField(max_length=20, choices=Fixability.choices, default=Fixability.FIXABLE, verbose_name="Вид")
    issue_type = models.CharField(max_length=20, choices=IssueType.choices, default=IssueType.SIMPLE, verbose_name="Тип")
    resolution_deadline_days = models.CharField(max_length=10, blank=True, null=True, verbose_name="Регламентный срок устранения (в днях)")

    class Meta:
        verbose_name = "Нарушение заказчика"
        verbose_name_plural = "Нарушения заказчика"
        permissions = [
            ("can_comment_issue", "Может комментировать замечание/нарушение"),
            ("can_verify_issue", "Может верифицировать устранение"),
            ("can_close_issue", "Может закрывать замечание/нарушение"),
        ]

class Violation(IssueBase):
    normative_link = models.CharField(max_length=512, blank=True, null=True)

    class Meta:
        verbose_name = "Нарушение инспектора"
        verbose_name_plural = "Нарушения инспектора"
        permissions = [
            ("can_comment_issue", "Может комментировать замечание/нарушение"),
            ("can_verify_issue", "Может верифицировать устранение"),
            ("can_close_issue", "Может закрывать замечание/нарушение"),
        ]

class Resolution(BaseModel):
    remark = models.ForeignKey(Remark, on_delete=models.CASCADE, null=True, blank=True, related_name='resolutions', db_index=True)
    violation = models.ForeignKey(Violation, on_delete=models.CASCADE, null=True, blank=True, related_name='resolutions', db_index=True)
    text = models.TextField()
    attachments = models.ManyToManyField(Attachment, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolutions', db_index=True)
    accepted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='accepted_resolutions')
    accepted_at = models.DateTimeField(null=True, blank=True)
    is_accepted = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        issue = self.remark or self.violation
        return f'Резолюция для {issue}'
