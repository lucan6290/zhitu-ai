"""
Django base settings for agent_face_pro project.
基础配置文件 - 包含所有环境共用的配置
纯API后端 - 前后端分离架构
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-4eg4r8rmhvx_tb*)2ipurcbr%ylly+)r8ti=c(ztowhp$^6cy9')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'corsheaders',
    'apps.face',
    'apps.chat',
    'apps.mcp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_CREDENTIALS = True

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

FACE_IMAGES_DIR = MEDIA_ROOT / 'face_images'

DATABASE_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', '123456'),
    'name': os.environ.get('DB_NAME', 'agent_face_sql'),
    'charset': 'utf8',
}

LLM_CONFIG = {
    'api_key': os.environ.get('QWEN_API_KEY', ''),
    'base_url': os.environ.get('QWEN_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1'),
    'model': os.environ.get('QWEN_MODEL', 'qwen3-max-2026-01-23'),
}

INVITATION_CODE = os.environ.get('INVITATION_CODE', '')

MCP_CONFIG = {
    'command': os.environ.get('MCP_COMMAND', 'npx'),
    'args': os.environ.get('MCP_ARGS', '-y,@zizaiwork/mcp').split(','),
    'api_key': os.environ.get('ZAI_API_KEY', ''),
}
