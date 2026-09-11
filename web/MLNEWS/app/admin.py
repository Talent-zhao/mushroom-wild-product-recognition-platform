from django import forms
from django.contrib import admin
from django.utils.html import format_html
from app.models import *
from meteorological import config

title = config.GLOBAL_SETTING["global_title"]
admin.site.site_header = title  # 登录和页面左侧标题
admin.site.site_title = f'{title}后台管理'  # 网页标题
admin.site.index_title = f'{title}后台管理'  #


# admin.site.register(User)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # list_display用于设置列表页面要显示的不同字段
    # 添加删除按钮（删除整行）
    def delete_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">删除</a>',
            f'{obj.id}/delete/'  # 使用相对路径进行删除
        )

    delete_button.short_description = '删除'
    delete_button.allow_tags = True  # 允许返回 HTML 标签

    def edit_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">修改</a>',
            f'{obj.id}/change/'  # 使用相对路径进行修改
        )

    edit_button.short_description = '修改'
    edit_button.allow_tags = True  # 允许返回 HTML 标签

    list_display = ['id', 'name', 'tel', 'password', 'delete_button', 'edit_button']


@admin.register(Datasets)
class DatasetsAdmin(admin.ModelAdmin):
    # list_display用于设置列表页面要显示的不同字段
    # 添加删除按钮（删除整行）
    def delete_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">删除</a>',
            f'{obj.id}/delete/'  # 使用相对路径进行删除
        )

    delete_button.short_description = '删除'
    delete_button.allow_tags = True  # 允许返回 HTML 标签

    def edit_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">修改</a>',
            f'{obj.id}/change/'  # 使用相对路径进行修改
        )

    edit_button.short_description = '修改'
    edit_button.allow_tags = True  # 允许返回 HTML 标签

    def img_display(self, obj):
        # 如果不为空
        if obj.img:
            string = '<img src="{}" style="width: 100px; height: 100px;" />'
            # 路径 还是 图片域 返回地址
            url = obj.img if isinstance(obj.img, str) else obj.img.url
            return format_html(string, url)
        return '没有图片'  # 如果没有图片，显示提示信息

    img_display.short_description = '图片预览'  # 自定义列标题
    img_display.allow_tags = True  # 允许返回 HTML 标签

    list_display = ['id', 'name', 'img', 'delete_button', 'edit_button', 'img_display']


@admin.register(PredictHistory)
class PredictHistoryAdmin(admin.ModelAdmin):
    # list_display用于设置列表页面要显示的不同字段
    # 添加删除按钮（删除整行）
    def delete_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">删除</a>',
            f'{obj.id}/delete/'  # 使用相对路径进行删除
        )

    delete_button.short_description = '删除'
    delete_button.allow_tags = True  # 允许返回 HTML 标签

    def edit_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">修改</a>',
            f'{obj.id}/change/'  # 使用相对路径进行修改
        )

    edit_button.short_description = '修改'
    edit_button.allow_tags = True  # 允许返回 HTML 标签

    list_display = ['id', 'user', 'kind', 'img', 'time', 'delete_button', 'edit_button']


@admin.register(Kind)
class KindAdmin(admin.ModelAdmin):
    # list_display用于设置列表页面要显示的不同字段
    # 添加删除按钮（删除整行）
    def delete_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">删除</a>',
            f'{obj.id}/delete/'  # 使用相对路径进行删除
        )

    delete_button.short_description = '删除'
    delete_button.allow_tags = True  # 允许返回 HTML 标签

    def edit_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">修改</a>',
            f'{obj.id}/change/'  # 使用相对路径进行修改
        )

    edit_button.short_description = '修改'
    edit_button.allow_tags = True  # 允许返回 HTML 标签

    def img_display(self, obj):
        # 如果不为空
        if obj.img:
            string = '<img src="{}" style="width: 100px; height: 100px;" />'
            # 路径 还是 图片域 返回地址
            url = obj.img if isinstance(obj.img, str) else obj.img.url
            return format_html(string, url)
        return '没有图片'  # 如果没有图片，显示提示信息

    img_display.short_description = '图片预览'  # 自定义列标题
    img_display.allow_tags = True  # 允许返回 HTML 标签

    list_display = ['id', 'name', 'img', 'delete_button', 'edit_button', 'img_display']


@admin.register(Datasets1)
class Datasets1Admin(admin.ModelAdmin):
    # list_display用于设置列表页面要显示的不同字段
    # 添加删除按钮（删除整行）
    def delete_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">删除</a>',
            f'{obj.id}/delete/'  # 使用相对路径进行删除
        )

    delete_button.short_description = '删除'
    delete_button.allow_tags = True  # 允许返回 HTML 标签

    def edit_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">修改</a>',
            f'{obj.id}/change/'  # 使用相对路径进行修改
        )

    edit_button.short_description = '修改'
    edit_button.allow_tags = True  # 允许返回 HTML 标签

    def img_display(self, obj):
        # 如果不为空
        if obj.img:
            string = '<img src="{}" style="width: 100px; height: 100px;" />'
            # 路径 还是 图片域 返回地址
            url = obj.img if isinstance(obj.img, str) else obj.img.url
            return format_html(string, url)
        return '没有图片'  # 如果没有图片，显示提示信息

    img_display.short_description = '图片预览'  # 自定义列标题
    img_display.allow_tags = True  # 允许返回 HTML 标签

    list_display = ['id', 'kind', 'img', 'delete_button', 'edit_button', 'img_display']


@admin.register(PredictHistory1)
class PredictHistory1Admin(admin.ModelAdmin):
    # list_display用于设置列表页面要显示的不同字段
    # 添加删除按钮（删除整行）
    def delete_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">删除</a>',
            f'{obj.id}/delete/'  # 使用相对路径进行删除
        )

    delete_button.short_description = '删除'
    delete_button.allow_tags = True  # 允许返回 HTML 标签

    def edit_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">修改</a>',
            f'{obj.id}/change/'  # 使用相对路径进行修改
        )

    edit_button.short_description = '修改'
    edit_button.allow_tags = True  # 允许返回 HTML 标签

    list_display = ['id', 'user', 'kind', 'img', 'time', 'delete_button', 'edit_button']


@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    # list_display用于设置列表页面要显示的不同字段
    # 添加删除按钮（删除整行）
    def delete_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">删除</a>',
            f'{obj.id}/delete/'  # 使用相对路径进行删除
        )

    delete_button.short_description = '删除'
    delete_button.allow_tags = True  # 允许返回 HTML 标签

    def edit_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">修改</a>',
            f'{obj.id}/change/'  # 使用相对路径进行修改
        )

    edit_button.short_description = '修改'
    edit_button.allow_tags = True  # 允许返回 HTML 标签

    list_display = ['id', 'user', 'title', 'date', 'img', 'kind', 'content', 'price', 'delete_button', 'edit_button']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # list_display用于设置列表页面要显示的不同字段
    # 添加删除按钮（删除整行）
    def delete_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">删除</a>',
            f'{obj.id}/delete/'  # 使用相对路径进行删除
        )

    delete_button.short_description = '删除'
    delete_button.allow_tags = True  # 允许返回 HTML 标签

    def edit_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">修改</a>',
            f'{obj.id}/change/'  # 使用相对路径进行修改
        )

    edit_button.short_description = '修改'
    edit_button.allow_tags = True  # 允许返回 HTML 标签

    list_display = ['id', 'goods', 'user', 'num', 'today', 'uuid', 'delete_button', 'edit_button']


def _sentiment_locked_badge(obj):
    """列表中「情感已人工确认」统一用徽章展示，避免 simpleui 下布尔列图标错位/不显示。"""
    if obj.sentiment_locked:
        return format_html(
            '<span title="已人工确认，脚本勿覆盖" style="display:inline-flex;align-items:center;'
            'padding:2px 10px;border-radius:999px;background:#e6f7ff;color:#096dd9;'
            'font-size:12px;line-height:1.5;white-space:nowrap;border:1px solid #91d5ff;">'
            '<span style="margin-right:4px;font-weight:bold;">✓</span>已确认</span>'
        )
    return format_html(
        '<span title="未人工确认" style="display:inline-flex;align-items:center;'
        'padding:2px 10px;border-radius:999px;background:#fafafa;color:#8c8c8c;'
        'font-size:12px;line-height:1.5;white-space:nowrap;border:1px solid #d9d9d9;">'
        '未确认</span>'
    )


_sentiment_locked_badge.short_description = '情感已人工确认'
_sentiment_locked_badge.admin_order_field = 'sentiment_locked'
_sentiment_locked_badge.allow_tags = True


_CHECKBOX_STYLE = (
    'width:1.125rem;height:1.125rem;vertical-align:middle;'
    'margin:0 8px 0 0;cursor:pointer;accent-color:#1890ff;'
)


class CommentSentimentAdminForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = '__all__'
        widgets = {
            'sentiment_locked': forms.CheckboxInput(attrs={'style': _CHECKBOX_STYLE}),
        }


class CommentBlogSentimentAdminForm(forms.ModelForm):
    class Meta:
        model = CommentBlog
        fields = '__all__'
        widgets = {
            'sentiment_locked': forms.CheckboxInput(attrs={'style': _CHECKBOX_STYLE}),
        }


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    form = CommentSentimentAdminForm
    # list_display用于设置列表页面要显示的不同字段
    # 添加删除按钮（删除整行）
    def delete_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">删除</a>',
            f'{obj.id}/delete/'  # 使用相对路径进行删除
        )

    delete_button.short_description = '删除'
    delete_button.allow_tags = True  # 允许返回 HTML 标签

    def edit_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">修改</a>',
            f'{obj.id}/change/'  # 使用相对路径进行修改
        )

    edit_button.short_description = '修改'
    edit_button.allow_tags = True  # 允许返回 HTML 标签

    list_display = ['id', 'item', 'user', 'content', 'sentiment', 'sentiment_confidence', _sentiment_locked_badge, 'date', 'delete_button', 'edit_button']
    readonly_fields = ['id', 'item', 'user', 'content', 'date', 'sentiment_confidence']

    def save_model(self, request, obj, form, change):
        """
        管理员在后台修改情感标签时，可以将其视为“人工确认”：
        - 只要在表单中改动了 sentiment 字段且保存为负面，就自动打上锁定标记；
        - 也允许管理员手动勾选/取消 sentiment_locked 以解锁。
        之后如果有批量重算脚本，应当跳过 sentiment_locked=True 的记录。
        """
        if change and form is not None and 'sentiment' in getattr(form, 'changed_data', []):
            if obj.sentiment == 'negative':
                obj.sentiment_locked = True
        super().save_model(request, obj, form, change)


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    # list_display用于设置列表页面要显示的不同字段
    # 添加删除按钮（删除整行）
    def delete_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">删除</a>',
            f'{obj.id}/delete/'  # 使用相对路径进行删除
        )

    delete_button.short_description = '删除'
    delete_button.allow_tags = True  # 允许返回 HTML 标签

    def edit_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">修改</a>',
            f'{obj.id}/change/'  # 使用相对路径进行修改
        )

    edit_button.short_description = '修改'
    edit_button.allow_tags = True  # 允许返回 HTML 标签

    def img_display(self, obj):
        # 如果不为空
        if obj.img:
            string = '<img src="{}" style="width: 100px; height: 100px;" />'
            # 路径 还是 图片域 返回地址
            url = obj.img if isinstance(obj.img, str) else obj.img.url
            return format_html(string, url)
        return '没有图片'  # 如果没有图片，显示提示信息

    img_display.short_description = '图片预览'  # 自定义列标题
    img_display.allow_tags = True  # 允许返回 HTML 标签

    list_display = ['id', 'user', 'kind', 'title', 'tags', 'content', 'date', 'img', 'delete_button', 'edit_button',
                    'img_display']


@admin.register(CommentBlog)
class CommentBlogAdmin(admin.ModelAdmin):
    form = CommentBlogSentimentAdminForm
    # list_display用于设置列表页面要显示的不同字段
    # 添加删除按钮（删除整行）
    def delete_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">删除</a>',
            f'{obj.id}/delete/'  # 使用相对路径进行删除
        )

    delete_button.short_description = '删除'
    delete_button.allow_tags = True  # 允许返回 HTML 标签

    def edit_button(self, obj):
        return format_html(
            '<a style=" background-color: white" class="button" href="{}">修改</a>',
            f'{obj.id}/change/'  # 使用相对路径进行修改
        )

    edit_button.short_description = '修改'
    edit_button.allow_tags = True  # 允许返回 HTML 标签

    list_display = ['id', 'item', 'user', 'content', 'sentiment', 'sentiment_confidence', _sentiment_locked_badge, 'date', 'delete_button', 'edit_button']
    readonly_fields = ['id', 'item', 'user', 'content', 'date', 'sentiment_confidence']

    def save_model(self, request, obj, form, change):
        if change and form is not None and 'sentiment' in getattr(form, 'changed_data', []):
            if obj.sentiment == 'negative':
                obj.sentiment_locked = True
        super().save_model(request, obj, form, change)


from django.contrib.auth.models import Group, User

admin.site.unregister(Group)
admin.site.unregister(User)