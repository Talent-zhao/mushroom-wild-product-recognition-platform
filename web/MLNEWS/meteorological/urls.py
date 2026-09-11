"""meteorological URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from app import views
from meteorological import settings

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('ueditor/', include('DjangoUeditor.urls')),
                  path('', views.index, name='index'),

                  path('login/', views.login, name='login'),
                  path('logout/', views.logout, name='logout'),
                  path('register/', views.register, name='register'),
                  path('profile', views.profileView.as_view(), name='profile'),  # 个人信息修改
                  # ================================================= #
                  # ****************** 蘑菇   *********************** #
                  # ================================================= #
                  path('data2db/', views.data2db, name='data2db'),  # 数据入库
                  path('datasets_list', views.datasets_list, name='datasets_list'),  # 数据集
                  path('upload1', views.upload1.as_view(), name='upload1'),  # 数据上传
                  path('predictHistory/', views.predictHistory.as_view(), name='predictHistory'),  # 识别记录

                  # ================================================= #
                  # ******************   山火   ********************* #
                  # ================================================= #
                  path('data2db1/', views.data2db1, name='data2db1'),  # 数据入库
                  path('goods_add', views.goods_add.as_view(), name='goods_add'),  # 添加
                  path('upload2', views.upload2.as_view(), name='upload2'),  # 数据上传
                  path('yuyue/', views.yuyueView.as_view(), name='yuyue'),
                  path('detail/', views.detail, name='detail'),
                  path('commentAjax', views.commentAjax, name='commentAjax'),  # 评论
                  path('pay/', views.pay, name='pay'),
                  path('myorder/', views.myorder, name='myorder'),

                  # ================================================= #
                  # ******************  文章   ********************** #
                  # ================================================= #
                  path('blog_list', views.blog_list.as_view(), name='blog_list'),  # 列表
                  path('blog_add', views.blog_add.as_view(), name='blog_add'),  # 添加
                  path('blog_detail', views.blog_detail.as_view(), name='blog_detail'),  # 详情
                  path('commentAjaxblog', views.commentAjaxblog, name='commentAjaxblog'),  # 评论

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
