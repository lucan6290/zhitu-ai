"""
Django development settings.
开发环境配置
"""

from .base import *
import os

DEBUG = True

ALLOWED_HOSTS = ['*']

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DATABASE_CONFIG['name'],
        'USER': DATABASE_CONFIG['user'],
        'PASSWORD': DATABASE_CONFIG['password'],
        'HOST': DATABASE_CONFIG['host'],
        'PORT': DATABASE_CONFIG['port'],
        'CHARSET': DATABASE_CONFIG['charset'],
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
