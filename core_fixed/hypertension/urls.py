from django.urls import path
from . import views, views_sodium

app_name = "hypertension"

urlpatterns = [
    path("connect-watch/", views.connect_watch, name="connect_watch"),
    # Dashboard at app root
    path("", views.dashboard_view, name="dashboard"),
    # Separate elder-friendly graphs
    path("graph/manual/", views.manual_bp_graph, name="manual_bp_graph"),
    path("graph/watch/", views.watch_bp_graph, name="watch_bp_graph"),

    # BP CRUD (moved under /readings/)
    path("readings/", views.bp_list, name="bp_list"),
    path("readings/new/", views.bp_create, name="bp_create"),
    path("readings/<int:pk>/edit/", views.bp_edit, name="bp_edit"),
    path("readings/<int:pk>/delete/", views.bp_delete, name="bp_delete"),

    # Quick Access / section pages (used by dashboard tiles)
    path("bp/home/", views.bp_home, name="bp_home"),
    path("medications/", views.medications_home, name="medications_home"),
    path("salt/", views.salt_home, name="salt_home"),
    path("food/", views.food_home, name="food_home"),
    path("devices/", views.devices_home, name="devices_home"),
    path("devices/connect/", views.connect_watch, name="connect_watch"),
    # Sodium intake API
    path('api/sodium/add-meal/', views_sodium.api_add_meal, name='api_add_meal'),
    path('api/sodium/today/', views_sodium.api_today_summary, name='api_today_summary'),
    path('api/sodium/weekly/', views_sodium.api_weekly_summary, name='api_weekly_summary'),
    path('api/sodium/alerts/', views_sodium.api_get_alerts, name='api_get_alerts'),
    path("reminders/", views.reminders_home, name="reminders_home"),
]
