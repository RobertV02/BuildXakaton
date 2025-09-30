from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from issues.models import Remark
from objects.models import OpeningChecklist


@login_required
def remark_detail(request, pk):
    remark = get_object_or_404(Remark.objects.select_related('object', 'created_by'), pk=pk)
    return render(request, 'issues/remark_detail.html', {'remark': remark})


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
    if request.user.groups.filter(name='CLIENT').exists() and remark.status == 'PENDING_CONFIRMATION':
        remark.status = 'ACCEPTED'
        remark.save()
        messages.success(request, 'Нарушение закрыто.')
    else:
        messages.error(request, 'У вас нет прав для этого действия.')
    return redirect('issues:remark_detail', pk=pk)


@login_required
def remarks_list(request):
	remarks = Remark.objects.select_related('object').order_by('-created_at')[:300]
	return render(request, 'issues/list/remarks.html', {'remarks': remarks})


@login_required
def checklists_list(request):
	checklists = OpeningChecklist.objects.select_related('object').order_by('-updated_at')[:300]
	return render(request, 'issues/list/checklists.html', {'checklists': checklists})

# Create your views here.
