# -*- coding: utf-8 -*-
import json
import os
import re

import joblib
from django.core.files import File
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator
from torchvision.models import densenet121, googlenet
from tqdm import tqdm

from app.models import User, Kind, Goods, Order, Comment, Blog, CommentBlog
from app.models import Datasets, Datasets1, PredictHistory, PredictHistory1

# ==================== 登录验证 ====================

def check_login(func):
    def wrapper(request):
        if not request.COOKIES.get('uid'):
            return redirect('/login/')
        return func(request)
    return wrapper


def get_user_context(request):
    """从 cookie 获取当前用户信息，返回 (uid, username)。未登录 uid=-1, username=''"""
    uid = int(request.COOKIES.get('uid', -1))
    username = ''
    if uid != -1:
        try:
            username = User.objects.filter(id=uid).values_list('name', flat=True).first() or ''
        except Exception:
            uid = -1
    return uid, username


def create_one_user_admin():
    """初始化管理员与示例用户（仅首次或数据库为空时有效）"""
    try:
        from django.contrib.auth import models as auth_models
        if not auth_models.User.objects.filter(username='admin').exists():
            auth_models.User.objects.create_superuser('admin', 'admin@qq.com', 'admin')
    except Exception:
        pass
    try:
        User.objects.get_or_create(tel='user', defaults={'password': '123456', 'name': 'user'})
        User.objects.get_or_create(tel='user1', defaults={'password': '123456', 'name': 'user1'})
    except Exception:
        pass


create_one_user_admin()

# ==================== 首页 ====================

@check_login
def index(request):
    uid, username = get_user_context(request)
    kind_list = Kind.objects.all()
    kind_param = request.GET.get('kind', 'all')
    if kind_param == 'all':
        newlist = Goods.objects.all()
        kind = 'all'
    else:
        kind = int(kind_param)
        newlist = Goods.objects.filter(kind_id=kind)
    return render(request, 'index.html', locals())

# ==================== 预约 ====================

class yuyueView(View):
    def get(self, request):
        pk = request.GET.get('id')
        if not pk:
            return redirect('/')
        try:
            pk = int(pk)
            info = Goods.objects.get(id=pk)
        except (ValueError, Goods.DoesNotExist):
            return redirect('/')
        uid, username = get_user_context(request)
        if uid != -1 and info.user_id == uid:
            return redirect(f'/detail/?id={pk}&own_goods=1')
        return render(request, 'yuyue.html', locals())

    def post(self, request):
        return JsonResponse({'status': 1, 'msg': '操作成功'})


# ==================== 支付 ====================

def pay(request):
    jid, num = request.GET.get('jid'), request.GET.get('num')
    if not jid or not num:
        return redirect('/')
    try:
        jid, num = int(jid), int(num)
        if num < 1:
            return redirect('/')
        goods = Goods.objects.get(id=jid)
    except (ValueError, Goods.DoesNotExist):
        return redirect('/')
    uid, username = get_user_context(request)
    if uid == -1:
        return redirect('/login/')
    if goods.user_id == uid:
        return redirect(f'/detail/?id={jid}&own_goods=1')
    Order.objects.create(user_id=uid, num=num, goods_id=jid)
    total = num * goods.price
    return render(request, 'alipay.html', locals())



# ==================== 商品详情 ====================

def detail(request):
    id_ = request.GET.get('id')
    if not id_:
        return redirect('/')
    try:
        id_ = int(id_)
        info = Goods.objects.get(id=id_)
    except (ValueError, Goods.DoesNotExist):
        return redirect('/')
    uid, username = get_user_context(request)
    comment_list = Comment.objects.filter(item_id=id_)
    return render(request, 'newDetail.html', locals())



# ==================== 登录 / 注册 / 登出 ====================

def login(request):
    if request.method != 'POST':
        return render(request, 'loginregister.html', {'msg': ''})
    tel, pwd = request.POST.get('tel'), request.POST.get('pwd')
    user = User.objects.filter(tel=tel, password=pwd).first()
    if not user:
        return render(request, 'loginregister.html', {'msg': '用户信息错误，请重新输入！'})
    resp = redirect('/')
    resp.set_cookie('uid', user.id, max_age=60 * 60 * 24)
    return resp


def register(request):
    if request.method != 'POST':
        return render(request, 'loginregister.html', {'msg': ''})
    name, tel, pwd = request.POST.get('name'), request.POST.get('tel'), request.POST.get('pwd')
    if User.objects.filter(tel=tel).exists():
        return render(request, 'loginregister.html', {'msg': '你已经有账号了，请登录'})
    User.objects.create(name=name, tel=tel, password=pwd)
    return render(request, 'loginregister.html', {'msg': '注册成功，请登录！'})


def logout(request):
    obj = redirect('/')
    obj.delete_cookie('uid')
    return obj

# ==================== 我的订单 ====================

@check_login
def myorder(request):
    uid, username = get_user_context(request)
    order_list = Order.objects.filter(user_id=uid) if uid != -1 else []
    return render(request, 'myorder.html', locals())



# ==================== 个人资料 ====================

@method_decorator(check_login, name='get')
class profileView(View):
    def get(self, request):
        uid, _ = get_user_context(request)
        my_info = User.objects.get(id=uid)
        return render(request, 'profile.html', locals())

    def post(self, request):
        uid, _ = get_user_context(request)
        if uid == -1:
            return redirect('/login/')
        info = {}
        if request.POST.get('name'):
            info['name'] = request.POST.get('name')
        if request.POST.get('tel'):
            info['tel'] = request.POST.get('tel')
        if request.POST.get('password1'):
            info['password'] = request.POST.get('password1')
        if info:
            User.objects.filter(id=uid).update(**info)
        resp = redirect('/login/')
        resp.delete_cookie('uid')
        return resp


def data2db1(request):
    Datasets1.objects.all().delete()
    Kind.objects.all().delete()
    dir_path = os.path.join('data', 'train')
    for root, _, files in tqdm(os.walk(dir_path), desc="数据入库："):
        root_split = root.split(os.path.sep)
        code = root_split[-1]
        name = code.split('-')[-1].split('(')[0]
        for file_name in files[:1000]:
            ext = file_name.split(".")[-1]
            if ext not in ['jpg', 'png', 'jpeg']:
                continue
            file_path = "/".join(root_split + [file_name])
            with open(file_path, 'rb') as f:
                file = File(f, name=file_path)
                if not Kind.objects.filter(name=code):
                    Kind.objects.create(name=name, img=file, )

                kind = Kind.objects.get(name=code)
                line = {
                    'kind': kind,
                    'img': file,
                }
                if not Datasets1.objects.filter(**line):
                    Datasets1.objects.create(**line)
    return JsonResponse({'status': 1, 'msg': '操作成功'})

import torch
import torch.nn as nn
def build_densenet(num_classes):
    """
    构建 densenet 模型
    """
    model = densenet121(pretrained = True)
    in_features = model.classifier.in_features
    model.classifier = nn.Linear(in_features, num_classes)
    return model
from PIL import Image
from torchvision import transforms

@method_decorator(check_login, name='get')
class upload1(View):
    """毒蘑菇识别：需登录后使用，识别结果会写入识别记录"""
    def get(self, request, *args, **kwargs):
        uid, username = get_user_context(request)
        return render(request, 'upload1.html', locals())

    def post(self, request, *args, **kwargs):
        from django.conf import settings
        uid, username = get_user_context(request)
        if uid == -1:
            return JsonResponse({'status': 401, 'msg': '请先登录后再进行识别', 'label': ''}, status=401)
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'status': 400, 'msg': '未选择文件', 'label': ''})
        base_dir = getattr(settings, 'BASE_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        upload_dir = os.path.join(base_dir, 'static', 'upload')
        os.makedirs(upload_dir, exist_ok=True)
        from time import strftime
        ext = os.path.splitext(file.name)[1] or '.jpg'
        safe_name = strftime('%Y%m%d%H%M%S') + '_' + (file.name or 'img')[:50]
        safe_name = re.sub(r'[^\w\-.]', '_', safe_name) + ext
        img_path = os.path.join(upload_dir, safe_name)
        try:
            with open(img_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
        except IOError as e:
            return JsonResponse({'status': 500, 'msg': f'保存失败: {e}', 'label': ''})
        try:
            model_pkl = os.path.join(base_dir, 'model', 'index2label.pkl')
            model_pt = os.path.join(base_dir, 'model', 'densenet_Adam-0.001.pt')
            if not os.path.isfile(model_pkl):
                model_pkl = os.path.join(os.getcwd(), 'model', 'index2label.pkl')
                model_pt = os.path.join(os.getcwd(), 'model', 'densenet_Adam-0.001.pt')
            id2class = joblib.load(model_pkl)
            model = build_densenet(len(id2class))
            model.to('cpu')
            ckpt = torch.load(model_pt, map_location='cpu', weights_only=False)
            model.load_state_dict(ckpt['model_weight'])
            label = predict_one_image(model, id2class, img_size=224, image_path=img_path, device='cpu')
            if not label or not str(label).strip():
                label = '未知'
        except Exception as e:
            return JsonResponse({'status': 500, 'msg': f'识别失败: {str(e)}', 'label': ''})
        kind_for_db = (label if label else '未知').strip()
        try:
            media_img = os.path.join(getattr(settings, 'MEDIA_ROOT', os.path.join(base_dir, 'media')), 'img')
            os.makedirs(media_img, exist_ok=True)
            with open(img_path, 'rb') as f:
                from django.core.files import File
                PredictHistory.objects.create(user_id=uid, kind=kind_for_db, img=File(f, name=safe_name))
        except Exception as e:
            return JsonResponse({'status': 500, 'msg': f'识别成功但记录保存失败: {str(e)}', 'label': label})
        return JsonResponse({'status': 200, 'msg': '操作成功', 'label': label})
def predict_one_image(model, id2class, img_size, image_path, device='cpu'):
    """返回预测类别文本。id2class 可为 list 或 dict（int/str 键）。"""
    model = model.to(device)
    image = Image.open(image_path)
    test_transforms = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(img_size),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    image = test_transforms(image)
    image = torch.reshape(image, (1, 3, img_size, img_size))
    model.eval()
    with torch.no_grad():
        image = image.to(device)
        output = model(image)
    idx = output.argmax(1)[0].item()
    if isinstance(id2class, dict):
        text = id2class.get(idx, id2class.get(str(idx), ''))
    else:
        text = id2class[idx] if idx < len(id2class) else ''
    text = str(text).strip() if text else ''
    return text
def data2db(request):
    Datasets.objects.all().delete()
    dir_path = os.path.join('data', '蘑菇是否有毒')
    for root, _, files in tqdm(os.walk(dir_path), desc="数据入库："):
        root_split = root.split(os.path.sep)
        code = root_split[-1]
        for file_name in files[:1000]:
            ext = file_name.split(".")[-1]
            if ext not in ['jpg', 'png', 'jpeg']:
                continue
            file_path = "/".join(root_split + [file_name])
            with open(file_path, 'rb') as f:
                file = File(f, name=file_path)
                line = {
                    'name': code,
                    'img': file,
                }
                if not Datasets.objects.filter(**line):
                    Datasets.objects.create(**line)
    return JsonResponse({'status': 1, 'msg': '操作成功'})

@check_login
def datasets_list(request):
    uid, username = get_user_context(request)
    all_type = ('无毒蘑菇', '有毒蘑菇')
    kind = request.GET.get("kind", all_type[0])

    data_list = Datasets.objects.filter(name=kind)

    # 分页
    total = len(data_list)
    pagenum = request.GET.get("pagenum", 1)
    pagenum = int(pagenum)
    pageSize = 20
    begin = (pagenum - 1) * pageSize
    end = pagenum * pageSize
    newlist = data_list[begin:end]

    return render(request, 'datasets_list.html', locals())


@method_decorator(check_login, name='get')
class predictHistory(View):
    """识别记录：展示当前用户全部识别记录（蘑菇识别 + 山货识别），按时间倒序；需登录"""
    def get(self, request, *args, **kwargs):
        uid, username = get_user_context(request)
        data_list = []
        from django.conf import settings
        # 蘑菇识别记录
        for r in PredictHistory.objects.filter(user_id=uid).order_by('-time'):
            try:
                img_url = r.img.url if r.img else ''
            except Exception:
                img_url = (settings.MEDIA_URL + str(r.img)) if r.img else ''
            data_list.append({
                'time': r.time,
                'img_url': img_url,
                'kind_label': r.kind,
                'record_type': '蘑菇识别',
            })
        # 山货识别记录
        for r in PredictHistory1.objects.filter(user_id=uid).select_related('kind').order_by('-time'):
            img_url = (settings.STATIC_URL.rstrip('/') + '/upload/' + str(r.img)) if r.img else ''
            data_list.append({
                'time': r.time,
                'img_url': img_url,
                'kind_label': r.kind.name if r.kind_id else '',
                'record_type': '山货识别',
            })
        data_list.sort(key=lambda x: x['time'], reverse=True)
        return render(request, 'predictHistory.html', locals())

    def post(self, request, *args, **kwargs):
        return JsonResponse({'status': 200, 'msg': '操作成功'})

class goods_add(View):
    def get(self, request):
        uid, username = get_user_context(request)
        cls_list = Kind.objects.all()
        return render(request, 'goods_add.html', locals())

    def post(self, request):
        uid, username = get_user_context(request)
        if uid == -1:
            return JsonResponse({'code': 403, 'msg': '请先登录'})
        postdata = request.POST.get('data')
        file = request.FILES.get('img')
        if not postdata or not file:
            return JsonResponse({'code': 400, 'msg': '参数不完整'})
        try:
            postdata = json.loads(postdata)
        except (ValueError, TypeError):
            return JsonResponse({'code': 400, 'msg': '数据格式错误'})
        postdata['kind_id'] = int(postdata.get('cls', 0))
        postdata.pop('cls', None)
        postdata.pop('img', None)
        postdata['img'] = file
        postdata['user_id'] = uid
        goods = Goods.objects.create(**postdata)
        return JsonResponse({'code': 200, 'msg': '发布成功', 'id': goods.id})

def build_googlenet(num_classes):
    """
    构建 googlenet 模型
    """
    model = googlenet(pretrained=True)
    model.fc.out_features = num_classes
    return model
@method_decorator(check_login, name='get')
class upload2(View):
    """山货识别：需登录后使用，识别结果会写入识别记录"""
    def get(self, request, *args, **kwargs):
        uid, username = get_user_context(request)
        return render(request, 'upload2.html', locals())

    def post(self, request, *args, **kwargs):
        uid, username = get_user_context(request)
        if uid == -1:
            return JsonResponse({'status': 401, 'msg': '请先登录后再进行识别', 'label': ''}, status=401)
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'status': 400, 'msg': '未选择文件', 'label': ''})
        from django.conf import settings
        base_dir = getattr(settings, 'BASE_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        upload_dir = os.path.join(base_dir, 'static', 'upload')
        os.makedirs(upload_dir, exist_ok=True)
        from time import strftime
        ext = os.path.splitext(file.name)[1] or '.jpg'
        safe_name = strftime('%Y%m%d%H%M%S') + '_' + (file.name or 'img')[:50]
        safe_name = re.sub(r'[^\w\-.]', '_', safe_name) + ext
        img_path = os.path.join(upload_dir, safe_name)
        try:
            with open(img_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
        except IOError as e:
            return JsonResponse({'status': 500, 'msg': f'保存失败: {e}', 'label': ''})
        try:
            model_dir = os.path.join(base_dir, 'model_山货')
            pkl_path = os.path.join(model_dir, 'index2label.pkl')
            pt_path = os.path.join(model_dir, 'GoogLeNet_Adam-0.001.pt')
            if not os.path.isfile(pkl_path):
                model_dir = os.path.join(os.getcwd(), 'model_山货')
                pkl_path = os.path.join(model_dir, 'index2label.pkl')
                pt_path = os.path.join(model_dir, 'GoogLeNet_Adam-0.001.pt')
            id2class = joblib.load(pkl_path)
            model = build_googlenet(len(id2class))
            model.to('cpu')
            ckpt = torch.load(pt_path, map_location='cpu', weights_only=False)
            model.load_state_dict(ckpt['model_weight'])
            label = predict_one_image(model, id2class, img_size=224, image_path=img_path, device='cpu')
            if not label or not str(label).strip():
                label = '未知'
        except Exception as e:
            return JsonResponse({'status': 500, 'msg': f'识别失败: {str(e)}', 'label': ''})
        kind_name = (label if label else '未知').strip()
        try:
            kind, _ = Kind.objects.get_or_create(name=kind_name, defaults={})
            PredictHistory1.objects.create(user_id=uid, kind=kind, img=safe_name)
        except Exception as e:
            return JsonResponse({'status': 500, 'msg': f'识别成功但记录保存失败: {str(e)}', 'label': label})
        return JsonResponse({'status': 200, 'msg': '操作成功', 'label': label})


def commentAjax(request):
    uid = int(request.COOKIES.get('uid', -1))
    if uid == -1:
        return JsonResponse({'ok': False, 'msg': '请先登录后再评论'}, status=200)

    item_id = request.POST.get('item_id')
    content = (request.POST.get('content') or '').strip()
    if not item_id or not content:
        return JsonResponse({'ok': False, 'msg': '评论内容不能为空'}, status=200)

    try:
        item_id = int(item_id)
    except (TypeError, ValueError):
        return JsonResponse({'ok': False, 'msg': '参数错误'}, status=200)

    # 情感分析
    try:
        from sentiment_analysis import analyze_sentiment
        sentiment_result = analyze_sentiment(content)
        sentiment = sentiment_result.get('sentiment', 'neutral')
        sentiment_confidence = sentiment_result.get('confidence', 0.5)
    except Exception as e:
        print(f"情感分析失败: {e}")
        sentiment = 'neutral'
        sentiment_confidence = 0.5

    try:
        Comment.objects.create(
            user_id=uid,
            content=content,
            item_id=item_id,
            sentiment=sentiment,
            sentiment_confidence=sentiment_confidence
        )
        return JsonResponse({'ok': True, 'msg': '评论成功'}, status=200)
    except Exception as e:
        print(f"评论创建失败: {e}")
        return JsonResponse({'ok': False, 'msg': '评论失败，请重试'}, status=200)



@method_decorator(check_login, name='get')
class blog_list(View):
    def get(self, request, *args, **kwargs):
        uid, username = get_user_context(request)
        kind_list = Kind.objects.all()
        if not kind_list:
            newlist = []
            kind = None
        else:
            kind = request.GET.get('kind', kind_list[0].id)
            kind = int(kind)
            newlist = Blog.objects.filter(kind_id=kind)
        return render(request, 'blog_list.html', locals())

    def post(self, request, *args, **kwargs):
        return JsonResponse({'code': 200, 'msg': '操作成功'})

class blog_add(View):
    def get(self, request):
        uid, username = get_user_context(request)
        cls_list = Kind.objects.all()
        return render(request, 'blog_add.html', locals())

    def post(self, request):
        uid, username = get_user_context(request)
        if uid == -1:
            return JsonResponse({'code': 403, 'msg': '请先登录'})
        postdata = request.POST.get('data')
        file = request.FILES.get('img')
        if not postdata or not file:
            return JsonResponse({'code': 400, 'msg': '参数不完整'})
        try:
            postdata = json.loads(postdata)
        except (ValueError, TypeError):
            return JsonResponse({'code': 400, 'msg': '数据格式错误'})
        postdata['kind_id'] = int(postdata.get('cls', 0))
        postdata.pop('cls', None)
        postdata.pop('img', None)
        postdata['img'] = file
        postdata['user_id'] = uid
        blog = Blog.objects.create(**postdata)
        return JsonResponse({'code': 200, 'msg': '发布成功', 'id': blog.id})




class blog_detail(View):
    def get(self, request):
        id_ = request.GET.get('id')
        if not id_:
            return redirect('/blog_list')
        try:
            id_ = int(id_)
            info = Blog.objects.get(id=id_)
        except (ValueError, Blog.DoesNotExist):
            return redirect('/blog_list')
        uid, username = get_user_context(request)
        if uid != info.user_id:
            from django.db.models import F
            Blog.objects.filter(pk=id_).update(view=F('view') + 1)
            info.refresh_from_db()
        comment_list = CommentBlog.objects.filter(item_id=id_)
        return render(request, 'blog_detail.html', locals())

    def post(self, request, *args, **kwargs):
        return JsonResponse({'status': 200, 'msg': '操作成功'})
def commentAjaxblog(request):
    uid = int(request.COOKIES.get('uid', -1))
    if uid == -1:
        return JsonResponse({'ok': False, 'msg': '请先登录后再评论'}, status=200)

    item_id = request.POST.get('item_id')
    content = (request.POST.get('content') or '').strip()
    if not item_id or not content:
        return JsonResponse({'ok': False, 'msg': '评论内容不能为空'}, status=200)

    try:
        item_id = int(item_id)
    except (TypeError, ValueError):
        return JsonResponse({'ok': False, 'msg': '参数错误'}, status=200)

    try:
        from sentiment_analysis import analyze_sentiment
        sentiment_result = analyze_sentiment(content)
        sentiment = sentiment_result.get('sentiment', 'neutral')
        sentiment_confidence = sentiment_result.get('confidence', 0.5)
    except Exception as e:
        print(f"情感分析失败: {e}")
        sentiment = 'neutral'
        sentiment_confidence = 0.5

    try:
        CommentBlog.objects.create(
            user_id=uid,
            content=content,
            item_id=item_id,
            sentiment=sentiment,
            sentiment_confidence=sentiment_confidence
        )
        return JsonResponse({'ok': True, 'msg': '评论成功'}, status=200)
    except Exception as e:
        print(f"评论创建失败: {e}")
        return JsonResponse({'ok': False, 'msg': '评论失败，请重试'}, status=200)

