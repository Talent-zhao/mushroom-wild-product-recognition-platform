# -*- coding: utf-8 -*-
"""
将 SQLite 中的数据导出，并在 MySQL 中建表、导入数据。

步骤：
  1. 从 SQLite 导出全部数据到 data_backup.json
  2. 在 MySQL 中执行 migrate，创建与项目模型一致的表结构
  3. 将 data_backup.json 导入 MySQL（default 库）

用法：python 迁移SQLite到MySQL.py
前提：MySQL 已启动，且 meteorological/config.py 中 database_type='mysql'、端口/密码正确
"""
import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meteorological.settings_migration')

BACKUP_FILE = os.path.join(BASE_DIR, 'data_backup.json')

def run(cmd, desc):
    print(f"\n>>> {desc}")
    print(f"    执行: {cmd}")
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'meteorological.settings_migration'
    env['PYTHONUTF8'] = '1'  # 强制 UTF-8，避免 Windows 下 dumpdata/loaddata 用 GBK 导致 UnicodeDecodeError
    ret = subprocess.call(cmd, shell=True, env=env)
    if ret != 0:
        print(f"    失败，退出码: {ret}")
        sys.exit(ret)
    print("    完成")

def main():
    os.chdir(BASE_DIR)
    print("=" * 60)
    print("  SQLite 导出 → MySQL 建表并导入")
    print("=" * 60)

    # 检查 SQLite 文件
    sqlite_path = None
    for p in [os.path.join(BASE_DIR, 'db.sqlite3'), os.path.join(BASE_DIR, 'db', 'db.sqlite3')]:
        if os.path.isfile(p):
            sqlite_path = p
            print(f"  源 SQLite: {sqlite_path}")
            break
    if not sqlite_path:
        print("  未找到 db.sqlite3，请确认路径")
        sys.exit(1)

    # 0. 预检查：MySQL 是否可用（可选，避免做到一半才报错）
    try:
        from meteorological import config
        if getattr(config, 'database_type', '') == 'mysql':
            import pymysql
            c = pymysql.connect(
                host='127.0.0.1', port=config.database_port, user=config.database_user,
                password=config.database_password, connect_timeout=3
            )
            c.close()
            print(f"  目标 MySQL: 127.0.0.1:{config.database_port} / {config.database_name}")
    except Exception as e:
        print(f"  MySQL 连接失败: {e}")
        print("  请先启动 MySQL，并检查 config.py 中 database_port、database_password")
        sys.exit(1)

    # 1. 从 SQLite 导出数据
    run(
        f'python manage.py dumpdata --database=sqlite_backup --natural-foreign --natural-primary -o "{BACKUP_FILE}"',
        "步骤 1/3: 从 SQLite 导出数据到 data_backup.json"
    )

    # 2. 在 MySQL 中建表（migrate 会按模型创建/更新表结构）
    run(
        'python manage.py migrate',
        "步骤 2/3: 在 MySQL 中创建表结构（migrate）"
    )

    # 3. 将数据导入 MySQL
    run(
        f'python manage.py loaddata "{BACKUP_FILE}"',
        "步骤 3/3: 将 data_backup.json 导入 MySQL"
    )

    print("\n" + "=" * 60)
    print("  迁移完成。数据文件: data_backup.json（可保留作备份）")
    print("=" * 60)

if __name__ == '__main__':
    main()
