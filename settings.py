"""
Django settings for ai_social_platform project.
"""

from pathlib import Path
import os
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

# Application definition
INSTALLED_APPS = [
  'django.contrib.admin',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.messages',
  'django.contrib.staticfiles',
  'django.contrib.sites',  # Required for allauth
  
  # Third party apps
  'allauth',
  'allauth.account',
  'allauth.socialaccount',
  'allauth.socialaccount.providers.google',
  
  # Local apps
  'core',  # Your main app
]

MIDDLEWARE = [
  'django.middleware.security.SecurityMiddleware',
  'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files in production
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.middleware.clickjacking.XFrameOptionsMiddleware',
  'allauth.account.middleware.AccountMiddleware',  # Required for allauth
]

ROOT_URLCONF = 'ai_social_platform.urls'

TEMPLATES = [
  {
      'BACKEND': 'django.template.backends.django.DjangoTemplates',
      'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'ai_social_platform.wsgi.application'

# Database - Using SQLite for simplicity
DATABASES = {
  'default': {
      'ENGINE': 'django.db.backends.sqlite3',
      'NAME': BASE_DIR / 'db.sqlite3',
  }
}

# Custom User Model
AUTH_USER_MODEL = 'core.CustomUser'

# Authentication backends
AUTHENTICATION_BACKENDS = [
  # Needed to login by username in Django admin
  'django.contrib.auth.backends.ModelBackend',
  # `allauth` specific authentication methods
  'allauth.account.auth_backends.AuthenticationBackend',
]

# Sites framework
SITE_ID = 1

# AllAuth settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_SIGNUP_REDIRECT_URL = '/'
ACCOUNT_LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# Social account settings
SOCIALACCOUNT_PROVIDERS = {
  'google': {
      'SCOPE': [
          'profile',
          'email',
      ],
      'AUTH_PARAMS': {
          'access_type': 'online',
      },
      'VERIFIED_EMAIL': True,
  }
}

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
  BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# API Configuration - Load from .env file with fallback


# Email Configuration (for password reset)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Login/Logout URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Security Settings for Production
if not DEBUG:
  SECURE_BROWSER_XSS_FILTER = True
  SECURE_CONTENT_TYPE_NOSNIFF = True
  SECURE_HSTS_INCLUDE_SUBDOMAINS = True
  SECURE_HSTS_SECONDS = 31536000
  SECURE_REDIRECT_EXEMPT = []
  SECURE_SSL_REDIRECT = True
  SESSION_COOKIE_SECURE = True
  CSRF_COOKIE_SECURE = True

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Cache Configuration (optional, for better performance)
CACHES = {
  'default': {
      'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
      'LOCATION': 'unique-snowflake',
  }
}

# Logging Configuration
LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'handlers': {
      'file': {
          'level': 'INFO',
          'class': 'logging.FileHandler',
          'filename': BASE_DIR / 'django.log',
      },
  },
  'loggers': {
      'django': {
          'handlers': ['file'],
          'level': 'INFO',
          'propagate': True,
      },
  },
}
