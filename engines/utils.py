#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用工具函数
"""

import random


def get_desktop_headers(referer: str = "") -> dict:
    """
    获取桌面端浏览器 headers（禁用 gzip，和旧版本一样）
    
    Args:
        referer: Referer URL（可选）
    
    Returns:
        headers dict
    """
    # 桌面端 UA（优先使用，避免移动端页面结构差异）
    desktop_uas = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    ]
    
    headers = {
        "User-Agent": random.choice(desktop_uas),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "identity",  # 禁用 gzip，关键！
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    if referer:
        headers["Referer"] = referer
    
    return headers