from django.urls import path
from . import views

app_name = "disaster_notification_system"

urlpatterns = [
    # interactive map
    path('', views.disaster_notification_system, name = 'home'),
    path('recent_fire/', views.get_recent_bushfires, name='recent_fire'),
    path('weather/', views.get_weather_data, name='weather'),
    path('get_user_properties/', views.get_user_properties, name='get_user_properties'),
    path('get_predicted_bushfire/', views.get_predicted_bushfire, name='get_predicted_bushfire'),
    path('get_predicted_bushfire_path/', views.get_path, name='get_predicted_bushfire_path'),
]