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

from django import forms
from .models import SolarPlant, Zone, PanelRow, SolarPanel
from django.forms import inlineformset_factory

class SolarPlantForm(forms.ModelForm):
    class Meta:
        model = SolarPlant
        fields = ['name', 'latitude', 'longitude', 'location', 'installed_capacity_kw', 'description', 'data_analyst', 'drone_controller']

class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = ['name']

class PanelRowForm(forms.ModelForm):
    class Meta:
        model = PanelRow
        fields = ['row_number']

class SolarPanelForm(forms.ModelForm):
    class Meta:
        model = SolarPanel
        fields = ['column_number', 'serial_number', 'is_active']


# Inline formsets
ZoneFormSet = inlineformset_factory(SolarPlant, Zone, form=ZoneForm, extra=1, can_delete=False)
PanelRowFormSet = inlineformset_factory(Zone, PanelRow, form=PanelRowForm, extra=1, can_delete=False)
SolarPanelFormSet = inlineformset_factory(PanelRow, SolarPanel, form=SolarPanelForm, extra=1, can_delete=False)
