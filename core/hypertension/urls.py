from django.urls import path
from . import views

app_name = "hypertension"

urlpatterns = [
    # BP CRUD (list is root of the app)
    path("", views.bp_list, name="bp_list"),
    path("new/", views.bp_create, name="bp_create"),
    path("<int:pk>/edit/", views.bp_edit, name="bp_edit"),
    path("<int:pk>/delete/", views.bp_delete, name="bp_delete"),

    # Quick Access / section pages (used by dashboard tiles)
    path("bp/home/", views.bp_home, name="bp_home"),
    path("medications/", views.medications_home, name="medications_home"),
    path("salt/", views.salt_home, name="salt_home"),
    path("food/", views.food_home, name="food_home"),
    path("devices/", views.devices_home, name="devices_home"),
    path("reminders/", views.reminders_home, name="reminders_home"),
]
