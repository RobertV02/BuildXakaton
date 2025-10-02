from dataclasses import dataclass
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from issues.models import Remark
from objects.models import ConstructionObject
from django.contrib.auth.models import User


@dataclass
class RemarkService:
    user: User
    obj: ConstructionObject | None = None

    # Role helpers (could delegate to central roles module if shared)
    def _in_group(self, name: str) -> bool:
        return self.user.is_superuser or self.user.groups.filter(name=name).exists()

    def can_create(self, obj: ConstructionObject) -> bool:
        return self._in_group('CLIENT') or self._in_group('INSPECTOR')

    def create(self, obj: ConstructionObject, data: dict) -> Remark:
        if not self.can_create(obj):
            raise PermissionDenied('Недостаточно прав для создания нарушения')
        remark = Remark(object=obj, created_by=self.user, **data)
        remark.save()
        return remark

    def submit_resolution(self, remark: Remark) -> Remark:
        # Foreman moves OPEN/IN_PROGRESS -> PENDING_CONFIRMATION
        if not self._in_group('FOREMAN'):
            raise PermissionDenied('Нет прав подтверждать устранение')
        if remark.status not in ['OPEN','IN_PROGRESS']:
            raise ValidationError('Можно подтвердить устранение только для открытого нарушения')
        remark.status = 'PENDING_CONFIRMATION'
        remark.save(update_fields=['status'])
        return remark

    def confirm_closure(self, remark: Remark) -> Remark:
        # Inspector or Client can close from PENDING_CONFIRMATION
        if not (self._in_group('INSPECTOR') or self._in_group('CLIENT')):
            raise PermissionDenied('Нет прав подтверждать закрытие')
        if remark.status != 'PENDING_CONFIRMATION':
            raise ValidationError('Можно подтвердить только ожидающее подтверждение нарушение')
        remark.status = 'ACCEPTED'
        remark.save(update_fields=['status'])
        return remark
