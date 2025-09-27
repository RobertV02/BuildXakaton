from django.contrib import admin
from .models import PresenceToken, InspectionVisit, PresenceConfirmation

admin.site.register(PresenceToken)
admin.site.register(InspectionVisit)
admin.site.register(PresenceConfirmation)
