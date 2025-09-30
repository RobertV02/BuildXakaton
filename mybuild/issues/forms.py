from django import forms
from .models import Remark, IssueCategory

class RemarkForm(forms.ModelForm):
    class Meta:
        model = Remark
        fields = ['category', 'name', 'fixability', 'issue_type', 'description', 'severity', 'resolution_deadline_days']
        widgets = {
            'category': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300', 'required': 'required'}),
            'name': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300', 'required': 'required'}),
            'fixability': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300', 'required': 'required'}),
            'issue_type': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300', 'required': 'required'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full rounded-md border-gray-300'}),
            'severity': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300', 'required': 'required'}),
            'resolution_deadline_days': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300', 'placeholder': 'Число дней или -'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove queryset since category is now CharField

    def clean(self):
        cleaned_data = super().clean()
        fixability = cleaned_data.get('fixability')
        resolution_deadline_days = cleaned_data.get('resolution_deadline_days')
        
        if fixability == 'NON_FIXABLE':
            if resolution_deadline_days != '-':
                cleaned_data['resolution_deadline_days'] = '-'
        
        return cleaned_data

    def clean_resolution_deadline_days(self):
        data = self.cleaned_data['resolution_deadline_days']
        if data and data != '-':
            try:
                num = int(data)
                if num <= 0:
                    raise forms.ValidationError("Срок должен быть положительным числом.")
            except ValueError:
                raise forms.ValidationError("Срок должен быть числом или '-'.")
        return data
