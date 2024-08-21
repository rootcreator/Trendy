import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-)$$&@2#p--dw%tei2h3_5#_)6*tp)9t4y63tbff_mh3wr0$-r$'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'chicken-aware-nicely.ngrok-free.app', 'https://chicken-aware-nicely.ngrok-free.app/']

CSRF_TRUSTED_ORIGINS = [
    'https://chicken-aware-nicely.ngrok-free.app',
    # Add any other trusted origins if necessary
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'app',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'trends.urls'

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

WSGI_APPLICATION = 'trends.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_REDIRECT_URL = '/profile/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

YOUTUBE_API_KEY = 'AIzaSyAf63RX80yCepWkqTCbOJqH9NwU3n_ttpg'
SPOTIFY_CLIENT_ID = 'c8d2f5f66d3c4315a60db04d36564d8f'
SPOTIFY_CLIENT_SECRET = 'ba4372fb586b44639a58e269adacc9bf'
NEWS_API_KEY = 'b16b069ac1554fdaba3edbe8c632d002'
RAPIDAPI_KEY = '1ecad14232mshea32a62c1e4dc2ap181062jsn38bf6995676a'


TWITTER_API_KEY = '1ecad14232mshea32a62c1e4dc2ap181062jsn38bf6995676a'

TMDB_API_KEY = 'a818eb1454383bdcb39576af4e8f54ab'

ALPHA_VANTAGE_API_KEY = '9F2ZXE5KLGDWTG7C'
COINMARKETCAP_API_KEY = '5bda27c4-51e9-413e-b07d-ec6a1bac07bc'
