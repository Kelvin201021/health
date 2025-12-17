from django.contrib import admin
from django.urls import path, include
from .views import landing_page

urlpatterns = [
    path("", landing_page, name="landing_page"),
    path("admin/", admin.site.urls),

    # Login / Logout (Django built-in)
    path("accounts/", include("django.contrib.auth.urls")),

    # Signup Route
    path("signup/", include("hypertension.urls_signup")),

    # Hypertension App (dashboard + BP pages)
    path("dashboard/", include("hypertension.urls")),

    # Google Fit routes
    path("googlefit/", include("core_fixed.googlefit_urls")),
]

