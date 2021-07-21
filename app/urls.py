from django.urls import path
from django.urls import path, include

urlpatterns = [
    path('logs', include('watering_logs.urls')),
]
