from django.contrib import admin
from django.urls import path, include
from .views import landing_page
from hypertension import views as hypertension_views
from hypertension.views import MyLoginView 

urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('admin/', admin.site.urls),
    path('dashboard/', include('hypertension.urls')),
    path('accounts/login/', MyLoginView.as_view(), name='login'),
    path('signup/', include('hypertension.urls_signup')),
    path('googlefit/', include('core_fixed.googlefit_urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

