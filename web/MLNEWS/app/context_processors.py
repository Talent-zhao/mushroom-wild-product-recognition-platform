"""
上下文管理器

"""
from meteorological import config
def global_context(request):
    return_dict = {}
    # 全局设置
    return_dict.update(config.GLOBAL_SETTING)
    return return_dict
