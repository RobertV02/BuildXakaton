from django import forms
from .models import OpeningChecklist
import json


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
