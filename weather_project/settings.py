import os
from pathlib import Path
import dj_database_url

# Base directory

BASE_DIR = Path(**file**).resolve().parent.parent

# SECURITY

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', '@&=86tw^0$*f*d^pjtod+-u3o)nkh9v5br**^#-*hi2%7=d4ha')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Hosts

ALLOWED_HOSTS = [
'localhost',
'127.0.0.1',
'.render.com',
'weather-analytics-dashboard-qy7d.onrender.com'
]

# Installed apps

INSTALLED_APPS = [
'django.contrib.admin',
'django.contrib.auth',
'django.contrib.contenttypes',
'django.contrib.sessions',
'django.contrib.messages',
'django.contrib.staticfiles',
'rest_framework',
'corsheaders',
'weather_app',
]

# Middleware

MIDDLEWARE = [
'django.middleware.security.SecurityMiddleware',
'whitenoise.middleware.WhiteNoiseMiddleware',
'django.contrib.sessions.middleware.SessionMiddleware',
'corsheaders.middleware.CorsMiddleware',
'django.middleware.common.CommonMiddleware',
'django.middleware.csrf.CsrfViewMiddleware',
'django.contrib.auth.middleware.AuthenticationMiddleware',
'django.contrib.messages.middleware.MessageMiddleware',
'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URLs & WSGI

ROOT_URLCONF = 'weather_project.urls'
WSGI_APPLICATION = 'weather_project.wsgi.application'

# Templates

TEMPLATES = [
{
'BACKEND': 'django.template.backends.django.DjangoTemplates',
'DIRS': [],
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

# Database

DATABASES = {
'default': dj_database_url.parse(os.getenv(
'DATABASE_URL',
'postgresql://weather_db_vyhi_user:Ae1HPI5LcAufzPnJzEN3x4cGZ8XeX6eB@dpg-d450l895pdvs73c2omg0-a.oregon-postgres.render.com/weather_db_vyhi'
))
}

# Password validation

AUTH_PASSWORD_VALIDATORS = [
{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST framework config

REST_FRAMEWORK = {
'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
'PAGE_SIZE': 10,
'DEFAULT_RENDERER_CLASSES': [
'rest_framework.renderers.JSONRenderer',
'rest_framework.renderers.BrowsableAPIRenderer',
],
}

# CORS

CORS_ALLOWED_ORIGINS = [
"http://localhost:3000",
"[http://127.0.0.1:3000](http://127.0.0.1:3000)",
]

# Security for production

if not DEBUG:
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# OpenWeatherMap API

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', 'b2146676cdfa655806c3fded53cb3387')
