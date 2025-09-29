from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from materials.models import Delivery


@login_required
def delivery_list(request):
	deliveries = Delivery.objects.select_related('object', 'material').order_by('-delivered_at')[:300]
	return render(request, 'materials/list.html', {'deliveries': deliveries})
