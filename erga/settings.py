"""
Django settings for the CBP/ERGA GTC project.
Deployment-specific values are read from erga/.env — see .env.template for the full list.
"""

import os
from decouple import config

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)   # project root (contains manage.py)

# ── Deployment-specific (set in erga/.env) ─────────────────────────────────────
URL_PREFIX                 = config('URL_PREFIX',                 default='/cbp-dev')
DB_NAME                    = config('DB_NAME',                    default='cbp_dev')
LOG_FILE                   = config('LOG_FILE',                   default='/home/talioto/logs/ear-review-dev.log')
EAR_STUCK_THRESHOLD_DAYS   = config('EAR_STUCK_THRESHOLD_DAYS',   default=7, cast=int)
ENABLE_CRONS               = config('ENABLE_CRONS',               default=False, cast=bool)
ACCOUNT_EMAIL_VERIFICATION = config('ACCOUNT_EMAIL_VERIFICATION', default='mandatory')
ACCOUNT_EMAIL_REQUIRED     = config('ACCOUNT_EMAIL_REQUIRED',     default=True, cast=bool)

# ──────────────────────────────────────────────────────────────────────────────

# Derived from URL_PREFIX
MEDIA_URL   = URL_PREFIX + '/media/'
STATIC_URL  = config('STATIC_URL', default=URL_PREFIX + '/static/')
LOGIN_URL   = URL_PREFIX + '/accounts/login/'
LOGIN_REDIRECT_URL                            = URL_PREFIX + '/dashboard/'
ACCOUNT_LOGOUT_REDIRECT_URL                   = URL_PREFIX + '/'
DEFAULT_DOMAIN                                = 'https://genomes.cnag.cat' + URL_PREFIX + '/'
EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = URL_PREFIX + '/edit_profile/'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = (
    URL_PREFIX + '/accounts/login/?next=' + URL_PREFIX + '/edit_profile/'
)
CKEDITOR_UPLOAD_PATH = MEDIA_URL

# Derived from PROJECT_DIR
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'deployment', 'data')

# Secrets
SECRET_KEY          = config('SECRET_KEY')
DB_PASSWORD         = config('DB_PASSWORD')
EMAIL_HOST_USER     = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL  = config('DEFAULT_FROM_EMAIL')
GITHUB_TOKEN        = config('GITHUB_TOKEN')

DEBUG = False

ALLOWED_HOSTS = [
    'resistome.cnag.cat', 'resistome.cnag.es', 'resistome.cnag.eu',
    'genomes.cnag.cat', 'genomes.cnag.es', 'genomes.cnag.eu',
    'localhost', '10.73.4.1',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_extensions',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dal',
    'dal_select2',
    'erga',
    'django_registration',
    'status',
    'rest_framework',
    'django_filters',
    'django_tables2',
    'django_tables2_column_shifter',
    'bootstrap3',
    'bootstrap4',
    'cookielaw',
    'crispy_forms',
    'qurl_templatetag',
    'multiselectfield',
    'modelclone',
    'django_addanother',
    'django_popup_view_field',
    'tagging',
    'debug_toolbar',
    'django_cron',
    'django_ckeditor_5',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF      = 'erga.urls'
WSGI_APPLICATION  = 'erga.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'erga', 'templates'),
            os.path.join(PROJECT_DIR, 'status', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'status.context_processors.customization',
                'status.context_processors.dashboard_action_count',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_NAME,
        'USER': 'cbp_admin',
        'PASSWORD': DB_PASSWORD,
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
    'OPTIONS': {
        'init_command': 'SET foreign_key_checks = 0;',
    },
}

CRON_CLASSES = [
    'status.views.SpeciesSaveCronJob',
    'status.views.UpdateSamplesCronJob',
    'status.views.FetchEARsCronJob',
] if ENABLE_CRONS else []

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Europe/Madrid'
USE_I18N  = True
USE_L10N  = True
USE_TZ    = True
USE_THOUSAND_SEPARATOR = True

DATE_INPUT_FORMATS = [
    '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y',
    '%Y-%m',
    '%b %d %Y', '%b %d, %Y',
    '%d %b %Y', '%d %b, %Y',
    '%B %d %Y', '%B %d, %Y',
    '%d %B %Y', '%d %B, %Y',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_ROOT = '/home/www/resistome.cnag.cat/incredible/deployment/static'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

CRISPY_TEMPLATE_PACK = 'bootstrap4'
SITE_ID = 1
ACCOUNT_ACTIVATION_DAYS            = 7
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7
ACCOUNT_AUTHENTICATION_METHOD      = 'username_email'
ACCOUNT_UNIQUE_EMAIL               = True
ACCOUNT_USERNAME_REQUIRED          = False
ACCOUNT_DEFAULT_HTTP_PROTOCOL      = 'https'
ACCOUNT_FORMS = {'signup': 'status.forms.CustomSignupForm'}

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST    = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT    = 587

NOTIFICATIONS = True

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 99999999999,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissions',
    ],
}

DATA_UPLOAD_MAX_MEMORY_SIZE    = 500 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE    = 1 * 1024 * 1024
DATA_UPLOAD_MAX_NUMBER_FIELDS  = 10000

PILL_PALETTE     = 'original'
CMS_COLOR_SCHEME = 'light'

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'underline', 'strikethrough', '|',
            'link', 'bulletedList', 'numberedList', '|',
            'blockQuote', 'insertTable', '|',
            'undo', 'redo',
        ],
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {'format': '{levelname} {message}', 'style': '{'},
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_FILE,
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {'handlers': ['file'], 'level': 'WARNING', 'propagate': True},
        'status': {'handlers': ['file'], 'level': 'DEBUG',   'propagate': False},
        'erga':   {'handlers': ['file'], 'level': 'DEBUG',   'propagate': False},
    },
}
