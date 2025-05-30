# drone/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('upload-inspection/', views.upload_inspection, name='upload_inspection'),
    path('status/', views.drone_status_view, name='drone_status'),
    path('edit-inspection/<int:inspection_id>/', views.edit_inspection, name='edit_inspection'),
    path('plant/<int:plant_id>/', views.plant_detail_view, name='plant_detail'),
    path('ajax/zones/<int:plant_id>/', views.ajax_get_zones_by_plant, name='ajax_get_zones'),
    path('tasks/', views.drone_task_view, name='drone_tasks'),
    path('notifications/', views.notification_view, name='notifications'),
]
