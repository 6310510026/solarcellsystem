# plant/forms.py
from django import forms
from .models import DroneInspection

class DroneInspectionForm(forms.ModelForm):
    class Meta:
        model = DroneInspection
        fields = ['plant', 'zone', 'image', 'description']
