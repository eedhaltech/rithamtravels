"""
Django settings for ritham_tours project.
"""

from pathlib import Path
from datetime import timedelta
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)
# DEBUG = config('DEBUG', default=True, cast=bool)

# ALLOWED_HOSTS = ['*']

ALLOWED_HOSTS = [
    "rithamtravels.in",
    "www.rithamtravels.in",
    ".onrender.com",
]



# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'phonenumber_field',
    'accounts',
    'vehicles',
    'bookings',
    'tours',
    'blog',
    'enquiries',
    'seo',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ritham_tours.urls'

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
                'seo.context_processors.seo_context',
                'accounts.context_processors.system_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'ritham_tours.wsgi.application'

# Database


# server database

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'ritham_tours',
#         'USER': 'dbadmin',
#         'PASSWORD': 'DbAdmin@123',
#         'HOST': 'localhost',
#         'PORT': '3306',
#         'OPTIONS': {
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#         },
#     }
# }

CSRF_TRUSTED_ORIGINS = [
    "https://rithamtravels.in",
    "https://www.rithamtravels.in",
    "https://*.onrender.com",
]


# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# local development database (SQLite) 

from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
    }
}


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'ritham_tours',
#         'USER': 'root',
#         'PASSWORD': '',
#         'HOST':'localhost',
#         'PORT':'3306',
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': config('DB_NAME', default='ritham_tours'),
#         'USER': config('DB_USER', default='postgres'),
#         'PASSWORD': config('DB_PASSWORD', default='postgres'),
#         'HOST': config('DB_HOST', default='localhost'),
#         'PORT': config('DB_PORT', default='5432'),

#     }
# }

# Alternative MySQL configuration (uncomment if using MySQL)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': config('DB_NAME', default='ritham_tours'),
#         'USER': config('DB_USER', default='root'),
#         'PASSWORD': config('DB_PASSWORD', default=''),
#         'HOST': config('DB_HOST', default='localhost'),
#         'PORT': config('DB_PORT', default='3306'),
#     }
# }

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
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

# Static files finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    # Local dev
    "http://localhost:8000",
    "http://127.0.0.1:8000",

    # Production
    "https://rithamtravels.in",
    "https://www.rithamtravels.in",
    "https://rithamtravels.onrender.com",
]




CORS_ALLOW_ALL_ORIGINS = DEBUG

# Razorpay Configuration
RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID', default='')
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET', default='')

# WhatsApp Cloud API Configuration
# WHATSAPP_ACCESS_TOKEN = config('WHATSAPP_ACCESS_TOKEN', default='')
# WHATSAPP_PHONE_NUMBER_ID = config('WHATSAPP_PHONE_NUMBER_ID', default='')
# WHATSAPP_BUSINESS_ACCOUNT_ID = config('WHATSAPP_BUSINESS_ACCOUNT_ID', default='')
# WHATSAPP_VERIFY_TOKEN = config('WHATSAPP_VERIFY_TOKEN', default='ritham_webhook_verify_2024')

# Email Configuration - Google App Password
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'rithamtravels@gmail.com'
EMAIL_HOST_PASSWORD = 'ijpb wwdc tdhc hdny'
DEFAULT_FROM_EMAIL = 'Ritham Travels <rithamtravels@gmail.com>'
SERVER_EMAIL = 'rithamtravels@gmail.com'

# Company Email Configuration
COMPANY_EMAIL = 'rithamtravels@gmail.com'
CONTACT_EMAIL = 'rithamtravels@gmail.com'

# WhatsApp Configuration (using Twilio or similar)
# WHATSAPP_API_KEY = config('WHATSAPP_API_KEY', default='')
# WHATSAPP_API_SECRET = config('WHATSAPP_API_SECRET', default='')
# WHATSAPP_PHONE_NUMBER = config('WHATSAPP_PHONE_NUMBER', default='+919787110763')

# Google API Configuration
GOOGLE_PLACES_API_KEY = config('GOOGLE_PLACES_API_KEY', default='')
GOOGLE_PLACE_ID = config('GOOGLE_PLACE_ID', default='')

# Company Details
COMPANY_NAME = 'Ritham Tours & Travels'
COMPANY_PHONE = '+91 97871 10763'
COMPANY_EMAIL = 'rithamtravels@gmail.com'
COMPANY_ADDRESS = 'Coimbatore, Tamil Nadu, India'

# SEO Configuration
SITE_DOMAIN = 'https://rithamtravels.in'
SITE_URL = 'https://rithamtravels.in'  # Centralized site URL for SEO
GOOGLE_ANALYTICS_ID = config('GOOGLE_ANALYTICS_ID', default='')
GOOGLE_SITE_VERIFICATION = config('GOOGLE_SITE_VERIFICATION', default='')
FACEBOOK_APP_ID = config('FACEBOOK_APP_ID', default='')

# Ensure logs directory exists
import os
LOGS_DIR = BASE_DIR / 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'django.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'whatsapp_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'whatsapp.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'email_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'email.log',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'bookings.services.whatsapp_service': {
            'handlers': ['whatsapp_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'bookings.services.email_service': {
            'handlers': ['email_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'bookings.services.notification_service': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'bookings.signals': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

