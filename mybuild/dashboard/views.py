from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, F, Avg, Sum, Case, When, IntegerField, Value
from django.utils import timezone
from datetime import timedelta, date
from objects.models import ConstructionObject, OpeningChecklist, DailyChecklist
from materials.models import Delivery
from issues.models import Remark, Violation
from audit.models import AuditLog


@login_required
def dashboard(request):
    # Базовая фильтрация по правам доступа
    if request.user.is_superuser:
        accessible_objects = ConstructionObject.objects.all()
    else:
        user_orgs = request.user.memberships.values_list('org', flat=True).distinct()
        accessible_objects = ConstructionObject.objects.filter(org__in=user_orgs)
    
    # Основные метрики
    total_objects = accessible_objects.count()
    active_objects = accessible_objects.filter(status='ACTIVE').count()
    
    # Критические нарушения
    critical_remarks = Remark.objects.filter(
        object__in=accessible_objects,
        severity='CRITICAL',
        status__in=['OPEN', 'IN_PROGRESS']
    )
    critical_violations = Violation.objects.filter(
        object__in=accessible_objects,
        severity='HIGH',
        status__in=['OPEN', 'IN_PROGRESS']
    )
    critical_issues_count = critical_remarks.count() + critical_violations.count()
    
    # Просроченные чек-листы
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    three_days_ago = today - timedelta(days=3)
    
    overdue_opening_checklists = OpeningChecklist.objects.filter(
        object__in=accessible_objects,
        status='DRAFT',
        created_at__date__lt=week_ago
    ).count()
    
    overdue_daily_checklists = DailyChecklist.objects.filter(
        object__in=accessible_objects,
        status='DRAFT', 
        created_at__date__lt=week_ago
    ).count()
    
    overdue_checklists_count = overdue_opening_checklists + overdue_daily_checklists
    
    # Расчет индекса качества
    total_checklists = OpeningChecklist.objects.filter(
        object__in=accessible_objects
    ).count() + DailyChecklist.objects.filter(
        object__in=accessible_objects
    ).count()
    
    completed_checklists = OpeningChecklist.objects.filter(
        object__in=accessible_objects,
        status='COMPLETED'
    ).count() + DailyChecklist.objects.filter(
        object__in=accessible_objects,
        status='COMPLETED'
    ).count()
    
    total_issues = Remark.objects.filter(
        object__in=accessible_objects
    ).count() + Violation.objects.filter(
        object__in=accessible_objects
    ).count()
    
    if total_checklists > 0:
        completion_rate = (completed_checklists / total_checklists) * 100
        if total_issues > 0:
            issue_impact = min((total_issues / total_checklists) * 20, 30)  # До 30% снижения
            quality_score = max(completion_rate - issue_impact, 0)
        else:
            quality_score = completion_rate
    else:
        quality_score = 85  # Базовый показатель для новых систем
    
    # Последние объекты
    recent_objects = accessible_objects.select_related('org').order_by('-created_at')[:5]
    
    # Критические нарушения для списка
    critical_issues_list = list(critical_remarks.select_related('object')[:3]) + \
                          list(critical_violations.select_related('object')[:3])
    critical_issues_list = sorted(critical_issues_list, key=lambda x: x.created_at, reverse=True)[:5]
    
    # Просроченные чек-листы для списка
    overdue_opening_list = OpeningChecklist.objects.filter(
        object__in=accessible_objects,
        status='DRAFT',
        created_at__date__lt=week_ago
    ).select_related('object').annotate(
        days_overdue=timezone.now().date() - F('created_at__date'),
        type_display=Value('Вводный чек-лист')
    )[:3]
    
    overdue_daily_list = DailyChecklist.objects.filter(
        object__in=accessible_objects,
        status='DRAFT',
        created_at__date__lt=week_ago
    ).select_related('object').annotate(
        days_overdue=timezone.now().date() - F('created_at__date'),
        type_display=Value('Ежедневный чек-лист')
    )[:3]
    
    overdue_checklists_list = list(overdue_opening_list) + list(overdue_daily_list)
    overdue_checklists_list = sorted(overdue_checklists_list, 
                                   key=lambda x: x.created_at,
                                   reverse=False)[:5]
    
    # Прогресс по контролю качества
    quality_progress = []
    for obj in accessible_objects.filter(status='ACTIVE')[:5]:
        total_checks = OpeningChecklist.objects.filter(object=obj).count() + \
                      DailyChecklist.objects.filter(object=obj).count()
        completed_checks = OpeningChecklist.objects.filter(object=obj, status='COMPLETED').count() + \
                          DailyChecklist.objects.filter(object=obj, status='COMPLETED').count()
        issues_count = Remark.objects.filter(object=obj).count() + \
                      Violation.objects.filter(object=obj).count()
        
        if total_checks > 0:
            percentage = int((completed_checks / total_checks) * 100)
        else:
            percentage = 0
            
        quality_progress.append({
            'object_name': obj.name,
            'percentage': percentage,
            'completed_checks': completed_checks,
            'total_checks': total_checks,
            'issues_count': issues_count
        })
    
    # Предстоящие проверки
    upcoming_date = today + timedelta(days=7)
    upcoming_opening = OpeningChecklist.objects.filter(
        object__in=accessible_objects,
        status='DRAFT'
    ).select_related('object').annotate(
        days_until=Value(0),
        type_display=Value('Вводный чек-лист')
    ).order_by('-created_at')[:3]
    
    upcoming_daily = DailyChecklist.objects.filter(
        object__in=accessible_objects,
        status='DRAFT'
    ).select_related('object').annotate(
        days_until=Value(0),
        type_display=Value('Ежедневный чек-лист')
    ).order_by('-created_at')[:3]
    
    upcoming_inspections = list(upcoming_opening) + list(upcoming_daily)
    upcoming_inspections = sorted(upcoming_inspections, 
                                key=lambda x: x.created_at)[:5]
    
    # Последние поставки
    recent_deliveries = Delivery.objects.filter(
        object__in=accessible_objects
    ).select_related('material', 'object').order_by('-delivered_at')[:5]
    
    context = {
        'stats': {
            'active_objects': active_objects,
            'overdue_checklists': overdue_checklists_count,
            'critical_issues': critical_issues_count,
            'quality_score': int(quality_score),
        },
        'critical_issues': critical_issues_count,
        'recent_objects': recent_objects,
        'critical_issues_list': critical_issues_list,
        'overdue_checklists': overdue_checklists_list,
        'quality_progress': quality_progress,
        'upcoming_inspections': upcoming_inspections,
        'recent_deliveries': recent_deliveries,
    }
    
    return render(request, 'dashboard/dashboard.html', context)
