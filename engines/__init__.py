# -*- coding: utf-8 -*-
"""热搜引擎模块"""

from .baidu import get_baidu_hot
from .weibo import get_weibo_hot
from .zhihu import get_zhihu_hot

__all__ = ["get_baidu_hot", "get_weibo_hot", "get_zhihu_hot"]