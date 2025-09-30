from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from objects.models import ConstructionObject, OpeningChecklist
from materials.models import Delivery
from issues.models import Remark, Violation
from audit.models import AuditLog


@login_required
def dashboard(request):
    if request.user.is_superuser:
        object_count = ConstructionObject.objects.count()
        active_checklists = OpeningChecklist.objects.exclude(status='DRAFT').count()
        delivery_count = Delivery.objects.count()
        remark_count = Remark.objects.count() + Violation.objects.count()
    else:
        user_orgs = request.user.memberships.values_list('org', flat=True).distinct()
        accessible_objects = ConstructionObject.objects.filter(org__in=user_orgs)
        object_count = accessible_objects.count()
        active_checklists = OpeningChecklist.objects.filter(object__in=accessible_objects).exclude(status='DRAFT').count()
        delivery_count = Delivery.objects.filter(object__in=accessible_objects).count()
        remark_count = Remark.objects.filter(object__in=accessible_objects).count() + Violation.objects.filter(object__in=accessible_objects).count()
    recent_audit = AuditLog.objects.select_related('actor')[:15]
    return render(request, 'dashboard/dashboard.html', {
        'stats': {
            'objects': object_count,
            'active_checklists': active_checklists,
            'deliveries': delivery_count,
            'issues': remark_count,
        },
        'recent_audit': recent_audit,
    })
