# ================================================= #
# ****************** 该功能是为了删除sqlite数据的，不会不要执行   ******************* #
# ================================================= #
import  os
# os.remove( os.path.join("db","db.sqlite3") )
os.system("python manage.py makemigrations")
os.system("python manage.py migrate")


