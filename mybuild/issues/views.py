from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from issues.models import Remark
from objects.models import OpeningChecklist, ConstructionObject
from issues.forms import RemarkForm
from issues.services import RemarkService


@login_required
def remark_new(request, pk):
    obj = get_object_or_404(ConstructionObject, pk=pk)
    # Access check to organization
    if not request.user.is_superuser:
        user_orgs = request.user.memberships.values_list('org', flat=True).distinct()
        if obj.org_id not in user_orgs:
            raise PermissionDenied("У вас нет доступа к этому объекту.")
    service = RemarkService(user=request.user)
    if request.method == 'POST':
        form = RemarkForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                remark = service.create(obj, form.cleaned_data)
                messages.success(request, 'Нарушение создано успешно.')
                return redirect('objects:detail', pk=pk)
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = RemarkForm()
    return render(request, 'issues/remark_form.html', {'form': form,'object': obj})


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
        'is_inspector': request.user.groups.filter(name='INSPECTOR').exists(),
    }
    return render(request, 'issues/remark_detail.html', context)


@login_required
def confirm_resolution(request, pk):
    remark = get_object_or_404(Remark, pk=pk)
    service = RemarkService(user=request.user)
    try:
        service.submit_resolution(remark)
        messages.success(request, 'Устранение подтверждено, ожидается подтверждение.')
    except Exception as e:
        messages.error(request, str(e))
    return redirect('issues:remark_detail', pk=pk)


@login_required
def confirm_closure(request, pk):
    remark = get_object_or_404(Remark, pk=pk)
    service = RemarkService(user=request.user)
    try:
        service.confirm_closure(remark)
        messages.success(request, 'Устранение нарушения подтверждено.')
    except Exception as e:
        messages.error(request, str(e))
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


@login_required
def remarks_create(request):
	"""Создание нового нарушения"""
	if request.user.is_superuser:
		accessible_objects = ConstructionObject.objects.all()
	else:
		user_orgs = request.user.memberships.values_list('org', flat=True).distinct()
		accessible_objects = ConstructionObject.objects.filter(org__in=user_orgs)
	
	if request.method == 'POST':
		form = RemarkForm(request.POST, request.FILES)
		if form.is_valid():
			try:
				object_id = request.POST.get('construction_object')
				obj = get_object_or_404(ConstructionObject, pk=object_id)
				
				# Проверка доступа
				if not request.user.is_superuser:
					if obj.org_id not in request.user.memberships.values_list('org', flat=True):
						raise PermissionDenied("У вас нет доступа к этому объекту.")
				
				service = RemarkService(user=request.user)
				remark = service.create(obj, form.cleaned_data)
				messages.success(request, 'Нарушение создано успешно.')
				return redirect('remarks_list')
			except Exception as e:
				messages.error(request, str(e))
	else:
		form = RemarkForm()
	
	return render(request, 'issues/create_remark.html', {
		'form': form,
		'accessible_objects': accessible_objects
	})
