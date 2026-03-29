# -*- coding: utf-8 -*-
"""热搜引擎基础模块"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random
import time
from typing import List, Dict, Optional

# 随机 User-Agent 池
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
]


def get_random_ua() -> str:
    """获取随机 User-Agent"""
    return random.choice(USER_AGENTS)


def create_session(retries: int = 3) -> requests.Session:
    """创建带重试机制的 Session"""
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_with_retry(
    url: str,
    headers: Optional[Dict] = None,
    timeout: int = 5,
    retries: int = 3,
    delay_range: tuple = (0.5, 1.5),
) -> Optional[requests.Response]:
    """
    带重试的请求
    
    Args:
        url: 请求 URL
        headers: 请求头（不传则自动生成）
        timeout: 超时时间（秒）
        retries: 重试次数
        delay_range: 延迟范围（秒）
    
    Returns:
        Response 对象或 None
    """
    if headers is None:
        headers = {
            "User-Agent": get_random_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            # "Accept-Encoding": "gzip, deflate, br",  # 让 requests 自动处理
            "Connection": "keep-alive",
        }
    
    session = create_session(retries=1)  # Session 内部不重试，手动重试
    
    for attempt in range(retries):
        try:
            # 随机延迟
            if attempt > 0:
                delay = random.uniform(*delay_range)
                time.sleep(delay)
            
            # 随机 UA
            headers["User-Agent"] = get_random_ua()
            
            response = session.get(url, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                return response
            elif response.status_code in [429, 503]:
                # 被限流，等待更长时间
                time.sleep(random.uniform(2, 4))
                continue
            else:
                print(f"HTTP {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"超时 (尝试 {attempt + 1}/{retries})")
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {str(e)[:50]} (尝试 {attempt + 1}/{retries})")
    
    return None