from django.urls import path
from .views import register_user, login_user, logout_user, role_redirect, plant_owner_dashboard_view, data_analyst_dashboard_view, drone_controller_dashboard_view, plant_detail_analyst_view, data_analyst_analytics_view, panel_analytics_view, complete_profile

urlpatterns = [
    path('signup/', register_user, name='register_page'),
    path('login/', login_user, name='login_page'),
    path('logout/', logout_user, name='logout_page'),
    path('redirect/', role_redirect, name='role_redirect'),
    path('dashboard/plant-owner/', plant_owner_dashboard_view, name='plant_owner_dashboard'),
    path('dashboard/data-analyst/', data_analyst_dashboard_view, name='data_analyst_dashboard'),
    path('dashboard/drone-controller/', drone_controller_dashboard_view, name='drone_controller_dashboard'),
    path('dashboard/data-analyst/plant/<int:plant_id>/', plant_detail_analyst_view, name='plant_detail_analyst'),
    path('dashboard/data-analyst/analytics/', data_analyst_analytics_view, name='data_analyst_analytics'),
    path('dashboard/data-analyst/analytics/<int:plant_id>/', panel_analytics_view, name='panel_analytics'),
    path('complete-profile/', complete_profile, name='complete_profile'),
]