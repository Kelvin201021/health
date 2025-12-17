# -----------------------------
# Quick Access Placeholder Views
# -----------------------------

from django.shortcuts import render

def bp_home(request):
    return render(request, "sections/bp_home.html")

def medications_home(request):
    return render(request, "sections/medications_home.html")

def salt_home(request):
    return render(request, "sections/salt_home.html")

def food_home(request):
    return render(request, "sections/food_home.html")

def devices_home(request):
    return render(request, "sections/devices_home.html")

def reminders_home(request):
    return render(request, "sections/reminders_home.html")

def landing_page(request):
    return render(request, 'landing.html')
