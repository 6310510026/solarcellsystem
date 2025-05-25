from django import forms
from .models import SolarPlant

class SolarPlantForm(forms.ModelForm):
    class Meta:
        model = SolarPlant
        fields = ['name', 'location', 'installed_capacity_kw', 'description', 'data_analyst', 'drone_controller']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # เอาไว้จำกัดสิทธิ
        super().__init__(*args, **kwargs)
        self.fields['data_analyst'].queryset = user.__class__.objects.filter(role='data_analyst')
        self.fields['drone_controller'].queryset = user.__class__.objects.filter(role='drone_controller')
