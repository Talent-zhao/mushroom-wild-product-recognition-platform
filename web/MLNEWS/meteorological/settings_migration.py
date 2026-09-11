"""
数据迁移专用配置：同时配置 SQLite（源）和 MySQL（目标），用于 dumpdata/loaddata
迁移时 default 固定为 MySQL（按 config 中 mysql 配置），不采用 SQLite 回退
"""
import os
from .settings import *
from meteorological import config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SQLite 可能位置（按优先级尝试）
for p in [os.path.join(BASE_DIR, 'db.sqlite3'), os.path.join(BASE_DIR, 'db', 'db.sqlite3')]:
    if os.path.isfile(p):
        sqlite_path = p
        break
else:
    sqlite_path = os.path.join(BASE_DIR, 'db.sqlite3')

# 双数据库：default=MySQL（目标），sqlite_backup=SQLite（源）
# 迁移时 default 始终用 MySQL 配置，避免 config 因连接失败回退到 SQLite
if getattr(config, 'database_type', 'sqlite') == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config.database_name,
            'USER': config.database_user,
            'PASSWORD': config.database_password,
            'HOST': '127.0.0.1',
            'PORT': str(config.database_port),
            'OPTIONS': {'charset': 'utf8mb4'},
        },
        'sqlite_backup': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': sqlite_path,
        },
    }
else:
    DATABASES = {
        'default': config.DATABASES['default'],
        'sqlite_backup': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': sqlite_path,
        },
    }
