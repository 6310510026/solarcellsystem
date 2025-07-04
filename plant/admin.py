
# Register your models here.

from django.contrib import admin
import nested_admin
from .models import SolarPlant, Zone, PanelRow, SolarPanel, InspectionReport

class SolarPanelInline(nested_admin.NestedTabularInline):
    model = SolarPanel
    extra = 1

class PanelRowInline(nested_admin.NestedTabularInline):
    model = PanelRow
    extra = 1
    inlines = [SolarPanelInline]

class ZoneInline(nested_admin.NestedStackedInline):
    model = Zone
    extra = 1
    inlines = [PanelRowInline]

@admin.register(SolarPlant)
class SolarPlantAdmin(nested_admin.NestedModelAdmin):
    list_display = ('name', 'location', 'owner', 'data_analyst', 'drone_controller')  # ✅ เพิ่ม 2 ตำแหน่งนี้ให้เห็นใน list
    inlines = [ZoneInline]

@admin.register(InspectionReport)
class DummyInspectionReportAdmin(admin.ModelAdmin):
    list_display = ('plant', 'is_analyzed', 'report_date')
    list_filter = ('is_analyzed', 'report_date')
    search_fields = ('plant__name',)
