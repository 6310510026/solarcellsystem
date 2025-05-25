from django.contrib import admin
from .models import DroneInspection
# Register your models here.

@admin.register(DroneInspection)
class DroneInspectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'plant', 'zone', 'captured_by', 'status', 'captured_at')
    list_filter = ('status', 'plant', 'zone')
    search_fields = ('description',)
