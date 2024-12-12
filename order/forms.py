from django import forms
from eval.models import WorkDayAssignment

class WorkDayAssignmentForm(forms.ModelForm):
    class Meta:
        model = WorkDayAssignment
        fields = ['project', 'assigned_hours', 'work_performed']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'assigned_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'work_performed': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_assigned_hours(self):
        assigned_hours = self.cleaned_data['assigned_hours']
        if assigned_hours < 0.5:
            raise forms.ValidationError(_("Assigned hours must be at least 0.5 hours."))
        return assigned_hours
