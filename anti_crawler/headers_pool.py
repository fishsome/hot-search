#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Headers池管理 - 反爬虫基础组件
随机轮换 User-Agent 和 Headers，模拟真实浏览器
"""

import random
from typing import Dict

# User-Agent池（主流浏览器）
USER_AGENTS = [
    # Chrome Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    # Chrome Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Firefox Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    # Firefox Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Safari Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    # Edge Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

# Headers池（不同浏览器类型）
HEADERS_POOL = [
    # Chrome标准headers
    {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    },
    # Firefox标准headers
    {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    },
    # Safari标准headers
    {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    },
]


class HeadersPool:
    """Headers池管理器"""

    def __init__(self):
        self.ua_pool = USER_AGENTS
        self.headers_pool = HEADERS_POOL

    def get_random_headers(self) -> Dict[str, str]:
        """获取随机headers（UA + 标准headers）"""
        # 随机选择UA
        ua = random.choice(self.ua_pool)
        # 随机选择基础headers
        base_headers = random.choice(self.headers_pool)
        # 组合完整headers
        headers = base_headers.copy()
        headers["User-Agent"] = ua
        return headers

    def get_headers_for_site(self, site: str) -> Dict[str, str]:
        """为特定站点获取headers（可定制）"""
        headers = self.get_random_headers()
        
        # 特定站点定制headers（如需要）
        # 注意：搜索引擎不要加 Referer，否则会被反爬
        if site == "zaobao":
            headers["Referer"] = "https://www.zaobao.com/"
        elif site == "apnews":
            headers["Referer"] = "https://apnews.com/"
        # 搜索引擎不添加 Referer（模拟有机流量，避免反爬）
        
        return headers


if __name__ == "__main__":
    # 测试
    pool = HeadersPool()
    for i in range(5):
        headers = pool.get_random_headers()
        print(f"Headers {i+1}: {headers['User-Agent'][:50]}...")