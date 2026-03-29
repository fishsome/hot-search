#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hot Search v2.0 - 反爬工具模块
提供 User-Agent 轮换、请求头伪装、重试机制等功能

作者：FishSome
原则：
- 不用第三方 Token
- 不被墙、不被封禁
- 快速、准确
"""

import random
import time
import json
import os
from typing import Dict, Optional, List, Tuple
from urllib.parse import urlparse
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==================== User-Agent 池 ====================

USER_AGENTS = {
    "chrome": [
        # Windows Chrome
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # macOS Chrome
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        # Linux Chrome
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    ],
    "firefox": [
        # Windows Firefox
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        # macOS Firefox
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
        # Linux Firefox
        "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    ],
    "safari": [
        # macOS Safari
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        # iOS Safari
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    ],
    "mobile": [
        # Android Chrome
        "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
        # iOS Safari
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    ],
    "bot_friendly": [
        # 搜索引擎爬虫（某些网站对爬虫更友好）
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
        "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
    ],
}


def get_random_ua(browser: str = "auto") -> str:
    """
    随机获取一个 User-Agent
    
    Args:
        browser: 浏览器类型 (auto/chrome/firefox/safari/mobile/bot_friendly)
    
    Returns:
        User-Agent 字符串
    """
    if browser == "auto":
        # 随机选择一个浏览器类型
        browser = random.choice(["chrome", "chrome", "firefox", "safari", "mobile"])
    
    if browser in USER_AGENTS:
        return random.choice(USER_AGENTS[browser])
    
    return random.choice(USER_AGENTS["chrome"])


# ==================== 浏览器指纹 ====================

BROWSER_FINGERPRINTS = {
    "chrome": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    },
    "firefox": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "max-age=0",
        "Te": "trailers",
    },
    "safari": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "max-age=0",
    },
    "mobile": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua-Mobile": "?1",
    },
}


def get_headers(browser: str = "auto", referer: Optional[str] = None) -> Dict[str, str]:
    """
    生成完整的请求头
    
    Args:
        browser: 浏览器类型
        referer: Referer URL（可选，会自动生成或使用传入值）
    
    Returns:
        请求头字典
    """
    if browser == "auto":
        browser = random.choice(["chrome", "chrome", "firefox", "safari"])
    
    # 获取浏览器指纹
    fingerprint = BROWSER_FINGERPRINTS.get(browser, BROWSER_FINGERPRINTS["chrome"]).copy()
    
    # 添加随机 User-Agent
    fingerprint["User-Agent"] = get_random_ua(browser)
    
    # 添加 Referer
    if referer:
        fingerprint["Referer"] = referer
    else:
        # 生成随机 Referer
        referers = [
            "https://www.google.com/",
            "https://www.google.com/search?q=news",
            "https://www.bing.com/",
            "https://www.baidu.com/",
            "https://www.sogou.com/",
        ]
        fingerprint["Referer"] = random.choice(referers)
    
    # 随机添加一些常用请求头
    if random.random() > 0.5:
        fingerprint["DNT"] = "1"
    
    return fingerprint


# ==================== Referer 生成 ====================

SEARCH_ENGINE_REFERERS = [
    "https://www.google.com/search?q=",
    "https://www.google.com.hk/search?q=",
    "https://www.bing.com/search?q=",
    "https://www.baidu.com/s?wd=",
    "https://www.sogou.com/web?query=",
    "https://www.so.com/s?q=",
    "https://cn.bing.com/search?q=",
]

SOCIAL_REFERERS = [
    "https://www.facebook.com/",
    "https://twitter.com/",
    "https://weibo.com/",
    "https://www.zhihu.com/",
    "https://www.douban.com/",
]


def get_random_referer(url: Optional[str] = None, keyword: Optional[str] = None) -> str:
    """
    生成随机 Referer
    
    Args:
        url: 目标 URL（用于生成同域 Referer）
        keyword: 搜索关键词（用于生成搜索引擎 Referer）
    
    Returns:
        Referer URL
    """
    if url:
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}/"
        
        # 50% 使用同域 Referer，50% 使用搜索引擎
        if random.random() > 0.5:
            return domain
    
    # 使用搜索引擎 Referer
    base = random.choice(SEARCH_ENGINE_REFERERS)
    if keyword:
        return base + keyword
    else:
        keywords = ["news", "today", "latest", "热点", "新闻", "今日"]
        return base + random.choice(keywords)


# ==================== Cookie 管理 ====================

class CookieManager:
    """Cookie 持久化管理"""
    
    def __init__(self, cookie_file: Optional[str] = None):
        self.cookie_file = cookie_file or os.path.expanduser("~/.openclaw/workspace/skills/hot-search/cookies.json")
        self._cookies: Dict[str, Dict[str, str]] = {}
        self._load()
    
    def _load(self):
        """从文件加载 Cookie"""
        try:
            if os.path.exists(self.cookie_file):
                with open(self.cookie_file, "r", encoding="utf-8") as f:
                    self._cookies = json.load(f)
        except Exception:
            self._cookies = {}
    
    def _save(self):
        """保存 Cookie 到文件"""
        try:
            os.makedirs(os.path.dirname(self.cookie_file), exist_ok=True)
            with open(self.cookie_file, "w", encoding="utf-8") as f:
                json.dump(self._cookies, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def get_cookies(self, domain: str) -> Dict[str, str]:
        """获取指定域名的 Cookie"""
        return self._cookies.get(domain, {})
    
    def set_cookies(self, domain: str, cookies: Dict[str, str]):
        """设置指定域名的 Cookie"""
        if domain not in self._cookies:
            self._cookies[domain] = {}
        self._cookies[domain].update(cookies)
        self._save()
    
    def update_from_response(self, url: str, response: requests.Response):
        """从响应中更新 Cookie"""
        domain = urlparse(url).netloc
        cookies = {c.name: c.value for c in response.cookies}
        if cookies:
            self.set_cookies(domain, cookies)
    
    def apply_to_session(self, session: requests.Session, url: str):
        """将 Cookie 应用到 Session"""
        domain = urlparse(url).netloc
        cookies = self.get_cookies(domain)
        for name, value in cookies.items():
            session.cookies.set(name, value, domain=domain)


# ==================== 请求重试 ====================

def create_retry_session(
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    status_forcelist: List[int] = None,
    timeout: int = 10
) -> requests.Session:
    """
    创建带有重试机制的 Session
    
    Args:
        max_retries: 最大重试次数
        backoff_factor: 退避因子（每次重试等待时间 = backoff_factor * (2 ** retry))
        status_forcelist: 触发重试的状态码
        timeout: 默认超时时间
    
    Returns:
        配置好的 Session
    """
    if status_forcelist is None:
        status_forcelist = [403, 429, 500, 502, 503, 504]
    
    session = requests.Session()
    
    # 配置重试策略
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
        raise_on_status=False,  # 不抛出异常
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    # 设置默认超时
    session.timeout = timeout
    
    return session


def retry_request(
    url: str,
    max_retries: int = 3,
    method: str = "GET",
    headers: Optional[Dict] = None,
    params: Optional[Dict] = None,
    data: Optional[Dict] = None,
    json: Optional[Dict] = None,
    timeout: int = 10,
    delay_range: Tuple[float, float] = (0.5, 2.0),
    session: Optional[requests.Session] = None
) -> requests.Response:
    """
    带重试机制的请求
    
    Args:
        url: 请求 URL
        max_retries: 最大重试次数
        method: 请求方法
        headers: 请求头
        params: URL 参数
        data: 表单数据
        json: JSON 数据
        timeout: 超时时间（秒）
        delay_range: 重试延迟范围（秒）
        session: 复用的 Session
    
    Returns:
        Response 对象（失败时返回 None 或抛出异常）
    """
    should_close_session = False
    
    if session is None:
        session = create_retry_session(max_retries=1, timeout=timeout)
        should_close_session = True
    
    # 生成请求头
    if headers is None:
        headers = get_headers()
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # 随机延迟
            if attempt > 0:
                delay = random.uniform(*delay_range) * (1.5 ** attempt)  # 指数退避
                time.sleep(delay)
            
            # 每次请求使用不同的 User-Agent
            if attempt > 0:
                headers["User-Agent"] = get_random_ua()
                headers["Referer"] = get_random_referer(url)
            
            response = session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json,
                timeout=timeout,
                allow_redirects=True,
            )
            
            # 检查是否需要重试
            if response.status_code in [403, 429, 500, 502, 503, 504]:
                continue
            
            return response
            
        except requests.exceptions.Timeout as e:
            last_error = f"Timeout: {url}"
            continue
        except requests.exceptions.ConnectionError as e:
            last_error = f"Connection Error: {str(e)[:100]}"
            continue
        except Exception as e:
            last_error = f"Error: {str(e)[:100]}"
            continue
    
    # 所有重试都失败，返回一个模拟响应
    if should_close_session:
        session.close()
    
    # 创建一个失败的响应对象
    class FailedResponse:
        status_code = 0
        text = ""
        content = b""
        headers = {}
        url = url
        error = last_error
        
        def json(self):
            return {}
        
        def raise_for_status(self):
            raise requests.exceptions.RequestException(last_error or "Request failed")
    
    return FailedResponse()


# ==================== 请求限流 ====================

@dataclass
class RateLimit:
    """请求限流器"""
    max_requests_per_minute: int = 30
    min_interval: float = 0.5  # 最小间隔（秒）
    
    def __post_init__(self):
        self._last_request_time = 0.0
        self._request_count = 0
        self._minute_start = time.time()
    
    def wait(self):
        """等待直到可以进行下一次请求"""
        now = time.time()
        
        # 检查是否需要重置计数
        if now - self._minute_start >= 60:
            self._request_count = 0
            self._minute_start = now
        
        # 检查每分钟限制
        if self._request_count >= self.max_requests_per_minute:
            sleep_time = 60 - (now - self._minute_start)
            if sleep_time > 0:
                time.sleep(sleep_time)
            self._request_count = 0
            self._minute_start = time.time()
        
        # 检查最小间隔
        elapsed = now - self._last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        self._last_request_time = time.time()
        self._request_count += 1


# ==================== 便捷函数 ====================

def safe_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict] = None,
    timeout: int = 10,
    **kwargs
) -> Optional[requests.Response]:
    """
    安全请求（自动处理异常）
    
    Args:
        url: 请求 URL
        method: 请求方法
        headers: 请求头
        timeout: 超时时间
        **kwargs: 其他请求参数
    
    Returns:
        Response 对象或 None
    """
    try:
        if headers is None:
            headers = get_headers()
        
        session = create_retry_session(max_retries=1, timeout=timeout)
        response = session.request(
            method=method.upper(),
            url=url,
            headers=headers,
            timeout=timeout,
            **kwargs
        )
        session.close()
        return response
    except Exception as e:
        print(f"请求失败: {url} - {str(e)[:50]}")
        return None


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=== 反爬工具测试 ===\n")
    
    # 测试 User-Agent
    print("1. 随机 User-Agent:")
    for browser in ["chrome", "firefox", "safari", "mobile"]:
        print(f"  {browser}: {get_random_ua(browser)[:60]}...")
    
    # 测试请求头
    print("\n2. 完整请求头:")
    headers = get_headers()
    for key, value in headers.items():
        print(f"  {key}: {value[:50]}{'...' if len(value) > 50 else ''}")
    
    # 测试 Referer
    print("\n3. 随机 Referer:")
    for _ in range(3):
        print(f"  {get_random_referer()}")
    
    # 测试重试请求
    print("\n4. 重试请求测试:")
    response = retry_request("https://httpbin.org/get", max_retries=2, timeout=5)
    if response and hasattr(response, 'status_code') and response.status_code == 200:
        print(f"  状态码: {response.status_code}")
        print(f"  User-Agent: {response.json().get('headers', {}).get('User-Agent', 'N/A')[:50]}...")
    else:
        print("  请求失败（可能是网络问题）")
    
    print("\n测试完成！")