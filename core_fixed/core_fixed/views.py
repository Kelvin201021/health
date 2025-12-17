from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def googlefit_connect(request):
    return HttpResponse("Google Fit connect placeholder working.")

def googlefit_callback(request):
    return HttpResponse("Google Fit callback placeholder working.")

def googlefit_sync_blood_pressure(request):
    return HttpResponse("Google Fit blood pressure sync placeholder working.")

@login_required
def home(request):
    return render(request, "dashboard.html")
