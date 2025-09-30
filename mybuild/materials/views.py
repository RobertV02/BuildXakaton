from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from materials.models import Delivery
from objects.models import ConstructionObject


@login_required
def delivery_list(request):
	deliveries = Delivery.objects.select_related('object', 'material').order_by('-delivered_at')
	# Filter by user's accessible objects unless superuser
	if not request.user.is_superuser:
		user_orgs = request.user.memberships.values_list('org', flat=True).distinct()
		accessible_objects = ConstructionObject.objects.filter(org__in=user_orgs).values_list('id', flat=True)
		deliveries = deliveries.filter(object_id__in=accessible_objects)
	deliveries = deliveries[:300]
	return render(request, 'materials/list.html', {'deliveries': deliveries})
