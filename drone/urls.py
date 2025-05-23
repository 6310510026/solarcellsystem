# drone/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('upload-inspection/', views.upload_inspection, name='upload_inspection'),
    path('status/', views.drone_status_view, name='drone_status'),
]
