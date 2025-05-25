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
    captured_date = models.DateField(verbose_name="Image Date")
    captured_time = models.TimeField(verbose_name="Image Time")

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


