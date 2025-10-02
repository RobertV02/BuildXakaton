"""Регистрация DRF rout    role_map = {
        'create': ['ADMIN', 'FOREMAN'],
        'plan': ['CLIENT'],
        'request_activation': ['CLIENT'],
        'activate': ['INSPECTOR'],
        'close': ['ADMIN'],
    }зовые ViewSet скелеты.

Пока минимально: только модели без бизнес-логики (CRUD / read-only) —
логика и кастом-экшены будут добавляться постепенно.
"""
from __future__ import annotations

from rest_framework import routers, viewsets, mixins, decorators, response, status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from core.services.scoping import ScopedQuerySetMixin
from core.permissions import MatrixPermission

from objects.models import ConstructionObject, OpeningChecklist, DailyChecklist
from schedules.models import WorkItem
from materials.models import Delivery, OCRResult, TTNDocument, LabSampleRequest
from issues.models import Remark, Violation


class ConstructionObjectViewSet(ScopedQuerySetMixin, viewsets.ModelViewSet):
    queryset = ConstructionObject.objects.all()
    permission_classes = [IsAuthenticated, MatrixPermission]
    role_map = {
        'create': ['ORG_ADMIN', 'FOREMAN'],
        'plan': ['CLIENT'],
        'request_activation': ['CLIENT'],
        'activate': ['INSPECTOR'],
        'close': ['ADMIN'],
    }

    def get_serializer_class(self):
        from objects.serializers import (
            ConstructionObjectListSerializer,
            ConstructionObjectDetailSerializer,
        )
        if self.action == 'list':
            return ConstructionObjectListSerializer
        return ConstructionObjectDetailSerializer

    def perform_create(self, serializer):  # type: ignore[override]
        from rest_framework.exceptions import PermissionDenied
        from core.services.scoping import get_user_org_ids
        org_obj = serializer.validated_data.get('org')
        if org_obj and org_obj.id not in get_user_org_ids(self.request.user):
            raise PermissionDenied('Вы не состоите в указанной организации.')
        instance = serializer.save()
        from audit.services import log_action
        from notifications.services import notify, build_basic_payload, OBJECT_CREATED
        log_action(actor=self.request.user, action='create_object', instance=instance)
        notify([self.request.user], OBJECT_CREATED, build_basic_payload(instance))

    def perform_update(self, serializer):  # type: ignore[override]
        old = self.get_object()
        instance = serializer.save()
        from audit.services import log_action
        from notifications.services import notify, build_basic_payload, OBJECT_UPDATED
        log_action(actor=self.request.user, action='update_object', instance=instance, before=old)
        notify([self.request.user], OBJECT_UPDATED, build_basic_payload(instance))

    # ---------- FSM actions ----------
    @decorators.action(detail=True, methods=['post'])
    @extend_schema(summary="Планирование объекта", responses={200: OpenApiResponse(description="Успех"), 400: OpenApiResponse(description="Неверный статус")})
    def plan(self, request, pk=None):
        obj = self.get_object()
        from objects.models import ObjectStatus
        if obj.status != ObjectStatus.DRAFT:
            return response.Response({'detail': 'Можно запланировать только из DRAFT.'}, status=400)
        obj.status = ObjectStatus.PLANNED
        obj.save(update_fields=['status', 'updated_at'])
        from audit.services import log_action
        from notifications.services import notify, build_basic_payload
        log_action(actor=request.user, action='object_plan', instance=obj)
        notify([request.user], 'object.planned', build_basic_payload(obj))
        return response.Response({'status': obj.status})

    @decorators.action(detail=True, methods=['post'])
    @extend_schema(summary="Запрос активации объекта", responses={200: OpenApiResponse(description="Успех"), 400: OpenApiResponse(description="Неверный статус")})
    def request_activation(self, request, pk=None):
        obj = self.get_object()
        from objects.models import ObjectStatus
        if obj.status not in (ObjectStatus.PLANNED, ObjectStatus.DRAFT):
            return response.Response({'detail': 'Нельзя запросить активацию в текущем статусе.'}, status=400)
        obj.status = ObjectStatus.ACTIVATION_PENDING
        obj.save(update_fields=['status', 'updated_at'])
        from audit.services import log_action
        from notifications.services import notify, build_basic_payload
        log_action(actor=request.user, action='object_request_activation', instance=obj)
        notify([request.user], 'object.activation_requested', build_basic_payload(obj))
        return response.Response({'status': obj.status})

    @decorators.action(detail=True, methods=['post'])
    @extend_schema(summary="Активация объекта", responses={200: OpenApiResponse(description="Успех"), 400: OpenApiResponse(description="Неверный статус")})
    def activate(self, request, pk=None):
        obj = self.get_object()
        from objects.models import ObjectStatus
        if obj.status not in (ObjectStatus.ACTIVATION_PENDING, ObjectStatus.PLANNED):
            return response.Response({'detail': 'Можно активировать только из ACTIVATION_PENDING или PLANNED.'}, status=400)
        from django.utils import timezone
        obj.status = ObjectStatus.ACTIVE
        obj.activated_at = timezone.now()
        obj.activated_by = request.user
        obj.save(update_fields=['status', 'activated_at', 'activated_by', 'updated_at'])

        # Create opening checklist automatically when object is activated
        if not hasattr(obj, 'opening_checklist'):
            from objects.models import OpeningChecklist
            OpeningChecklist.objects.create(
                object=obj,
                data={"fields": []},  # Empty checklist data to be filled later
                filled_by=None  # Will be set when checklist is filled
            )

        from audit.services import log_action
        from notifications.services import notify, build_basic_payload
        log_action(actor=request.user, action='object_activate', instance=obj)
        notify([request.user], 'object.activated', build_basic_payload(obj))
        return response.Response({'status': obj.status})

    @decorators.action(detail=True, methods=['post'])
    @extend_schema(summary="Закрытие объекта", responses={200: OpenApiResponse(description="Успех"), 400: OpenApiResponse(description="Неверный статус")})
    def close(self, request, pk=None):
        obj = self.get_object()
        from objects.models import ObjectStatus
        if obj.status != ObjectStatus.ACTIVE:
            return response.Response({'detail': 'Закрыть можно только активный объект.'}, status=400)
        obj.status = ObjectStatus.CLOSED
        obj.save(update_fields=['status', 'updated_at'])
        from audit.services import log_action
        from notifications.services import notify, build_basic_payload
        log_action(actor=request.user, action='object_close', instance=obj)
        notify([request.user], 'object.closed', build_basic_payload(obj))
        return response.Response({'status': obj.status})


class WorkItemViewSet(ScopedQuerySetMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = WorkItem.objects.select_related('revision').all()
    permission_classes = [IsAuthenticated, MatrixPermission]

    def get_serializer_class(self):
        from schedules.serializers import WorkItemListSerializer, WorkItemDetailSerializer
        if self.action == 'list':
            return WorkItemListSerializer
        return WorkItemDetailSerializer


class DeliveryViewSet(ScopedQuerySetMixin, viewsets.ModelViewSet):
    queryset = Delivery.objects.select_related('object').all()
    permission_classes = [IsAuthenticated, MatrixPermission]

    def get_serializer_class(self):
        from materials.serializers import DeliveryListSerializer, DeliveryDetailSerializer
        if self.action == 'list':
            return DeliveryListSerializer
        return DeliveryDetailSerializer

    def perform_create(self, serializer):  # type: ignore[override]
        data = serializer.validated_data
        offline_batch_id = data.get('offline_batch_id')
        defaults = dict(data)
        if hasattr(serializer.Meta.model, 'created_by'):
            defaults['created_by'] = self.request.user
        from core.services.offline import create_or_get_offline
        instance, created = create_or_get_offline(serializer.Meta.model, offline_batch_id=offline_batch_id, user=self.request.user, defaults=defaults)
        from audit.services import log_action
        from notifications.services import notify, build_basic_payload, DELIVERY_CREATED, DELIVERY_UPDATED
        if created:
            log_action(actor=self.request.user, action='create_delivery', instance=instance)
            notify([self.request.user], DELIVERY_CREATED, build_basic_payload(instance))
        else:
            # treat as idempotent replay
            log_action(actor=self.request.user, action='replay_delivery', instance=instance, extra={'offline_batch_id': offline_batch_id})
            notify([self.request.user], DELIVERY_UPDATED, build_basic_payload(instance))
        # IMPORTANT: Assign instance back to serializer so DRF create() response includes ID & fields.
        serializer.instance = instance

    @extend_schema(
        summary="Создать поставку (идемпотентно по offline_batch_id)",
        description="Если передан offline_batch_id уже существующей записи, возвратит 200 и существующий объект, иначе 201.",
        responses={200: OpenApiResponse(description='Повтор (idempotent replay)'), 201: OpenApiResponse(description='Создано')}
    )
    def create(self, request, *args, **kwargs):  # type: ignore[override]
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # perform_create sets instance & logs actions
        self.perform_create(serializer)
        status_code = status.HTTP_201_CREATED
        if 'offline_batch_id' in serializer.validated_data:
            offline_id = serializer.validated_data.get('offline_batch_id')
            # replay marked by existing AuditLog action replay_delivery OR instance pre-existence
            # Simplistic: if replay_delivery just logged OR instance already existed
            from audit.models import AuditLog
            if AuditLog.objects.filter(action='replay_delivery', object_id=str(serializer.instance.pk)).exists():
                status_code = status.HTTP_200_OK
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status_code, headers=headers)

    def perform_update(self, serializer):  # type: ignore[override]
        old = self.get_object()
        instance = serializer.save()
        from audit.services import log_action
        from notifications.services import notify, build_basic_payload, DELIVERY_UPDATED
        log_action(actor=self.request.user, action='update_delivery', instance=instance, before=old)
        notify([self.request.user], DELIVERY_UPDATED, build_basic_payload(instance))


class OCRResultViewSet(ScopedQuerySetMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = OCRResult.objects.select_related('source_file').all()
    permission_classes = [IsAuthenticated, MatrixPermission]

    def get_serializer_class(self):
        from materials.serializers import OCRResultSerializer
        return OCRResultSerializer


class TTNDocumentViewSet(ScopedQuerySetMixin, viewsets.ModelViewSet):
    queryset = TTNDocument.objects.select_related('attachment', 'ocr').all()
    permission_classes = [IsAuthenticated, MatrixPermission]

    def get_serializer_class(self):
        from materials.serializers import TTNDocumentSerializer
        return TTNDocumentSerializer


class LabSampleRequestViewSet(ScopedQuerySetMixin, viewsets.ModelViewSet):
    queryset = LabSampleRequest.objects.select_related('material', 'delivery').all()
    permission_classes = [IsAuthenticated, MatrixPermission]

    def get_serializer_class(self):
        from materials.serializers import LabSampleRequestSerializer
        return LabSampleRequestSerializer


class RemarkViewSet(ScopedQuerySetMixin, viewsets.ModelViewSet):
    queryset = Remark.objects.select_related('object').all()
    permission_classes = [IsAuthenticated, MatrixPermission]

    def get_serializer_class(self):
        from issues.serializers import (
            RemarkListSerializer,
            RemarkDetailSerializer,
        )
        if self.action == 'list':
            return RemarkListSerializer
        return RemarkDetailSerializer

    def perform_create(self, serializer):  # type: ignore[override]
        instance = serializer.save(created_by=self.request.user)
        from audit.services import log_action
        from notifications.services import notify, build_basic_payload, REMARK_CREATED
        log_action(actor=self.request.user, action='create_remark', instance=instance)
        notify([self.request.user], REMARK_CREATED, build_basic_payload(instance))

    def perform_update(self, serializer):  # type: ignore[override]
        old = self.get_object()
        instance = serializer.save()
        from audit.services import log_action
        from notifications.services import notify, build_basic_payload, REMARK_UPDATED
        log_action(actor=self.request.user, action='update_remark', instance=instance, before=old)
        notify([self.request.user], REMARK_UPDATED, build_basic_payload(instance))


class ViolationViewSet(ScopedQuerySetMixin, viewsets.ModelViewSet):
    queryset = Violation.objects.select_related('object').all()
    permission_classes = [IsAuthenticated, MatrixPermission]

    def get_serializer_class(self):
        from issues.serializers import (
            ViolationListSerializer,
            ViolationDetailSerializer,
        )
        if self.action == 'list':
            return ViolationListSerializer
        return ViolationDetailSerializer

    def perform_create(self, serializer):  # type: ignore[override]
        instance = serializer.save(created_by=self.request.user)
        from audit.services import log_action
        from notifications.services import notify, build_basic_payload, VIOLATION_CREATED
        log_action(actor=self.request.user, action='create_violation', instance=instance)
        notify([self.request.user], VIOLATION_CREATED, build_basic_payload(instance))

    def perform_update(self, serializer):  # type: ignore[override]
        old = self.get_object()
        instance = serializer.save()
        from audit.services import log_action
        from notifications.services import notify, build_basic_payload, VIOLATION_UPDATED
        log_action(actor=self.request.user, action='update_violation', instance=instance, before=old)
        notify([self.request.user], VIOLATION_UPDATED, build_basic_payload(instance))


class OpeningChecklistViewSet(ScopedQuerySetMixin, viewsets.ModelViewSet):
    queryset = OpeningChecklist.objects.select_related('object').all()
    permission_classes = [IsAuthenticated, MatrixPermission]
    role_map = {
        'submit': ['FOREMAN', 'ADMIN'],
        'approve': ['ADMIN', 'CLIENT'],
        'reject': ['ADMIN', 'CLIENT'],
    }

    def get_serializer_class(self):
        from objects.serializers import OpeningChecklistSerializer
        return OpeningChecklistSerializer

    @decorators.action(detail=True, methods=['post'])
    @extend_schema(summary="Отправка чеклиста", responses={200: OpenApiResponse(description="Отправлен"), 400: OpenApiResponse(description="Неверный статус")})
    def submit(self, request, pk=None):
        checklist = self.get_object()
        from objects.models import OpeningChecklistStatus
        if checklist.status != OpeningChecklistStatus.DRAFT:
            return response.Response({'detail': 'Можно отправить только из DRAFT.'}, status=400)
        from django.utils import timezone
        checklist.status = OpeningChecklistStatus.SUBMITTED
        checklist.submitted_at = timezone.now()
        checklist.save(update_fields=['status', 'submitted_at', 'updated_at'])
        from audit.services import log_action
        from notifications.services import notify, build_basic_payload
        log_action(actor=request.user, action='checklist_submit', instance=checklist)
        notify([request.user], 'checklist.submitted', build_basic_payload(checklist))
        return response.Response({'status': checklist.status})

    @decorators.action(detail=True, methods=['post'])
    @extend_schema(summary="Утверждение чеклиста", responses={200: OpenApiResponse(description="Утвержден"), 400: OpenApiResponse(description="Неверный статус")})
    def approve(self, request, pk=None):
        checklist = self.get_object()
        from objects.models import OpeningChecklistStatus
        if checklist.status != OpeningChecklistStatus.SUBMITTED:
            return response.Response({'detail': 'Можно утвердить только из SUBMITTED.'}, status=400)
        from django.utils import timezone
        checklist.status = OpeningChecklistStatus.APPROVED
        checklist.reviewed_at = timezone.now()
        checklist.reviewed_by = request.user
        checklist.save(update_fields=['status', 'reviewed_at', 'reviewed_by', 'updated_at'])
        from audit.services import log_action
        from notifications.services import notify, build_basic_payload
        log_action(actor=request.user, action='checklist_approve', instance=checklist)
        notify([request.user], 'checklist.approved', build_basic_payload(checklist))
        return response.Response({'status': checklist.status})

    @decorators.action(detail=True, methods=['post'])
    @extend_schema(summary="Отклонение чеклиста", request=None, responses={200: OpenApiResponse(description="Отклонен"), 400: OpenApiResponse(description="Неверный статус")})
    def reject(self, request, pk=None):
        checklist = self.get_object()
        from objects.models import OpeningChecklistStatus
        if checklist.status != OpeningChecklistStatus.SUBMITTED:
            return response.Response({'detail': 'Можно отклонить только из SUBMITTED.'}, status=400)
        from django.utils import timezone
        checklist.status = OpeningChecklistStatus.REJECTED
        checklist.reviewed_at = timezone.now()
        checklist.reviewed_by = request.user
        comment = request.data.get('comment')
        if comment:
            checklist.review_comment = comment
            checklist.save(update_fields=['status', 'reviewed_at', 'reviewed_by', 'review_comment', 'updated_at'])
        else:
            checklist.save(update_fields=['status', 'reviewed_at', 'reviewed_by', 'updated_at'])
        from audit.services import log_action
        from notifications.services import notify, build_basic_payload
        log_action(actor=request.user, action='checklist_reject', instance=checklist, extra={'comment': comment})
        notify([request.user], 'checklist.rejected', build_basic_payload(checklist))
        return response.Response({'status': checklist.status})


class DailyChecklistViewSet(ScopedQuerySetMixin, viewsets.ModelViewSet):
    queryset = DailyChecklist.objects.select_related('object').all()
    permission_classes = [IsAuthenticated, MatrixPermission]
    role_map = {
        'create': ['FOREMAN', 'ADMIN'],
        'update': ['FOREMAN', 'ADMIN'],
        'partial_update': ['FOREMAN', 'ADMIN'],
        'destroy': ['FOREMAN', 'ADMIN'],
        'confirm': ['CLIENT', 'ADMIN'],
    }

    def get_serializer_class(self):
        from objects.serializers import DailyChecklistSerializer
        return DailyChecklistSerializer

    @decorators.action(detail=True, methods=['post'])
    @extend_schema(summary="Подтверждение ежедневного чеклиста", responses={200: OpenApiResponse(description="Подтвержден"), 400: OpenApiResponse(description="Неверный статус")})
    def confirm(self, request, pk=None):
        checklist = self.get_object()
        from objects.models import DailyChecklistStatus
        if checklist.status != DailyChecklistStatus.PENDING_CONFIRMATION:
            return response.Response({'detail': 'Можно подтвердить только из PENDING_CONFIRMATION.'}, status=400)
        from django.utils import timezone
        checklist.status = DailyChecklistStatus.APPROVED
        checklist.confirmed_at = timezone.now()
        checklist.confirmed_by = request.user
        checklist.save(update_fields=['status', 'confirmed_at', 'confirmed_by', 'updated_at'])
        from audit.services import log_action
        from notifications.services import notify, build_basic_payload
        log_action(actor=request.user, action='daily_checklist_confirm', instance=checklist)
        notify([request.user], 'daily_checklist.confirmed', build_basic_payload(checklist))
        return response.Response({'status': checklist.status})


router = routers.DefaultRouter()
router.register('objects', ConstructionObjectViewSet, basename='object')
router.register('work-items', WorkItemViewSet, basename='workitem')
router.register('deliveries', DeliveryViewSet, basename='delivery')
router.register('ocr-results', OCRResultViewSet, basename='ocrresult')
router.register('ttn-docs', TTNDocumentViewSet, basename='ttn')
router.register('lab-samples', LabSampleRequestViewSet, basename='labsample')
router.register('remarks', RemarkViewSet, basename='remark')
router.register('violations', ViolationViewSet, basename='violation')
router.register('opening-checklists', OpeningChecklistViewSet, basename='openingchecklist')
router.register('daily-checklists', DailyChecklistViewSet, basename='dailychecklist')
