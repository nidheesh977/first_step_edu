import environ
import os
from pathlib import Path
env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


SECRET_KEY = 'django-insecure-w%_4y(!zj-a@6_6$ydd4y7uwqxove%fv0395-alm390g+#tmbi'
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    "phonenumber_field",
    'django_summernote', 

    "admin_dashboard.apps.AdminDashboardConfig",
    "application.apps.ApplicationConfig",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'first_edu.urls'

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
                'first_edu.context_processors.marquee_context_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'first_edu.wsgi.application'

DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.postgresql',
       'NAME': "firststepedu",
       'USER': 'postgres',
       'PASSWORD': 'root',
       'PORT': '5432',
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

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True



STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'staticfiles/'),
]
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static/")


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

AUTH_USER_MODEL = 'application.CustomUser'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.office365.com'
EMAIL_HOST_USER = "Info@firstedu.co.in"
EMAIL_HOST_PASSWORD = "Firstedu@123"
EMAIL_PORT = 587

PHONENUMBER_DB_FORMAT = "NATIONAL"
PHONENUMBER_DEFAULT_FORMAT = "NATIONAL"
PHONENUMBER_DEFAULT_REGION = "IN"

LOGIN_URL = 'application:signin'


# FIXME -> RAZORPAY KEY
RAZORPAY_KEY_ID = "rzp_test_N43gLBtLP7Ny7U"
RAZORPAY_KEY_SECRET = "QYlFBbzaCKEg9Ok4KQtvRgGV"


CSRF_TRUSTED_ORIGINS = [
    'https://api.razorpay.com',
]