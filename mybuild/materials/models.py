from django.contrib.auth.models import User
from django.db import models

from core.models import BaseModel
from documents.models import Attachment
from objects.models import ConstructionObject
from schedules.models import WorkItem


class MaterialType(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    unit = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class OCRResult(BaseModel):
    source_file = models.ForeignKey(
        Attachment, on_delete=models.CASCADE, related_name="ocr_results"
    )
    raw_text = models.TextField(blank=True, null=True)
    parsed = models.JSONField(default=dict)
    success = models.BooleanField(default=False, db_index=True)
    error = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"OCR для {self.source_file.name}"


class TTNDocument(BaseModel):
    attachment = models.ForeignKey(Attachment, on_delete=models.PROTECT)
    ocr = models.OneToOneField(
        OCRResult, on_delete=models.SET_NULL, null=True, blank=True
    )
    number = models.CharField(max_length=128, db_index=True, blank=True, null=True)
    date = models.DateField(db_index=True, blank=True, null=True)

    def __str__(self):
        return self.number or str(self.id)


class QualityPassport(BaseModel):
    attachment = models.ForeignKey(Attachment, on_delete=models.PROTECT)
    number = models.CharField(max_length=128, db_index=True, blank=True, null=True)
    date = models.DateField(db_index=True, blank=True, null=True)

    def __str__(self):
        return self.number or str(self.id)


class Delivery(BaseModel):
    object = models.ForeignKey(
        ConstructionObject,
        on_delete=models.CASCADE,
        related_name="deliveries",
        db_index=True,
    )
    work_item = models.ForeignKey(
        WorkItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deliveries",
    )
    material = models.ForeignKey(
        MaterialType, on_delete=models.PROTECT, db_index=True
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    delivered_at = models.DateTimeField(db_index=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_deliveries",
    )
    ttn = models.OneToOneField(
        TTNDocument, on_delete=models.SET_NULL, null=True, blank=True
    )
    quality_passport = models.OneToOneField(
        QualityPassport, on_delete=models.SET_NULL, null=True, blank=True
    )
    photos = models.ManyToManyField(Attachment, blank=True)

    def __str__(self):
        return f"Поставка {self.material.name} на {self.object.name}"
