from django.shortcuts import render
from watering_handler.apps import do_watering

def custom_watering(request):
    do_watering()
    return render(request, 'custom_watering.html', {})