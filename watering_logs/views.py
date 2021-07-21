import os.path

from django.shortcuts import render

def logs(request, maxOutputLines=None):
    log_filename = "app_smartwateringsystem.log"
    context = {
        'lines': []
    }
    if not os.path.isfile(log_filename):
        return render(request, 'watering_logs.html', context)
        
    log_file = open(log_filename, "r")
    lines = log_file.readlines()
    log_file.close()

    if (maxOutputLines is not None):
        maxOutputLines = 0 - maxOutputLines
    else:
        maxOutputLines = -1000

    context = {
        'lines': lines[maxOutputLines:]
    }
    return render(request, 'watering_logs.html', context)