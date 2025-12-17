from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
	path('admin/', admin.site.urls),
	# Redirect bare root to dashboard (app mounted at /dashboard/)
	path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
	path('dashboard/', include('hypertension.urls')),
]

