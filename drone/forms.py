# plant/forms.py
from django import forms
from .models import DroneInspection
from plant.models import SolarPlant, Zone

class DroneInspectionForm(forms.ModelForm):
    class Meta:
        model = DroneInspection
        fields = ['plant', 'zone', 'image', 'description', 'captured_date', 'captured_time']
        widgets = {
            'captured_date': forms.DateInput(attrs={'type': 'date'}),
            'captured_time': forms.TimeInput(attrs={'type': 'time'}),
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # ⬅️ ดึง user ออกมาก่อน
        super().__init__(*args, **kwargs)

        if user and hasattr(user, 'role') and user.role == 'drone_controller':
            self.fields['plant'].queryset = SolarPlant.objects.filter(drone_controller=user)
        else:
            self.fields['plant'].queryset = SolarPlant.objects.none()

        # Dynamic zone filtering
        if 'plant' in self.data:
            try:
                plant_id = int(self.data.get('plant'))
                self.fields['zone'].queryset = Zone.objects.filter(plant_id=plant_id)
            except (ValueError, TypeError):
                self.fields['zone'].queryset = Zone.objects.none()
        elif self.instance.pk:
            self.fields['zone'].queryset = Zone.objects.filter(plant=self.instance.plant)
        else:
            self.fields['zone'].queryset = Zone.objects.none()


