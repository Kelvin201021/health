from django.contrib import admin
from django.urls import path, include
from core import views as core_views   # Google Fit views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Main app URLs
    path('dashboard/', include('hypertension.urls')),
    path('signup/', include('hypertension.urls_signup')),

    # Google Fit OAuth Endpoints
    path('googlefit/connect/', core_views.googlefit_connect, name='googlefit_connect'),
    path('googlefit/callback/', core_views.googlefit_callback, name='googlefit_callback'),
]
