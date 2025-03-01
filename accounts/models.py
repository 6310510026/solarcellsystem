# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("site_admin", "Site Admin"),     # ผู้ดูแลเว็บไซต์
        ("plant_owner", "Plant Owner"),  
        ("data_analyst", "Data Analyst"),  
        ("drone_controller", "Drone Controller"),        
        
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="plant_owner")


    def is_site_admin(self):
        return self.role == "site_admin"

    def is_plant_owner(self):
        return self.role == "plant_owner"

    def is_data_analyst(self):
        return self.role == "data_analyst"

    def is_drone_controller(self):
        return self.role == "drone_controller"

    def formatted_id(self):
        """แสดง ID เป็น 3 หลัก เช่น 001, 002, 100"""
        return str(self.id).zfill(3)

    def save(self, *args, **kwargs):
        if self.is_staff and self.role not in ["site_admin"]:
            self.role = "site_admin"
        super().save(*args, **kwargs)

    def __str__(self):
        """แสดง ID เป็น 3 หลักตอนแสดงใน Django Admin หรือ QuerySet"""
        return f"{self.username} (ID: {self.formatted_id()})"
