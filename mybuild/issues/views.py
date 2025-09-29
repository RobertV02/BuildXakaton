from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from issues.models import Remark
from objects.models import OpeningChecklist


@login_required
def remarks_list(request):
	remarks = Remark.objects.select_related('object', 'category').order_by('-created_at')[:300]
	return render(request, 'issues/list/remarks.html', {'remarks': remarks})


@login_required
def checklists_list(request):
	checklists = OpeningChecklist.objects.select_related('object').order_by('-updated_at')[:300]
	return render(request, 'issues/list/checklists.html', {'checklists': checklists})

# Create your views here.
