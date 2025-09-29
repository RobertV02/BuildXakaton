from django import forms
from .models import Delivery, MaterialType

class DeliveryForm(forms.ModelForm):
    delivered_at = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    class Meta:
        model = Delivery
        fields = ['material', 'quantity', 'delivered_at']
        widgets = {
            'material': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300'}),
            'quantity': forms.NumberInput(attrs={'step': '0.001', 'class': 'mt-1 block w-full rounded-md border-gray-300'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['material'].queryset = MaterialType.objects.order_by('name')
