from django.contrib import admin
from .models import IssueCategory, Remark, Violation, Resolution

admin.site.register(IssueCategory)
admin.site.register(Remark)
admin.site.register(Violation)
admin.site.register(Resolution)
