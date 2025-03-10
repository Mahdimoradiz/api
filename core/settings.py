"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from datetime import timedelta
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-z9a6&3*8wl@5wf0r_bar86m_v6-f!2xd07&!f-66tj^0@*qy6m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'import_export',
    'rangefilter',
    'corsheaders',
    'django_filters',
    'drf_yasg',
    'captcha',
    'axes',
    # apps
    
    'profiles.apps.ProfilesConfig',
    'post.apps.PostConfig',
    'user.apps.UserConfig',
    'live.apps.LiveConfig',
]



AXES_FAILURE_LIMIT = 5  
AXES_COOLOFF_TIME = timedelta(minutes=15) 


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR]
        ,
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


WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# This section is for configuring the production environment

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'nexsocia_mysql',
#         'USER': 'nexsocia_mehdi',
#         'PASSWORD': 'ahcrD2xs)8?q',
#         'HOST': 'https://nexsocial.ir/',
#         'PORT': '3306',
#         'OPTIONS': {
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#         },
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CORS_ALLOW_ALL_ORIGINS = True

# Allowed file types for uploads

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm']
ALLOWED_FILE_TYPES = ALLOWED_IMAGE_TYPES + ALLOWED_VIDEO_TYPES

# Video upload limits

VIDEO_LIMITS = {
    'feed': {'duration': 60, 'size': 15 * 1024 * 1024},  # 60 seconds, 15 MB
    'reels': {'duration': 60, 'size': 15 * 1024 * 1024},  # 60 seconds, 15 MB
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=29), 
    'REFRESH_TOKEN_LIFETIME': timedelta(days=29),    
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',                           
    'SIGNING_KEY': SECRET_KEY,                       
    'VERIFYING_KEY': None,
}

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}


AUTH_USER_MODEL = "user.User"




AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  
    'django.contrib.auth.backends.ModelBackend', 
]

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

ASGI_APPLICATION = 'your_project.asgi.application'

MAX_LOGIN_ATTEMPTS = 5
MAX_SIGNUP_ATTEMPTS = 3

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your@email.com'
EMAIL_HOST_PASSWORD = 'your-password'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'


ACCOUNT_REACTIVATION_DAYS = 30  
TWO_FACTOR_TIMEOUT = 300 

# تنظیمات برنامه
APP_NAME = 'NexSocial'
API_VERSION = '1.0.0'



DEFAULT_FROM_EMAIL = 'your@email.com'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your@email.com'
EMAIL_HOST_PASSWORD = 'your-password'

