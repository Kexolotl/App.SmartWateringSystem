from django.urls import path
from watering_logs import views

urlpatterns = [
    path('<int:lines>', views.logs, name='logs'),
    path('', views.logs, name='logs')
]