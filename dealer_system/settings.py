import os
import dj_database_url
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-this-later")

# Keep True until site opens properly, later change to False
DEBUG = os.getenv("DEBUG", "True") == "True"


# ALLOWED HOSTS
ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "dealer-system.onrender.com,localhost,127.0.0.1"
).split(",")

# CSRF
CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS",
    "https://dealer-system.onrender.com"
).split(",")

# Render / proxy settings
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False


# APPLICATIONS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core',
]


# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# URL CONFIG
ROOT_URLCONF = 'dealer_system.urls'


# TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# WSGI
WSGI_APPLICATION = 'dealer_system.wsgi.application'


# DATABASE
BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# PASSWORD VALIDATION
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# INTERNATIONALIZATION
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True


# STATIC FILES
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# MEDIA FILES
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# DEFAULT PRIMARY KEY FIELD TYPE
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'