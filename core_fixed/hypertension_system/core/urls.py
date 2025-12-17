from django.contrib import admin
from django.urls import path, include
from core import views as core_views  # Google Fit views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Dashboard
    path('dashboard/', include('hypertension.urls')),

    # Accounts
    path('accounts/signup/', include('accounts.urls_signup')),
    path('accounts/', include('accounts.urls')),

    # BP and other sections
    path('bp/', include('bp.urls')),
    path('medications/', include('medications.urls')),
    path('salt/', include('salt.urls')),
    path('food/', include('food.urls')),
    path('devices/', include('devices.urls')),
    path('reminders/', include('reminders.urls')),

    # Google Fit OAuth Endpoints
    path('googlefit/connect/', core_views.googlefit_connect, name='googlefit_connect'),
    path('googlefit/callback/', core_views.googlefit_callback, name='googlefit_callback'),
]
