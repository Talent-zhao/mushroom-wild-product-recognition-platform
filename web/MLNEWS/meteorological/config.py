"""
配置文件
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据库
database_type = 'mysql'  # sqlite 或者 mysql
# 如果选择 mysql 数据库，配置如下
database_name = 'mlnews'  # 数据库名字
database_user = 'root'  # 用户名
database_password = '123456'  # 数据库密码
database_port = 3396  # 端口
#####################    全局设置    #####################

GLOBAL_SETTING = {
    'global_title': '山货交易',  # 课题名字
    'global_font_color': '#15c377',  # 全局字体颜色
    'global_bg_color': '#e74c3c',  # 全局背景颜色
    'echartsTheme': 'macarons',  # echarts主题

    'nav_bg_color': '#7d5fff',  # 菜单栏背景颜色

}

if database_type == 'sqlite':
    # sqlite数据库
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db', 'db.sqlite3'),
        }
    }
else:
    # mysql 数据库（若连接失败则自动回退到 SQLite，保证项目能先跑起来）
    _mysql_ok = False
    try:
        import pymysql
        c = pymysql.connect(
            host='127.0.0.1', port=database_port, user=database_user,
            password=database_password, connect_timeout=2
        )
        c.close()
        _mysql_ok = True
    except Exception as e:
        print(f"MySQL 未连接（{e}），已自动改用 SQLite。要使用 MySQL 请先启动 MySQL 并检查 config.py 中端口、密码。")

    if _mysql_ok:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': database_name,
                'USER': database_user,
                'PASSWORD': database_password,
                'HOST': '127.0.0.1',
                'PORT': str(database_port),
                'OPTIONS': {'charset': 'utf8mb4'},
            }
        }
        try:
            from utils.connect_mysql import ConnectMysql
            con = ConnectMysql(passwd=database_password, port=database_port)
            if database_name not in con.get_all_db():
                con.create_db(database_name, 'utf8mb4', 'utf8mb4_general_ci')
                print(f"已自动创建 MySQL 数据库: {database_name}")
        except Exception as e:
            print(f"MySQL 建库检查: {e}")
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            }
        }
