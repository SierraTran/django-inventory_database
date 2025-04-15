"""
Django settings for inventory_database project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from django.core.management.commands.runserver import Command as runserver
from pathlib import Path
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Media files (Uploaded by users)
MEDIA_ROOT = os.path.join(BASE_DIR, "public/static")
MEDIA_URL = "/media/"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fallback-secret-key-for-dev")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEST_OUTPUT_VERBOSE = True

ALLOWED_HOSTS = ['*']
runserver.default_port = '8000'
runserver.default_addr = '127.0.0.1'

SECURE_SSL_REDIRECT = True

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "haystack",
    "coverage",
    "inventory_database",
    "inventory",
    "authentication",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "inventory_database.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [            
            BASE_DIR / "authentication/templates/authentication",
            BASE_DIR / "inventory/templates/inventory",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'authentication.context_processors.unread_notifications_count',
            ],
        },
    },
]

WSGI_APPLICATION = "inventory_database.wsgi.application"

# Haystack Configuration

HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "haystack.backends.whoosh_backend.WhooshEngine",
        "PATH": os.path.join(BASE_DIR, "whoosh_index"),
    },
}

#This setting will update search indexes
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# For sqlany-django,
# DATABASES = {
#   'default' : {
#       'ENGINE': 'sqlany_django',
#       'NAME': 'django',
#       'USER': 'dba',
#       'PASSWORD': 'sql',
#       'HOST': 'myhost',
#       'PORT': 'portnum'
#   }
# }


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

# Since this project is only going to be used by Hayes Instruments,
# I used the EST timezone.
DATETIME_FORMAT = "%Y-%m-%d %I:%M:%S %p"

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"

# Absolute path for collected static files
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


# Additional locations for the static app to traverse to for static files

STATICFILES_DIRS = [
    BASE_DIR / "authentication/static",
    BASE_DIR / "inventory/static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# will bring the user back to "/inventory_database/"
LOGIN_REDIRECT_URL = "/inventory_database/"

# will bring the user back to the login page ("/inventory_database/accounts/login/")
LOGOUT_REDIRECT_URL = "/inventory_database/accounts/login/"

# This marks session cookies as secure, making it more difficult for network 
# traffic sniffers to hijack user sessions.
SESSION_COOKIE_SECURE = True

# If the user closes the browser, the session will expire and the user will
# have to log in again.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# This marks CSRF cookies as secure, making it more difficult for network 
# traffic sniffers to steal the CSRF token.
CSRF_COOKIE_SECURE = True

# Message storage for the messages framework
# https://docs.djangoproject.com/en/5.1/ref/settings/#message-storage
# This setting handles both sessions and cookies
MESSAGE_STORAGE = "django.contrib.messages.storage.fallback.FallbackStorage"