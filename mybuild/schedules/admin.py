from django.contrib import admin
from .models import ScheduleRevision, WorkItem, ChangeRequest

admin.site.register(ScheduleRevision)
admin.site.register(WorkItem)
admin.site.register(ChangeRequest)
