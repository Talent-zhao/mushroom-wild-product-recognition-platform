# coding=utf-8
"""
    @product  :   PyCharm
    @Author   :   xeon
    @date     :   2022/9/11 02:14
    @fileName :   init.py
    @功能      : 初始化
"""
from faker import Faker

faker = Faker("zh-CN")
from django.core.management.base import BaseCommand
from app.models import *
def create_faker_info():

    User.objects.all().delete()
    User.objects.create(name='user',password='123456',tel='user')
    for i in range(5):
        # 生成指定时间的日期
        date = faker.date_between('-100day','today')
        simple_profile = faker.simple_profile()
        """
        {'username': 'songguiying',
         'name': '申凯',
         'sex': 'F',
         'address': '江苏省惠州县沈河官路f座 807064',
         'mail': 'yonggong@yahoo.com',
         'birthdate': datetime.date(1980, 6, 3)}
        """
        username = simple_profile['name']
        tel  = faker.phone_number()
        password = 'CHANGE_ME'
        User.objects.create(name=username,tel=tel,password=password)

    # 类别
    tmp = '北京 天津 河北 辽宁 吉林 黑龙江 山东 江苏 上海 浙江 安徽 福建 江西 广东 广西 海南 河南 湖南 湖北 山西 内蒙古 宁夏 青海 陕西 甘肃 新疆 四川 贵州 云南 重庆 西藏 香港 澳门 台湾'
    for item in tmp.split():
        Kind.objects.create(name=item)
def init_(request):
    print('初始化数据OK')
    pass
class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        create_faker_info()
        self.stdout.write(self.style.SUCCESS('Successfully !'))
        pass
        # try:
        #     poll = Poll.objects.get(pk=poll_id)
        # except Poll.DoesNotExist:
        #     raise CommandError('Poll "%s" does not exist' % poll_id)
        # self.stdout.write(self.style.SUCCESS('Successfully closed poll!'))