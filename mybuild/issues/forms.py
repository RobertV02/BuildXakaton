from django import forms
from .models import Remark, IssueCategory

class RemarkForm(forms.ModelForm):
    class Meta:
        model = Remark
        fields = ['category', 'name', 'fixability', 'issue_type', 'description', 'severity', 'resolution_deadline_days']
        widgets = {
            'category': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300'}),
            'name': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300'}),
            'fixability': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300'}),
            'issue_type': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full rounded-md border-gray-300'}),
            'severity': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300'}),
            'resolution_deadline_days': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300', 'placeholder': 'Число дней или -'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = IssueCategory.objects.order_by('title')
