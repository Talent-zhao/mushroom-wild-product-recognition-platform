import uuid

from django.db import models
from DjangoUeditor.models import UEditorField
class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128,verbose_name='姓名')
    tel = models.CharField(max_length=128,verbose_name='手机')
    password = models.CharField(max_length=128,verbose_name='密码')

    class Meta:
        verbose_name_plural = '用户管理'  # 此时，admin中表的名字就是‘用户表‘

    def __str__(self):
        return self.name

class Datasets(models.Model):
    id = models.AutoField(primary_key=True)
    ch = (
        ('无毒蘑菇','无毒蘑菇'),
        ('有毒蘑菇','有毒蘑菇'),
    )
    name = models.CharField(max_length=128,verbose_name='类别',choices=ch)
    img = models.ImageField(verbose_name='图片',null=True,upload_to='img/')

    class Meta:
        verbose_name_plural = '毒蘑菇数据集管理'  # 此时，admin中表的名字就是verbose_name_plural


class PredictHistory(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,verbose_name='用户',on_delete=models.CASCADE)
    kind = models.CharField(max_length=128,verbose_name="类别")
    img = models.ImageField(verbose_name='图片',null=True,upload_to='img/')
    time = models.DateTimeField(auto_now_add=True, verbose_name='时间')
    class Meta:
        verbose_name = '蘑菇识别管理'
        verbose_name_plural = verbose_name  #
        ordering = ['-time']  # 排序



class Kind(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128,verbose_name='名字')
    img = models.ImageField(verbose_name='图片', null=True, upload_to='img/')
    class Meta:
        verbose_name_plural = '山货类别管理'  # 此时，admin中表的名字就是‘用户表‘

    def __str__(self):
        return self.name


class Datasets1(models.Model):
    id = models.AutoField(primary_key=True)
    kind = models.ForeignKey(Kind,on_delete=models.CASCADE,verbose_name="类别")
    img = models.ImageField(verbose_name='图片',null=True,upload_to='img/')

    class Meta:
        verbose_name_plural = '山货数据集管理'  # 此时，admin中表的名字就是verbose_name_plural




class PredictHistory1(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,verbose_name='用户',on_delete=models.CASCADE)
    kind = models.ForeignKey(Kind, on_delete=models.CASCADE, verbose_name="类别")
    img = models.CharField(max_length=128, verbose_name="图片")
    time = models.DateTimeField(auto_now_add=True, verbose_name='时间')
    class Meta:
        verbose_name = '山货识别管理'
        verbose_name_plural = verbose_name  #
        ordering = ['-time']




class Goods(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE)
    title = models.CharField(max_length=128,verbose_name='标题')
    date = models.DateField(verbose_name='日期',auto_now_add=True)
    img = models.ImageField(upload_to='news/img/', verbose_name='图像')
    kind = models.ForeignKey(Kind, models.CASCADE, verbose_name='类别')
    content = UEditorField(u'内容',
                 default='',
                 width=1000,
                 height=300,
                 imagePath='news/images/',
                 filePath='news/files/')
    price = models.IntegerField(verbose_name='价格',default=100)

    class Meta:
        verbose_name_plural = '商品管理'  # 此时，admin中表的名字就是‘用户表‘

    def __str__(self):
        return self.title



class Order(models.Model):
    id = models.AutoField(primary_key=True)
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name='商品', default=1)
    user = models.ForeignKey(User,on_delete=models.CASCADE,verbose_name='用户')
    num = models.IntegerField(verbose_name='数量',default=1)
    today = models.DateField(verbose_name='下单日期',auto_now_add=True)
    uuid = models.CharField(max_length=64,verbose_name='订单号',default=uuid.uuid4())
    def total(self):
        return  self.num * self.goods.price

    class Meta:
        verbose_name = '订单管理'  # 定义在管理后台显示的名称
        verbose_name_plural = verbose_name  # 定义复数时的名称（去除复数的s）
        ordering = ['id']  # 排序



class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    item = models.ForeignKey(Goods,verbose_name='item',on_delete=models.CASCADE)
    user = models.ForeignKey(User,verbose_name='用户',on_delete=models.CASCADE)
    content = models.CharField(max_length=1024,verbose_name='评论内容')
    date = models.DateField(auto_now_add=True,verbose_name='评论时间')
    # 情感分析字段
    sentiment = models.CharField(max_length=20, verbose_name='情感倾向', default='neutral', 
                                 choices=[('positive', '正面'), ('negative', '负面'), ('neutral', '中性')])
    sentiment_confidence = models.FloatField(verbose_name='情感置信度', default=0.5)
    sentiment_locked = models.BooleanField(verbose_name='情感已人工确认', default=False)
    class Meta:
        verbose_name = '商品评价管理'  # 定义在管理后台显示的名称
        verbose_name_plural = verbose_name  # 定义复数时的名称（去除复数的s）
        ordering = ['-date']




class Blog(models.Model):
    id = models.AutoField(primary_key=True,verbose_name='id')
    user = models.ForeignKey(User,verbose_name='发布人',on_delete=models.CASCADE)
    kind = models.ForeignKey(Kind, models.CASCADE, verbose_name='类别')
    title = models.CharField(max_length=64,verbose_name='标题')
    tags = models.CharField(max_length=128,verbose_name='标签')
    content = UEditorField(u'内容',
                           default='内容',
                           width=1000,
                           height=400,
                           imagePath='upload/img/',
                           filePath='upload/file/')
    date = models.DateTimeField(auto_now=True,verbose_name="发布时间")
    img = models.ImageField(verbose_name='图片',null=True,upload_to='img/')
    view = models.PositiveIntegerField(verbose_name='浏览量', default=0)
    class Meta:
        verbose_name = '文章管理'  # 定义在管理后台显示的名称
        verbose_name_plural = verbose_name  # 定义复数时的名称（去除复数的s）
    def __str__(self):
        return self.title

class CommentBlog(models.Model):
    id = models.AutoField(primary_key=True)
    item = models.ForeignKey(Blog,verbose_name='文章',on_delete=models.CASCADE)
    user = models.ForeignKey(User,verbose_name='用户',on_delete=models.CASCADE)
    content = models.CharField(max_length=1024,verbose_name='评论内容')
    date = models.DateField(auto_now_add=True,verbose_name='评论时间')
    # 情感分析字段
    sentiment = models.CharField(max_length=20, verbose_name='情感倾向', default='neutral',
                                 choices=[('positive', '正面'), ('negative', '负面'), ('neutral', '中性')])
    sentiment_confidence = models.FloatField(verbose_name='情感置信度', default=0.5)
    sentiment_locked = models.BooleanField(verbose_name='情感已人工确认', default=False)
    class Meta:
        verbose_name = '文章评论管理'  # 定义在管理后台显示的名称
        verbose_name_plural = verbose_name  # 定义复数时的名称（去除复数的s）
        ordering = ['-date']











