import os
from dotenv import load_dotenv
load_dotenv()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = bool(int(os.getenv('DEBUG', 0)))
ALLOWED_HOSTS = ['localhost']


INSTALLED_APPS = [
    "django_dramatiq",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tumblr_auth',
    'tumblr_posts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'backend.wsgi.application'

if DEBUG and not os.getenv('USE_POSTGRES'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB'),
            'USER': os.getenv('POSTGRES_USER'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
            'HOST': os.getenv('POSTGRES_HOST'),
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
USE_L10N = True
USE_TZ = True

SESSION_COOKIE_HTTPONLY = False  # Needed for accessing cookies from front end

TUMBLR_CONSUMER_KEY = os.getenv('TUMBLR_CONSUMER_KEY')
TUMBLR_CONSUMER_SECRET = os.getenv('TUMBLR_CONSUMER_SECRET')
TUMBLR_REQUEST_TOKEN_URL = 'https://www.tumblr.com/oauth/request_token'
TUMBLR_AUTHORIZATION_URL = 'https://www.tumblr.com/oauth/authorize'
TUMBLR_ACCESS_TOKEN_URL = 'https://www.tumblr.com/oauth/access_token'
MIN_POSTS_UPDATE_INTERVAL = 60 * 60 if not DEBUG else 10

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

REDIS = {
    'host': os.getenv('REDIS_HOST'),
    'port': os.getenv('REDIS_PORT'),
    'db': os.getenv('REDIS_DB'),
}

DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.redis.RedisBroker",
    "OPTIONS": REDIS,
}

DRAMATIQ_RESULT_BACKEND = {
    "BACKEND": "dramatiq.results.backends.redis.RedisBackend",
    "BACKEND_OPTIONS": REDIS,
    "MIDDLEWARE_OPTIONS": {
        "result_ttl": 60000
    }
}