"""
Django settings for supervisor project.

Generated by 'django-admin startproject' using Django 4.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'background_tasks': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# GET SECRETS PATH
SECRETS_PATH = os.environ.get('SECRETS_PATH', '/run/secrets')


def _read_secret(secret_path: str, key: str, default=None):
    # Check environment variables
    value = os.getenv(key, None)
    if value is not None:
        return value
    # Check file environment variable
    file_path = os.getenv('{}_FILE'.format(key.upper()), None)
    if file_path is None:
        file_path = os.path.join(secret_path, key.upper())
    if file_path is not None and os.path.exists(file_path):
        with open(file_path, 'r') as secret:
            value = secret.read()
    if value is None:
        value = default
    return value

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = os.getenv('DEBUG', False) in [1, "1", True, "True", "true"]

# Setup data directory
DATA_DIRECTORY = Path(os.environ.get('SUPERVISOR_DATA', os.path.join(BASE_DIR, '_data', ''))).resolve()
os.makedirs(DATA_DIRECTORY, exist_ok=True)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'django_apscheduler',
    'rest_framework',
    'rest_framework_simplejwt',
    'tesla_ce_supervisor',
    # Prometheus metrics exporter
    'django_prometheus',
#    'apps.web',
#    'apps.api'
]

# AUTO, None, SETUP, CONFIG (in service mode, force update all variables and exit())
SETUP_MODE = os.environ.get('SETUP_MODE', None)
if SETUP_MODE is not None:
    SETUP_MODE = SETUP_MODE.upper()

SUPERVISOR_MODULES = []
CONFIGURATION_SOURCE = 'database'

if SETUP_MODE == 'BUILD':
    # Used for Docker image build. Only for migrations!
    SUPERVISOR_ADMIN_USER = None
    SUPERVISOR_ADMIN_PASSWORD = None
    SUPERVISOR_ADMIN_EMAIL = None
    SECRET_KEY = get_random_secret_key()
    TESLA_DOMAIN = None
    ALLOWED_HOSTS = []  # No access allowed
    INSTALLED_APPS += [
        'tesla_ce_supervisor.apps.web',
        'tesla_ce_supervisor.apps.api',
    ]
    SUPERVISOR_MODULES = ['web', 'api']
    CONFIGURATION_SOURCE = 'file'

elif SETUP_MODE == 'SETUP':
    SUPERVISOR_ADMIN_USER = None
    SUPERVISOR_ADMIN_PASSWORD = None
    SUPERVISOR_ADMIN_EMAIL = None
    SECRET_KEY = get_random_secret_key()
    TESLA_DOMAIN = None
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
    INSTALLED_APPS += [
        'tesla_ce_supervisor.apps.web',
    ]
    SUPERVISOR_MODULES = ['web']
    CONFIGURATION_SOURCE = 'file'

elif SETUP_MODE == 'DEV':
    # todo: remove this SETUP_MODE='DEV'
    SUPERVISOR_ADMIN_USER = _read_secret(SECRETS_PATH, 'SUPERVISOR_ADMIN_USER')
    SUPERVISOR_ADMIN_PASSWORD = _read_secret(SECRETS_PATH, 'SUPERVISOR_ADMIN_PASSWORD')
    SUPERVISOR_ADMIN_EMAIL = _read_secret(SECRETS_PATH, 'SUPERVISOR_ADMIN_EMAIL')
    SECRET_KEY = get_random_secret_key()
    TESLA_DOMAIN = None
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
    INSTALLED_APPS += [
        'tesla_ce_supervisor.apps.api',
        'tesla_ce_supervisor.apps.web',
    ]
    SUPERVISOR_MODULES = ['web', 'api']
    CONFIGURATION_SOURCE = 'file'

else:
    SUPERVISOR_ADMIN_USER = _read_secret(SECRETS_PATH, 'SUPERVISOR_ADMIN_USER')
    SUPERVISOR_ADMIN_PASSWORD = _read_secret(SECRETS_PATH, 'SUPERVISOR_ADMIN_PASSWORD')
    SUPERVISOR_ADMIN_EMAIL = _read_secret(SECRETS_PATH, 'SUPERVISOR_ADMIN_EMAIL')
    SECRET_KEY = _read_secret(SECRETS_PATH, 'SUPERVISOR_SECRET')
    TESLA_DOMAIN = _read_secret(SECRETS_PATH, 'TESLA_DOMAIN')
    ALLOWED_HOSTS = [TESLA_DOMAIN, '*']
    INSTALLED_APPS += [
        'tesla_ce_supervisor.apps.api',
    ]
    SUPERVISOR_MODULES = ['api']


MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'tesla_ce_supervisor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(os.path.dirname(__file__), 'apps', 'web', 'templates'),
            os.path.join(os.path.dirname(__file__), 'lib', 'deploy', 'templates'),
            os.path.join(os.path.dirname(__file__), 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
               'web_filters': 'tesla_ce_supervisor.apps.web.templatetags.filter',
            }
        },
    },
]

WSGI_APPLICATION = 'tesla_ce_supervisor.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

if SETUP_MODE == 'DEV' or SETUP_MODE == 'SETUP':
    DATABASES = {
        'default': {
            'ENGINE': 'django_prometheus.db.backends.sqlite3',
            'NAME': DATA_DIRECTORY / 'supervisor.sqlite3',
            'ATOMIC_REQUESTS': True
        }
    }

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django_prometheus.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB', 'supervisor'),
            'USER': os.getenv('POSTGRES_USER', 'supervisor'),
            'HOST': os.getenv('POSTGRES_HOST', '127.0.0.1'),
            'PORT': os.getenv('POSTGRES_PORT', '5432'),
            'PASSWORD': _read_secret(os.path.join(os.environ.get('SUPERVISOR_DATA', '/data'), 'secrets'), 'DB_ROOT_PASSWORD'),
        }
    }



# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'tesla_ce_supervisor.apps.api.auth.SupervisorJWTAuthentication',
        #'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_URL = 'supervisor/static/'
STATIC_ROOT = os.getenv('STATICS_PATH', '')


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# supervisor service secrets:
# vault token
# vault keys[optional]  [ only privileged mode ]
# django secret
# admin password
# tesla.config.cfg [ only privileged mode ]

'''
For testing expired tokens
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(seconds=1),
}
'''