"""
Django settings for core_fixed project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-dev-only-replace-in-production")

DEBUG = True

ALLOWED_HOSTS = ["*"]   # allow local testing


# ---------------------------------------------------------
# APPLICATIONS
# ---------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your app
    'hypertension',
]


# ---------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Device token middleware maps `Authorization: Token <token>` or `X-Device-Token`
    # to `request.device` and sets `request.user` to the device owner for API device posts.
    'hypertension.middleware.DeviceTokenMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ---------------------------------------------------------
# URLS / WSGI
# ---------------------------------------------------------

ROOT_URLCONF = 'core_fixed.urls'


WSGI_APPLICATION = 'core_fixed.wsgi.application'


# ---------------------------------------------------------
# TEMPLATES
# ---------------------------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / "templates",  # Global templates folder
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ---------------------------------------------------------
# AUTHENTICATION SETTINGS
# ---------------------------------------------------------

LOGIN_REDIRECT_URL = "hypertension:dashboard"
LOGOUT_REDIRECT_URL = "login"


# ---------------------------------------------------------
# PASSWORD VALIDATION
# ---------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------------------------------------------------------
# LANGUAGE / TIME SETTINGS
# ---------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'   # Correct for India
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------
# STATIC FILES
# ---------------------------------------------------------

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# ---------------------------------------------------------
# DEFAULT PRIMARY KEY
# ---------------------------------------------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# ============================
# GOOGLE FIT OAUTH SETTINGS
# ============================

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "http://127.0.0.1:8000/googlefit/callback/")
GOOGLE_AUTH_SCOPE = "https://www.googleapis.com/auth/fitness.activity.read https://www.googleapis.com/auth/fitness.heart_rate.read"

