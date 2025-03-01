from django.urls import path
from .views import index, register_page, login_page, logout_page, plant_owner_dashboard, data_analyst_dashboard, drone_controller_dashboard, success

urlpatterns = [
    path("", index, name="index"),
    path('register/', register_page, name='register_page'),
    path('login/', login_page, name='login_page'),
    path('logout/', logout_page, name='logout_page'),
    path('success/', success,name='success'),
    path('dashboard/plant_owner/', plant_owner_dashboard, name='plant_owner_dashboard'),
    path('dashboard/data_analyst/', data_analyst_dashboard, name='data_analyst_dashboard'),
    path('dashboard/drone_controller', drone_controller_dashboard, name='drone_controller_dashboard'),
    
]
