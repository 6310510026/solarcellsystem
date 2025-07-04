from django.db import models
from plant.models import SolarPlant, Zone
from django.conf import settings


# Create your models here.
class DroneInspection(models.Model):
    STATUS_CHOICES = [
        ('pending', 'ยังไม่วิเคราะห์'),
        ('analyzed', 'วิเคราะห์แล้ว'),
        ('issue_found', 'พบปัญหา'),
        ('complete', 'แก้ไขแล้ว'),
    ]

    plant = models.ForeignKey('plant.SolarPlant', on_delete=models.CASCADE)
    zone = models.ForeignKey('plant.Zone', on_delete=models.CASCADE)
    captured_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to="inspections/")
    description = models.TextField(blank=True)
    captured_date = models.DateField(verbose_name="Image Date", null=True, blank=True)
    captured_time = models.TimeField(verbose_name="Image Time", null=True, blank=True)

    # ✅ เวลาที่ระบบบันทึกจริง
    captured_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    analyzed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analyzed_inspections'
    )

    def __str__(self):
        return f"Inspection {self.pk} @ {self.zone.name} - {self.get_status_display()}"



# drone/models.py

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=50, choices=[
        ('task_status', 'Task Status Changed'),
        ('new_plant', 'New Plant Assigned'),
        ('new_zone', 'New Zone Added'),
        ('new_panel', 'New Panel Added'),
    ])

    def __str__(self):
        return f"[{self.type}] {self.message[:30]}"