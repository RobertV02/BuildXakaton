from django import forms
from .models import Remark, IssueCategory

class RemarkForm(forms.ModelForm):
    class Meta:
        model = Remark
        fields = ['category', 'name', 'fixability', 'issue_type', 'description', 'severity', 'resolution_deadline_days']
        widgets = {
            'category': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300'}),
            'name': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300'}),
            'fixability': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300'}),
            'issue_type': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full rounded-md border-gray-300'}),
            'severity': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300'}),
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
        elif fixability == 'FIXABLE' and resolution_deadline_days and resolution_deadline_days != '-':
            try:
                days = int(resolution_deadline_days)
                if days <= 0:
                    raise forms.ValidationError("Срок должен быть положительным числом.")
                if days % 2 != 0:
                    raise forms.ValidationError("Срок должен быть четным числом.")
            except ValueError:
                raise forms.ValidationError("Срок должен быть числом или '-'.")
        
        return cleaned_data
