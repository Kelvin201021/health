from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Main hypertension app
    path('', include('hypertension.urls')),
    path('signup/', include('hypertension.urls_signup')),

    # Google Fit OAuth Routes
    path('googlefit/', include('core_fixed.googlefit_urls')),
]
