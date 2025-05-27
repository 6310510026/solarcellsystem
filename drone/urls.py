# drone/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('upload-inspection/', views.upload_inspection, name='upload_inspection'),
    path('status/', views.drone_status_view, name='drone_status'),
    path('edit-inspection/<int:inspection_id>/', views.edit_inspection, name='edit_inspection'),
    path('plant/<int:plant_id>/', views.plant_detail_view, name='plant_detail'),
]
