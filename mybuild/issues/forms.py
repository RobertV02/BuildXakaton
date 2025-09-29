from django import forms
from .models import Remark, IssueCategory

class RemarkForm(forms.ModelForm):
    class Meta:
        model = Remark
        fields = ['category', 'description', 'severity']
        widgets = {
            'category': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full rounded-md border-gray-300'}),
            'severity': forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = IssueCategory.objects.order_by('title')
