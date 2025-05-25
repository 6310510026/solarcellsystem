# plant/forms.py
from django import forms
from .models import DroneInspection

class DroneInspectionForm(forms.ModelForm):
    class Meta:
        model = DroneInspection
        fields = ['plant', 'zone', 'image', 'description', 'captured_date', 'captured_time']
        widgets = {
            'captured_date': forms.DateInput(attrs={'type': 'date'}),
            'captured_time': forms.TimeInput(attrs={'type': 'time'}),
        }
