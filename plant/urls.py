from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.create_plant, name='create_plant'),
    path('create/zone/<int:plant_id>/', views.create_zone, name='create_zone'),
    path('create/panel-row/<int:zone_id>/', views.create_panel_row, name='create_panel_row'),
    path('create/solar-panel/<int:panel_row_id>/', views.create_solar_panel, name='create_solar_panel'),
    path('my-plants/', views.plant_list_view, name='plant_list'),
    path('delete/<int:pk>/', views.delete_plant, name='delete_plant'),
    path('edit/<int:pk>/', views.edit_plant, name='edit_plant'),
    path('detail/<int:pk>/', views.plant_detail_view, name='plant_detail_solar'),
    path('report/', views.plant_report_view, name='plant_report'),
    path('report/<int:report_id>/', views.view_report, name='view_report'), 

]
