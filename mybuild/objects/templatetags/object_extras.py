from django import template
from django.utils.safestring import mark_safe

register = template.Library()

STATUS_STYLES = {
    'DRAFT': 'bg-gray-200 text-gray-800',
    'PLANNED': 'bg-blue-100 text-blue-800',
    'ACTIVATION_PENDING': 'bg-amber-100 text-amber-800',
    'ACTIVE': 'bg-green-100 text-green-800',
    'CLOSED': 'bg-red-100 text-red-800',
    # Checklist statuses
    'SUBMITTED': 'bg-blue-100 text-blue-800',
    'APPROVED': 'bg-green-100 text-green-800',
    'REJECTED': 'bg-red-100 text-red-800',
}

@register.simple_tag
def status_badge(status: str):
    cls = STATUS_STYLES.get(status, 'bg-gray-100 text-gray-800')
    return mark_safe(f"<span class='inline-flex items-center rounded px-2 py-0.5 text-xs font-medium {cls}'>{status}</span>")


@register.simple_tag
def checklist_status_badge(status: str):
    cls = STATUS_STYLES.get(status, 'bg-gray-100 text-gray-800')
    return mark_safe(f"<span class='inline-flex items-center rounded px-2 py-0.5 text-xs font-medium {cls}'>Checklist: {status}</span>")
