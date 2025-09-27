from django.contrib import admin
from .models import ConstructionObject, ObjectAssignment, OpeningChecklist, OpeningAct

admin.site.register(ConstructionObject)
admin.site.register(ObjectAssignment)
admin.site.register(OpeningChecklist)
admin.site.register(OpeningAct)
