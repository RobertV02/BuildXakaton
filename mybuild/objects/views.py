from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import ConstructionObject, OpeningChecklist
from core import api as core_api
from rest_framework.test import APIRequestFactory
from materials.forms import DeliveryForm
from materials.models import Delivery
from issues.forms import RemarkForm
from issues.models import Remark
from objects.models import ObjectStatus


@login_required
def object_list(request):
	qs = ConstructionObject.objects.select_related('org').all().order_by('-created_at')
	status = request.GET.get('status')
	if status:
		qs = qs.filter(status=status)
	context = {
		'objects': qs[:200],  # simple cap
		'statuses': ConstructionObject._meta.get_field('status').choices,
	}
	return render(request, 'objects/list.html', context)


@login_required
def object_detail(request, pk):
	obj = get_object_or_404(ConstructionObject.objects.select_related('org'), pk=pk)
	tab = request.GET.get('tab', 'info')
	tabs = [
		('info', 'Инфо'),
		('deliveries', 'Поставки'),
		('remarks', 'Замечания'),
		('checklist', 'Чек-лист'),
	]
	deliveries = obj.deliveries.select_related('material').order_by('-delivered_at')[:100] if tab == 'deliveries' else []
	remarks = obj.remark_set.select_related('category').order_by('-created_at')[:100] if tab == 'remarks' else []
	checklist = getattr(obj, 'opening_checklist', None) if tab == 'checklist' else None
	return render(request, 'objects/detail.html', {
		'object': obj,
		'tabs': tabs,
		'active_tab': tab,
		'deliveries': deliveries,
		'remarks': remarks,
		'checklist': checklist,
	})


@login_required
@require_http_methods(["POST"])
def checklist_submit(request, pk):
	obj = get_object_or_404(ConstructionObject, pk=pk)
	if not hasattr(obj, 'opening_checklist'):
		messages.error(request, 'Чек-лист отсутствует')
		return HttpResponseRedirect(reverse('objects:detail', args=[pk]) + '?tab=checklist')
	factory = APIRequestFactory()
	drf_request = factory.post('/')
	drf_request.user = request.user
	view = core_api.OpeningChecklistViewSet.as_view({'post': 'submit'})
	response = view(drf_request, pk=obj.opening_checklist.pk)
	if response.status_code < 300:
		messages.success(request, 'Отправлено')
	else:
		messages.error(request, f'Ошибка: {response.status_code}')
	return HttpResponseRedirect(reverse('objects:detail', args=[pk]) + '?tab=checklist')


@login_required
@require_http_methods(["POST"])
def checklist_approve(request, pk):
	obj = get_object_or_404(ConstructionObject, pk=pk)
	if not hasattr(obj, 'opening_checklist'):
		messages.error(request, 'Чек-лист отсутствует')
		return HttpResponseRedirect(reverse('objects:detail', args=[pk]) + '?tab=checklist')
	factory = APIRequestFactory()
	drf_request = factory.post('/')
	drf_request.user = request.user
	view = core_api.OpeningChecklistViewSet.as_view({'post': 'approve'})
	response = view(drf_request, pk=obj.opening_checklist.pk)
	if response.status_code < 300:
		messages.success(request, 'Одобрено')
	else:
		messages.error(request, f'Ошибка: {response.status_code}')
	return HttpResponseRedirect(reverse('objects:detail', args=[pk]) + '?tab=checklist')


@login_required
@require_http_methods(["POST"])
def checklist_reject(request, pk):
	obj = get_object_or_404(ConstructionObject, pk=pk)
	if not hasattr(obj, 'opening_checklist'):
		messages.error(request, 'Чек-лист отсутствует')
		return HttpResponseRedirect(reverse('objects:detail', args=[pk]) + '?tab=checklist')
	factory = APIRequestFactory()
	drf_request = factory.post('/')
	drf_request.user = request.user
	view = core_api.OpeningChecklistViewSet.as_view({'post': 'reject'})
	response = view(drf_request, pk=obj.opening_checklist.pk)
	if response.status_code < 300:
		messages.success(request, 'Отклонено')
	else:
		messages.error(request, f'Ошибка: {response.status_code}')
	return HttpResponseRedirect(reverse('objects:detail', args=[pk]) + '?tab=checklist')


@login_required
def delivery_new(request, pk):
	obj = get_object_or_404(ConstructionObject, pk=pk)
	if request.method == 'POST':
		form = DeliveryForm(request.POST)
		if form.is_valid():
			delivery: Delivery = form.save(commit=False)
			delivery.object = obj
			delivery.created_by = request.user
			delivery.save()
			messages.success(request, 'Поставка создана')
			return HttpResponseRedirect(reverse('objects:detail', args=[pk]) + '?tab=deliveries')
	else:
		form = DeliveryForm()
	return render(request, 'materials/delivery_form.html', {'form': form, 'object': obj})


@login_required
def remark_new(request, pk):
	obj = get_object_or_404(ConstructionObject, pk=pk)
	if request.method == 'POST':
		form = RemarkForm(request.POST)
		if form.is_valid():
			remark: Remark = form.save(commit=False)
			remark.object = obj
			remark.created_by = request.user
			remark.save()
			messages.success(request, 'Замечание создано')
			return HttpResponseRedirect(reverse('objects:detail', args=[pk]) + '?tab=remarks')
	else:
		form = RemarkForm()
	return render(request, 'issues/remark_form.html', {'form': form, 'object': obj})


def _run_object_action(request, pk, action: str, expected_statuses=None):
	obj = get_object_or_404(ConstructionObject, pk=pk)
	if expected_statuses and obj.status not in expected_statuses:
		messages.error(request, 'Недопустимый статус для действия')
		return HttpResponseRedirect(reverse('objects:detail', args=[pk]))
	factory = APIRequestFactory(); drf_request = factory.post('/')
	drf_request.user = request.user
	view = core_api.ConstructionObjectViewSet.as_view({'post': action})
	resp = view(drf_request, pk=obj.pk)
	if resp.status_code < 300:
		messages.success(request, f'Действие выполнено: {action}')
	else:
		detail = getattr(resp, 'data', {}).get('detail', 'Ошибка')
		messages.error(request, f'Ошибка: {detail}')
	return HttpResponseRedirect(reverse('objects:detail', args=[pk]))


@login_required
@require_http_methods(["POST"])
def object_plan(request, pk):
	return _run_object_action(request, pk, 'plan', expected_statuses=[ObjectStatus.DRAFT])


@login_required
@require_http_methods(["POST"])
def object_request_activation(request, pk):
	return _run_object_action(request, pk, 'request_activation', expected_statuses=[ObjectStatus.PLANNED, ObjectStatus.DRAFT])


@login_required
@require_http_methods(["POST"])
def object_activate(request, pk):
	return _run_object_action(request, pk, 'activate', expected_statuses=[ObjectStatus.ACTIVATION_PENDING, ObjectStatus.PLANNED])


@login_required
@require_http_methods(["POST"])
def object_close(request, pk):
	return _run_object_action(request, pk, 'close', expected_statuses=[ObjectStatus.ACTIVE])

# Create your views here.
