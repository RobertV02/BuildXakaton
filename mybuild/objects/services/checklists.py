from dataclasses import dataclass
from django.utils import timezone
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.models import User
from objects.models import ConstructionObject, OpeningChecklist, DailyChecklist, OpeningChecklistStatus, DailyChecklistStatus
from typing import Dict, Any


@dataclass
class OpeningChecklistService:
    user: User
    obj: ConstructionObject

    def can_edit(self, checklist: OpeningChecklist | None) -> bool:
        if self.user.is_superuser:
            return True
        return self.user.groups.filter(name='CLIENT').exists() and (not checklist or checklist.status in [OpeningChecklistStatus.DRAFT, OpeningChecklistStatus.REJECTED])

    def create(self, data: Dict[str, Any]) -> OpeningChecklist:
        if not self.user.groups.filter(name='CLIENT').exists() and not self.user.is_superuser:
            raise PermissionDenied("Только заказчик может создавать чеклист")
        if hasattr(self.obj, 'opening_checklist'):
            raise ValidationError("Чеклист уже существует")
        return OpeningChecklist.objects.create(object=self.obj, filled_by=self.user, data=data)

    def update(self, checklist: OpeningChecklist, data: Dict[str, Any]) -> OpeningChecklist:
        if not self.can_edit(checklist):
            raise PermissionDenied("Нет прав на редактирование")
        checklist.data = data
        checklist.save(update_fields=['data', 'updated_at'])
        return checklist

    def submit(self, checklist: OpeningChecklist) -> OpeningChecklist:
        if not self.user.groups.filter(name='CLIENT').exists() and not self.user.is_superuser:
            raise PermissionDenied("Нет прав на отправку")
        if checklist.status not in [OpeningChecklistStatus.DRAFT, OpeningChecklistStatus.REJECTED]:
            raise ValidationError("Разрешена отправка только из статуса Черновик или Отклонен")
        checklist.status = OpeningChecklistStatus.SUBMITTED
        checklist.submitted_at = timezone.now()
        checklist.reviewed_at = None
        checklist.reviewed_by = None
        checklist.review_comment = ''
        checklist.save(update_fields=['status','submitted_at','reviewed_at','reviewed_by','review_comment'])
        return checklist

    def approve(self, checklist: OpeningChecklist) -> OpeningChecklist:
        if not self.user.groups.filter(name='INSPECTOR').exists() and not self.user.is_superuser:
            raise PermissionDenied("Нет прав на утверждение")
        if checklist.status != OpeningChecklistStatus.SUBMITTED:
            raise ValidationError("Можно утвердить только отправленный чеклист")
        checklist.status = OpeningChecklistStatus.APPROVED
        checklist.reviewed_by = self.user
        checklist.reviewed_at = timezone.now()
        checklist.save(update_fields=['status','reviewed_by','reviewed_at'])
        return checklist

    def reject(self, checklist: OpeningChecklist, comment: str) -> OpeningChecklist:
        if not self.user.groups.filter(name='INSPECTOR').exists() and not self.user.is_superuser:
            raise PermissionDenied("Нет прав на отклонение")
        if checklist.status != OpeningChecklistStatus.SUBMITTED:
            raise ValidationError("Можно отклонить только отправленный чеклист")
        checklist.status = OpeningChecklistStatus.REJECTED
        checklist.reviewed_by = self.user
        checklist.reviewed_at = timezone.now()
        checklist.review_comment = comment
        checklist.save(update_fields=['status','reviewed_by','reviewed_at','review_comment'])
        return checklist


@dataclass
class DailyChecklistService:
    user: User
    obj: ConstructionObject

    def create(self, data: Dict[str, Any]) -> DailyChecklist:
        if not self.user.groups.filter(name='FOREMAN').exists() and not self.user.is_superuser:
            raise PermissionDenied("Нет прав на создание")
        return DailyChecklist.objects.create(object=self.obj, created_by=self.user, data=data, status=DailyChecklistStatus.DRAFT)

    def update(self, checklist: DailyChecklist, data: Dict[str, Any]) -> DailyChecklist:
        if checklist.created_by_id != self.user.id and not self.user.is_superuser:
            raise PermissionDenied("Можно редактировать только свои чеклисты")
        if checklist.status != DailyChecklistStatus.DRAFT:
            raise ValidationError("Редактирование разрешено только в Черновике")
        checklist.data = data
        checklist.save(update_fields=['data','updated_at'])
        return checklist

    def submit(self, checklist: DailyChecklist) -> DailyChecklist:
        if checklist.created_by_id != self.user.id and not self.user.is_superuser:
            raise PermissionDenied("Можно отправлять только свои чеклисты")
        if checklist.status != DailyChecklistStatus.DRAFT:
            raise ValidationError("Отправка разрешена только из Черновика")
        checklist.status = DailyChecklistStatus.PENDING_CONFIRMATION
        checklist.submitted_at = timezone.now()
        checklist.save(update_fields=['status','submitted_at'])
        return checklist

    def approve(self, checklist: DailyChecklist) -> DailyChecklist:
        if not self.user.groups.filter(name='CLIENT').exists() and not self.user.is_superuser:
            raise PermissionDenied("Нет прав на подтверждение")
        if checklist.status != DailyChecklistStatus.PENDING_CONFIRMATION:
            raise ValidationError("Можно подтвердить только ожидающий")
        checklist.status = DailyChecklistStatus.APPROVED
        checklist.confirmed_by = self.user
        checklist.confirmed_at = timezone.now()
        checklist.save(update_fields=['status','confirmed_by','confirmed_at'])
        return checklist
