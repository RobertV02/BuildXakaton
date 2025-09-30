from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from issues.models import Remark
from objects.models import OpeningChecklist


@login_required
def remark_detail(request, pk):
    remark = get_object_or_404(Remark.objects.select_related('object', 'created_by'), pk=pk)
    return render(request, 'issues/remark_detail.html', {'remark': remark})


@login_required
def remarks_list(request):
	remarks = Remark.objects.select_related('object').order_by('-created_at')[:300]
	return render(request, 'issues/list/remarks.html', {'remarks': remarks})


@login_required
def checklists_list(request):
	checklists = OpeningChecklist.objects.select_related('object').order_by('-updated_at')[:300]
	return render(request, 'issues/list/checklists.html', {'checklists': checklists})

# Create your views here.
