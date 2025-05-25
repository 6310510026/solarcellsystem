from django.db import models
from django.conf import settings
# Create your models here.


# 1. โรงไฟฟ้า
class SolarPlant(models.Model):
    name = models.CharField(max_length=255, verbose_name="ชื่อโรงไฟฟ้า")
    location = models.CharField(max_length=255, verbose_name="ที่ตั้ง")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='plants',
        verbose_name="เจ้าของโรง"
    )
    installed_capacity_kw = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        verbose_name="กำลังการผลิต (kW)"
    )
    description = models.TextField(blank=True, verbose_name="รายละเอียดเพิ่มเติม")
    created_at = models.DateTimeField(auto_now_add=True)

    data_analyst = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'role': 'data_analyst'},
        related_name='assigned_analyst_plants',
        verbose_name="นักวิเคราะห์ข้อมูล"
    )
    drone_controller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'role': 'drone_controller'},
        related_name='assigned_drone_plants',
        verbose_name="ผู้ควบคุมโดรน"
    )
    
    def __str__(self):
        return f"{self.name} ({self.location})"

    def save(self, *args, **kwargs):
        # ✅ ป้องกันคนที่ไม่ใช่ plant_owner
        if self.owner.role != 'plant_owner':
            raise PermissionError("เฉพาะผู้ใช้ที่เป็น plant_owner เท่านั้นที่สามารถสร้างโรงไฟฟ้าได้")

        is_new = self.pk is None
        super().save(*args, **kwargs)



# 2. โซนในโรงไฟฟ้า
class Zone(models.Model):
    plant = models.ForeignKey(SolarPlant, on_delete=models.CASCADE, related_name='zones')
    name = models.CharField(max_length=50, verbose_name="ชื่อโซน")  # เช่น Zone A, B, Main Zone

    class Meta:
        unique_together = ('plant', 'name')
    def __str__(self):
        return f"{self.name} - {self.plant.name}"


# 3. แถวของแผงในโซน
class PanelRow(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='rows')
    row_number = models.PositiveIntegerField(verbose_name="แถวที่")  # เช่น แถวที่ 1, 2, 3

    def __str__(self):
        return f"Row {self.row_number} - {self.zone.name}"


# 4. แผงโซลาร์เซลล์แต่ละแผง
class SolarPanel(models.Model):
    row = models.ForeignKey(PanelRow, on_delete=models.CASCADE, related_name='panels')
    column_number = models.PositiveIntegerField(verbose_name="คอลัมน์ที่")  # เช่น คอลัมน์ 1, 2, 3
    serial_number = models.CharField(max_length=100, blank=True, verbose_name="Serial Number")
    is_active = models.BooleanField(default=True, verbose_name="ใช้งานอยู่")

    def __str__(self):
        return f"Panel R{self.row.row_number}-C{self.column_number} ({self.row.zone.name} / {self.row.zone.plant.name})"
