# hypertension_system/urls.py
from django.contrib import admin
from django.urls import path, include
from core_fixed.hypertension import views as googlefit_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Main hypertension app
    path('', include('hypertension.urls')),
    path('signup/', include('hypertension.urls_signup')),

    # ⭐ GOOGLE FIT ROUTES (THESE WERE MISSING)
    path('googlefit/connect/', googlefit_views.googlefit_connect, name='googlefit_connect'),
    path('googlefit/callback/', googlefit_views.googlefit_callback, name='googlefit_callback'),
]
