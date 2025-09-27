from django.contrib import admin
from .models import MaterialType, OCRResult, TTNDocument, QualityPassport, Delivery

admin.site.register(MaterialType)
admin.site.register(OCRResult)
admin.site.register(TTNDocument)
admin.site.register(QualityPassport)
admin.site.register(Delivery)
