"""
Django settings module selector.
根据环境变量选择配置
"""

import os
from pathlib import Path

import pymysql

pymysql.install_as_MySQLdb()

# 加载 .env 文件到环境变量
_base = Path(__file__).resolve().parent.parent.parent
_env_path = _base / '.env'
if _env_path.exists():
    with open(_env_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value

environment = os.environ.get('DJANGO_ENV', 'development')

if environment == 'production':
    from .production import *
else:
    from .development import *
