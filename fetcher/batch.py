#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hot Search v2.0 - 批量二级爬取模块
支持热搜详情页批量抓取，自动频率控制

作者：FishSome
安全原则：
- 每次请求间隔 2-5 秒随机
- UA 轮换
- 完整请求头伪装
- 每分钟不超过 20 次
- 失败重试指数退避
"""

import os
import sys
import time
import random
import json
from typing import Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from collections import deque

try:
    from ..utils.anti_crawl import get_headers, get_random_ua, create_retry_session, RateLimit
    from ..utils.config import get_config
    from .article import ArticleFetcher, scrape_url
    from ..engines.baidu import get_baidu_hot
    from ..engines.weibo import get_weibo_hot
    from ..engines.zhihu import get_zhihu_hot
    from ..engines.douyin import get_douyin_hot
    from ..engines.toutiao import get_toutiao_hot
except ImportError:
    # 直接运行时使用绝对导入
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.anti_crawl import get_headers, get_random_ua, create_retry_session, RateLimit
    from utils.config import get_config
    from fetcher.article import ArticleFetcher, scrape_url
    from engines.baidu import get_baidu_hot
    from engines.weibo import get_weibo_hot
    from engines.zhihu import get_zhihu_hot
    from engines.douyin import get_douyin_hot
    from engines.toutiao import get_toutiao_hot


# ==================== 频率控制装饰器 ====================

def rate_limit(min_delay: float = 2.0, max_delay: float = 5.0, max_per_minute: int = 20):
    """
    频率控制装饰器
    
    Args:
        min_delay: 最小延迟（秒）
        max_delay: 最大延迟（秒）
        max_per_minute: 每分钟最大请求数
    
    Returns:
        装饰器函数
    """
    # 使用闭包保存状态
    request_times: deque = deque(maxlen=max_per_minute)
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # 检查每分钟限制
            while len(request_times) >= max_per_minute:
                oldest = request_times[0]
                wait_time = 60 - (now - oldest)
                if wait_time > 0:
                    time.sleep(wait_time + random.uniform(0.1, 0.5))
                now = time.time()
                # 清理过期的时间戳
                while request_times and (now - request_times[0]) >= 60:
                    request_times.popleft()
            
            # 随机延迟
            if request_times:
                elapsed = now - request_times[-1]
                if elapsed < min_delay:
                    delay = min_delay - elapsed + random.uniform(0, max_delay - min_delay)
                    time.sleep(delay)
            else:
                # 第一个请求也加一点随机延迟
                time.sleep(random.uniform(0.5, 1.5))
            
            # 记录请求时间
            request_times.append(time.time())
            
            # 执行原函数
            return func(*args, **kwargs)
        
        wrapper.request_times = request_times  # 暴露状态以便调试
        return wrapper
    
    return decorator


# ==================== 批量爬取器 ====================

@dataclass
class ScrapeResult:
    """抓取结果"""
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    success: bool = False
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class HotDetailResult:
    """热搜详情结果"""
    rank: int
    title: str
    url: str
    hot: str
    detail: Optional[Dict] = None  # {"content", "images", "summary"}
    success: bool = False
    error: Optional[str] = None


class BatchScraper:
    """批量爬取器，自动控制频率"""
    
    # 热搜引擎映射
    HOT_ENGINES = {
        "baidu": get_baidu_hot,
        "weibo": get_weibo_hot,
        "zhihu": get_zhihu_hot,
        "douyin": get_douyin_hot,
        "toutiao": get_toutiao_hot,
    }
    
    def __init__(
        self,
        min_delay: float = 2.0,
        max_delay: float = 5.0,
        max_per_minute: int = 20,
        max_retries: int = 3,
        timeout: int = 15,
    ):
        """
        初始化批量爬取器
        
        Args:
            min_delay: 最小延迟 2 秒
            max_delay: 最大延迟 5 秒
            max_per_minute: 每分钟最多 20 次
            max_retries: 最大重试次数
            timeout: 单次请求超时
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.max_per_minute = max_per_minute
        self.max_retries = max_retries
        self.timeout = timeout
        
        # 请求时间记录（用于频率控制）
        self._request_times: deque = deque(maxlen=max_per_minute)
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "success_count": 0,
            "failure_count": 0,
            "total_time": 0.0,
        }
        
        # 创建文章抓取器
        self.article_fetcher = ArticleFetcher()
    
    def _wait_for_rate_limit(self):
        """等待以满足频率限制"""
        now = time.time()
        
        # 检查每分钟限制
        while len(self._request_times) >= self.max_per_minute:
            oldest = self._request_times[0]
            wait_time = 60 - (now - oldest)
            if wait_time > 0:
                # 加一点随机抖动
                actual_wait = wait_time + random.uniform(0.1, 0.5)
                time.sleep(actual_wait)
            now = time.time()
            # 清理过期的时间戳
            while self._request_times and (now - self._request_times[0]) >= 60:
                self._request_times.popleft()
        
        # 检查最小间隔
        if self._request_times:
            elapsed = now - self._request_times[-1]
            if elapsed < self.min_delay:
                # 随机延迟
                delay = self.min_delay - elapsed + random.uniform(0, self.max_delay - self.min_delay)
                time.sleep(delay)
        else:
            # 第一个请求也加一点随机延迟
            time.sleep(random.uniform(0.5, 1.5))
        
        # 记录请求时间
        self._request_times.append(time.time())
    
    def _scrape_single_url(self, url: str) -> ScrapeResult:
        """
        抓取单个 URL
        
        Args:
            url: 目标 URL
        
        Returns:
            ScrapeResult 对象
        """
        result = ScrapeResult(url=url)
        
        # 等待频率控制
        self._wait_for_rate_limit()
        
        # 重试机制
        for attempt in range(self.max_retries):
            try:
                # 每次重试更换 UA
                headers = get_headers()
                
                # 使用文章抓取器
                scrape_result = scrape_url(url)
                
                if scrape_result.get("success"):
                    result.title = scrape_result.get("title")
                    result.content = scrape_result.get("content")
                    result.metadata = scrape_result.get("metadata", {})
                    result.success = True
                    self.stats["success_count"] += 1
                    return result
                
                # 如果失败但有错误信息，记录
                error = scrape_result.get("error", "未知错误")
                
                # 检查是否需要重试
                if "超时" in str(error) or "连接" in str(error):
                    # 指数退避
                    if attempt < self.max_retries - 1:
                        wait_time = (2 ** attempt) * random.uniform(1, 2)
                        time.sleep(wait_time)
                    continue
                
                result.error = error
                break
                
            except Exception as e:
                result.error = str(e)[:100]
                if attempt < self.max_retries - 1:
                    wait_time = (2 ** attempt) * random.uniform(1, 2)
                    time.sleep(wait_time)
        
        self.stats["failure_count"] += 1
        return result
    
    def scrape_batch(
        self,
        urls: List[str],
        callback: Optional[Callable[[int, int, ScrapeResult], None]] = None
    ) -> List[ScrapeResult]:
        """
        批量抓取 URL 列表
        
        Args:
            urls: URL 列表
            callback: 进度回调函数 (current, total, result)
        
        Returns:
            [ScrapeResult 对象列表]
        """
        results = []
        total = len(urls)
        start_time = time.time()
        
        for i, url in enumerate(urls):
            # 抓取单个 URL
            result = self._scrape_single_url(url)
            results.append(result)
            
            # 更新统计
            self.stats["total_requests"] += 1
            
            # 调用回调
            if callback:
                callback(i + 1, total, result)
        
        self.stats["total_time"] = time.time() - start_time
        return results
    
    def scrape_hot_details(
        self,
        platform: str,
        limit: int = 10,
        callback: Optional[Callable[[int, int, HotDetailResult], None]] = None
    ) -> List[HotDetailResult]:
        """
        获取热搜 + 批量抓取详情页
        
        Args:
            platform: baidu/weibo/zhihu/douyin/toutiao
            limit: 只抓取前 N 条的详情
            callback: 进度回调函数
        
        Returns:
            [HotDetailResult 对象列表]
        """
        results = []
        
        # 获取热搜引擎
        engine = self.HOT_ENGINES.get(platform)
        if not engine:
            print(f"不支持的平台: {platform}")
            return results
        
        # 获取热搜列表
        print(f"获取 {platform} 热搜列表...")
        hot_list = engine(limit=limit)
        
        if not hot_list:
            print(f"获取热搜失败或空列表")
            return results
        
        print(f"获取到 {len(hot_list)} 条热搜，开始抓取详情...")
        
        # 批量抓取详情
        for i, item in enumerate(hot_list):
            result = HotDetailResult(
                rank=item.get("rank", i + 1),
                title=item.get("title", ""),
                url=item.get("url", ""),
                hot=item.get("hot", ""),
            )
            
            # 如果有 URL，抓取详情
            if result.url:
                # 等待频率控制
                self._wait_for_rate_limit()
                
                # 抓取详情
                scrape_result = self._scrape_single_url(result.url)
                
                if scrape_result.success:
                    result.detail = {
                        "content": scrape_result.content,
                        "images": scrape_result.metadata.get("images", []),
                        "summary": scrape_result.metadata.get("summary", ""),
                    }
                    result.success = True
                else:
                    result.error = scrape_result.error
            
            results.append(result)
            
            # 更新统计
            self.stats["total_requests"] += 1
            
            # 调用回调
            if callback:
                callback(i + 1, len(hot_list), result)
        
        return results
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            "success_rate": (
                self.stats["success_count"] / self.stats["total_requests"]
                if self.stats["total_requests"] > 0 else 0
            ),
            "avg_time_per_request": (
                self.stats["total_time"] / self.stats["total_requests"]
                if self.stats["total_requests"] > 0 else 0
            ),
        }
    
    def reset_stats(self):
        """重置统计"""
        self.stats = {
            "total_requests": 0,
            "success_count": 0,
            "failure_count": 0,
            "total_time": 0.0,
        }


# ==================== 便捷函数 ====================

def scrape_urls_batch(urls: List[str], **kwargs) -> List[ScrapeResult]:
    """批量抓取 URL（便捷函数）"""
    scraper = BatchScraper(**kwargs)
    return scraper.scrape_batch(urls)


def scrape_hot_with_details(platform: str, limit: int = 10, **kwargs) -> List[HotDetailResult]:
    """获取热搜并抓取详情（便捷函数）"""
    scraper = BatchScraper(**kwargs)
    return scraper.scrape_hot_details(platform, limit)


# ==================== 进度回调示例 ====================

def print_progress(current: int, total: int, result):
    """打印进度回调"""
    status = "✓" if result.success else "✗"
    if isinstance(result, HotDetailResult):
        print(f"[{current}/{total}] {status} {result.title[:30]}")
    else:
        print(f"[{current}/{total}] {status} {result.url[:50]}")


# ==================== 测试 ====================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="批量二级爬取测试")
    parser.add_argument("command", choices=["batch", "hot", "stats"], help="测试命令")
    parser.add_argument("--urls", nargs="+", help="URL 列表")
    parser.add_argument("--platform", default="baidu", help="热搜平台")
    parser.add_argument("--limit", type=int, default=5, help="抓取数量")
    
    args = parser.parse_args()
    
    print("=== 批量二级爬取测试 ===\n")
    
    scraper = BatchScraper()
    
    if args.command == "batch" and args.urls:
        print(f"批量抓取 {len(args.urls)} 个 URL...\n")
        results = scraper.scrape_batch(args.urls, callback=print_progress)
        
        print(f"\n统计: {json.dumps(scraper.get_stats(), indent=2)}")
        
        for r in results:
            if r.success:
                print(f"\n--- {r.title[:50]} ---")
                print(r.content[:500] if r.content else "")
    
    elif args.command == "hot":
        print(f"获取 {args.platform} 热搜详情（前 {args.limit} 条）...\n")
        results = scraper.scrape_hot_details(args.platform, args.limit, callback=print_progress)
        
        print(f"\n统计: {json.dumps(scraper.get_stats(), indent=2)}")
        
        for r in results:
            print(f"\n{r.rank}. {r.title} 🔥{r.hot}")
            if r.detail:
                print(f"摘要: {r.detail.get('summary', '')[:100]}")
    
    elif args.command == "stats":
        print(f"当前统计: {json.dumps(scraper.get_stats(), indent=2)}")