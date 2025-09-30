from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from issues.models import Remark
from objects.models import OpeningChecklist


@login_required
def remark_detail(request, pk):
    remark = get_object_or_404(Remark.objects.select_related('object', 'category', 'created_by'), pk=pk)
    return render(request, 'issues/remark_detail.html', {'remark': remark})


@login_required
def remarks_list(request):
	remarks = Remark.objects.select_related('object', 'category').order_by('-created_at')[:300]
	return render(request, 'issues/list/remarks.html', {'remarks': remarks})


@login_required
def checklists_list(request):
	checklists = OpeningChecklist.objects.select_related('object').order_by('-updated_at')[:300]
	
	# Calculate status counts
	from objects.models import OpeningChecklistStatus
	draft_count = checklists.filter(status=OpeningChecklistStatus.DRAFT).count()
	submitted_count = checklists.filter(status=OpeningChecklistStatus.SUBMITTED).count()
	approved_count = checklists.filter(status=OpeningChecklistStatus.APPROVED).count()
	rejected_count = checklists.filter(status=OpeningChecklistStatus.REJECTED).count()
	
	# Get available objects for creating checklists (ACTIVE or ACTIVATION_PENDING without checklist)
	from objects.models import ConstructionObject, ObjectStatus
	available_objects = ConstructionObject.objects.filter(
		status__in=[ObjectStatus.ACTIVE, ObjectStatus.ACTIVATION_PENDING]
	).exclude(
		opening_checklist__isnull=False
	).select_related('org').order_by('name')
	
	# Check if user is foreman
	is_foreman = request.user.memberships.filter(role='FOREMAN').exists()
	
	return render(request, 'issues/list/checklists.html', {
		'checklists': checklists,
		'draft_count': draft_count,
		'submitted_count': submitted_count,
		'approved_count': approved_count,
		'rejected_count': rejected_count,
		'available_objects': available_objects,
		'is_foreman': is_foreman,
	})

@login_required
def create_checklist(request):
    from objects.models import ConstructionObject, OpeningChecklist
    
    if request.method == 'POST':
        object_id = request.POST.get('object_id')
        if not object_id:
            messages.error(request, 'Не выбран объект')
            return redirect('issues:checklists_list')
        
        try:
            obj = ConstructionObject.objects.get(id=object_id)
        except ConstructionObject.DoesNotExist:
            messages.error(request, 'Объект не найден')
            return redirect('issues:checklists_list')
        
        # Check if checklist already exists
        if hasattr(obj, 'opening_checklist'):
            messages.warning(request, 'Чек-лист для этого объекта уже существует')
            return redirect('issues:checklists_list')
        
        # Create checklist
        OpeningChecklist.objects.create(
            object=obj,
            data={"fields": []},
            filled_by=None
        )
        
        messages.success(request, f'Чек-лист для объекта "{obj.name}" успешно создан')
        return redirect('issues:checklists_list')
    
    return redirect('issues:checklists_list')
