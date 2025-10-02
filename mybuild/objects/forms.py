from django import forms
from .models import OpeningChecklist, ConstructionObject
from orgs.models import Organization
import json


class ConstructionObjectForm(forms.ModelForm):
    # Represent polygon JSON data as textarea for simple manual editing
    polygon_raw = forms.CharField(
        label='Геозона (JSON)',
        widget=forms.Textarea(attrs={'rows': 8, 'class': 'w-full font-mono text-sm'}),
        help_text='Введите JSON массив координат полигона. Пример: [[55.7558, 37.6176], [55.7559, 37.6177], ...]'
    )

    class Meta:
        model = ConstructionObject
        fields = ['org', 'name', 'description', 'plan_start', 'plan_end', 'polygon_raw']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full'}),
            'plan_start': forms.DateInput(attrs={'type': 'date', 'class': 'w-full'}),
            'plan_end': forms.DateInput(attrs={'type': 'date', 'class': 'w-full'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Limit org choices to user's organizations
        if self.user and not self.user.is_superuser:
            user_orgs = self.user.memberships.values_list('org', flat=True).distinct()
            self.fields['org'].queryset = Organization.objects.filter(id__in=user_orgs)
        
        # Set initial polygon if editing
        if self.instance and self.instance.pk and self.instance.polygon:
            self.fields['polygon_raw'].initial = json.dumps(self.instance.polygon, ensure_ascii=False, indent=2)
        else:
            self.fields['polygon_raw'].initial = json.dumps([], ensure_ascii=False, indent=2)

    def clean_polygon_raw(self):
        raw = self.cleaned_data['polygon_raw']
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise forms.ValidationError(f'Ошибка JSON: {e}')
        if not isinstance(parsed, list):
            raise forms.ValidationError('Геозона должна быть массивом координат (JSON array)')
        # Basic validation for coordinate array
        if parsed and not all(isinstance(coord, list) and len(coord) >= 2 for coord in parsed):
            raise forms.ValidationError('Каждая координата должна быть массивом [lat, lng]')
        self.cleaned_data['polygon'] = parsed
        return raw

    def save(self, commit=True):
        self.instance.polygon = self.cleaned_data.get('polygon', [])
        return super().save(commit=commit)


class OpeningChecklistForm(forms.ModelForm):
    # Represent JSON data as textarea for simple manual editing
    data_raw = forms.CharField(
        label='Данные (JSON)',
        widget=forms.Textarea(attrs={'rows': 12, 'class': 'w-full font-mono text-sm'}),
        help_text='Отредактируйте JSON структуру. Должен быть корректным JSON.'
    )

    class Meta:
        model = OpeningChecklist
        fields = ['data_raw']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.data:
            self.fields['data_raw'].initial = json.dumps(self.instance.data, ensure_ascii=False, indent=2)
        elif 'initial' in kwargs and kwargs['initial'].get('data_raw'):
            # leave as provided
            pass
        else:
            self.fields['data_raw'].initial = json.dumps({'items': []}, ensure_ascii=False, indent=2)

    def clean_data_raw(self):
        raw = self.cleaned_data['data_raw']
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise forms.ValidationError(f'Ошибка JSON: {e}')
        if not isinstance(parsed, dict):
            raise forms.ValidationError('Корневой элемент должен быть объектом (JSON object)')
        self.cleaned_data['data'] = parsed
        return raw

    def save(self, commit=True):
        self.instance.data = self.cleaned_data.get('data', {})
        return super().save(commit=commit)
