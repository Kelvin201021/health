# core_fixed/googlefit_urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("connect/", views.googlefit_connect, name="googlefit_connect"),
    path("callback/", views.googlefit_callback, name="googlefit_callback"),
]
