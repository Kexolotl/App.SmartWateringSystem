from django.urls import path
from watering_handler import views

urlpatterns = [
    path('', views.custom_watering, name='custom_watering')
]