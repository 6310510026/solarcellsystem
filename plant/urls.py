from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.create_plant, name='create_plant'),
    path('my-plants/', views.plant_list_view, name='plant_list'),
    path('delete/<int:pk>/', views.delete_plant, name='delete_plant'),
]
