from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from issues.models import Remark
from objects.models import OpeningChecklist, ConstructionObject
from issues.forms import RemarkForm


@login_required
def remark_new(request, pk):
    obj = get_object_or_404(ConstructionObject, pk=pk)
    
    # Check if user can create remarks
    if not request.user.is_superuser:
        user_orgs = request.user.memberships.values_list('org', flat=True).distinct()
        if obj.org_id not in user_orgs:
            raise PermissionDenied("У вас нет доступа к этому объекту.")
        
        # Only CLIENT and INSPECTOR can create remarks
        user_groups = request.user.groups.values_list('name', flat=True)
        if not ('CLIENT' in user_groups or 'INSPECTOR' in user_groups):
            raise PermissionDenied("Только заказчики и инспекторы могут создавать нарушения.")
    
    if request.method == 'POST':
        form = RemarkForm(request.POST, request.FILES)
        if form.is_valid():
            remark = form.save(commit=False)
            remark.object = obj
            remark.created_by = request.user
            remark.save()
            messages.success(request, 'Нарушение создано успешно.')
            return redirect('objects:detail', pk=pk)
    else:
        form = RemarkForm()
    
    return render(request, 'issues/remark_form.html', {
        'form': form,
        'object': obj,
    })


@login_required
def remark_detail(request, pk):
    remark = get_object_or_404(Remark.objects.select_related('object', 'created_by'), pk=pk)
    # Check access to the object unless superuser
    if not request.user.is_superuser:
        user_orgs = request.user.memberships.values_list('org', flat=True).distinct()
        if remark.object.org_id not in user_orgs:
            raise PermissionDenied("У вас нет доступа к этому нарушению.")
    context = {
        'remark': remark,
        'is_foreman': request.user.groups.filter(name='FOREMAN').exists(),
        'is_client': request.user.groups.filter(name='CLIENT').exists(),
    }
    return render(request, 'issues/remark_detail.html', context)


@login_required
def confirm_resolution(request, pk):
    remark = get_object_or_404(Remark, pk=pk)
    if request.user.groups.filter(name='FOREMAN').exists() and remark.status in ['OPEN', 'IN_PROGRESS']:
        remark.status = 'PENDING_CONFIRMATION'
        remark.save()
        messages.success(request, 'Устранение подтверждено, ожидается подтверждение от заказчика.')
    else:
        messages.error(request, 'У вас нет прав для этого действия.')
    return redirect('issues:remark_detail', pk=pk)


@login_required
def confirm_closure(request, pk):
    remark = get_object_or_404(Remark, pk=pk)
    user_groups = request.user.groups.values_list('name', flat=True)
    
    # INSPECTOR or FOREMAN can confirm closure
    if ('INSPECTOR' in user_groups or 'FOREMAN' in user_groups or request.user.is_superuser) and remark.status == 'PENDING_CONFIRMATION':
        remark.status = 'ACCEPTED'
        remark.save()
        messages.success(request, 'Устранение нарушения подтверждено.')
    else:
        messages.error(request, 'У вас нет прав для этого действия.')
    return redirect('issues:remark_detail', pk=pk)


@login_required
def remarks_list(request):
	remarks = Remark.objects.select_related('object').order_by('-created_at')
	# Filter by user's accessible objects unless superuser
	if not request.user.is_superuser:
		user_orgs = request.user.memberships.values_list('org', flat=True).distinct()
		accessible_objects = ConstructionObject.objects.filter(org__in=user_orgs).values_list('id', flat=True)
		remarks = remarks.filter(object_id__in=accessible_objects)
	remarks = remarks[:300]
	return render(request, 'issues/list/remarks.html', {'remarks': remarks})


@login_required
def checklists_list(request):
	checklists = OpeningChecklist.objects.select_related('object').order_by('-updated_at')
	# Filter by user's accessible objects unless superuser
	if not request.user.is_superuser:
		user_orgs = request.user.memberships.values_list('org', flat=True).distinct()
		accessible_objects = ConstructionObject.objects.filter(org__in=user_orgs).values_list('id', flat=True)
		checklists = checklists.filter(object_id__in=accessible_objects)
	checklists = checklists[:300]
	return render(request, 'issues/list/checklists.html', {'checklists': checklists})

# Create your views here.
