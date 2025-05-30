from django import forms
from django.contrib.auth import get_user_model  # ✅ ใช้เพื่อดึง Custom User Model อย่างปลอดภัย
from .models import SolarPlant, Zone, PanelRow, SolarPanel
from django.forms import inlineformset_factory

User = get_user_model()  # ✅ ดึงโมเดลผู้ใช้ที่ใช้อยู่ในโปรเจกต์ (custom หรือ default)

# ฟอร์มสำหรับสร้าง SolarPlant โดยกรองรายชื่อผู้ใช้ตาม role
class SolarPlantForm(forms.ModelForm):
    class Meta:
        model = SolarPlant
        fields = ['name', 'latitude', 'longitude', 'location', 'installed_capacity_kw', 'description', 'data_analyst', 'drone_controller']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # รับผู้ใช้เพื่อใช้ในการกรองสิทธิ์
        super().__init__(*args, **kwargs)
        if user:
            self.fields['data_analyst'].queryset = User.objects.filter(role='data_analyst')
            self.fields['drone_controller'].queryset = User.objects.filter(role='drone_controller')
        else:
            # ถ้าไม่มี user ส่งมา จะไม่แสดงข้อมูลเลย (ป้องกัน error)
            self.fields['data_analyst'].queryset = User.objects.none()
            self.fields['drone_controller'].queryset = User.objects.none()

# ฟอร์มสำหรับโซน
class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = ['name']

# ฟอร์มสำหรับแถวแผง
class PanelRowForm(forms.ModelForm):
    class Meta:
        model = PanelRow
        fields = ['row_number']

# ฟอร์มสำหรับแผงพลังงานแสงอาทิตย์
class SolarPanelForm(forms.ModelForm):
    class Meta:
        model = SolarPanel
        fields = ['column_number', 'serial_number', 'is_active']

# Inline formsets สำหรับสร้างฟอร์มลูกต่อเนื่อง
ZoneFormSet = inlineformset_factory(SolarPlant, Zone, form=ZoneForm, extra=1, can_delete=False)
PanelRowFormSet = inlineformset_factory(Zone, PanelRow, form=PanelRowForm, extra=1, can_delete=False)
SolarPanelFormSet = inlineformset_factory(PanelRow, SolarPanel, form=SolarPanelForm, extra=1, can_delete=False)

