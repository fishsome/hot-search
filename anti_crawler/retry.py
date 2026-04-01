#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能重试模块 - 反爬虫基础组件
支持自适应重试、指数退避、错误分类
"""

import time
import random
from functools import wraps
from typing import Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)


class RetryManager:
    """智能重试管理器"""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def calculate_delay(self, retry_count: int) -> float:
        """计算重试延迟（指数退避 + jitter）"""
        # 指数退避
        delay = self.base_delay * (self.exponential_base ** retry_count)
        # 限制最大延迟
        delay = min(delay, self.max_delay)
        # 添加随机抖动（jitter）
        if self.jitter:
            delay = delay + random.uniform(0, self.base_delay)
        return delay

    def should_retry(self, exception: Exception) -> bool:
        """判断是否应该重试（基于异常类型）"""
        # 网络错误 - 重试
        retry_exceptions = [
            "ConnectionError",
            "Timeout",
            "HTTPError",
            "RemoteDisconnected",
            "ReadTimeout",
            "ConnectTimeout",
        ]
        
        exception_name = type(exception).__name__
        
        # 4xx错误（客户端错误） - 不重试（除了429）
        if "HTTPError" in exception_name:
            if hasattr(exception, "response"):
                status_code = exception.response.status_code
                if status_code == 429:  # Too Many Requests - 重试
                    return True
                elif 400 <= status_code < 500:  # 其他4xx - 不重试
                    return False
        
        # 网络错误 - 重试
        return any(retry_exc in exception_name for retry_exc in retry_exceptions)

    def retry(self, func: Callable) -> Callable:
        """装饰器：为函数添加重试逻辑"""
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retry_count = 0
            last_exception = None
            
            while retry_count <= self.max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # 判断是否应该重试
                    if not self.should_retry(e):
                        logger.error(f"不可重试的异常: {type(e).__name__}: {str(e)[:100]}")
                        raise e
                    
                    # 达到最大重试次数
                    if retry_count >= self.max_retries:
                        logger.error(f"达到最大重试次数 ({self.max_retries})，放弃")
                        raise e
                    
                    # 计算延迟并等待
                    delay = self.calculate_delay(retry_count)
                    logger.warning(
                        f"重试 {retry_count + 1}/{self.max_retries}，"
                        f"延迟 {delay:.2f}s，异常: {type(e).__name__}"
                    )
                    time.sleep(delay)
                    retry_count += 1
            
            # 所有重试失败，抛出最后的异常
            raise last_exception
        
        return wrapper


def retry_on_failure(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
) -> Callable:
    """便捷装饰器：为函数添加重试逻辑"""
    retry_manager = RetryManager(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
    )
    return retry_manager.retry


if __name__ == "__main__":
    # 测试
    import requests
    
    @retry_on_failure(max_retries=3, base_delay=1.0)
    def test_request():
        response = requests.get("https://httpbin.org/status/500", timeout=2)
        response.raise_for_status()
        return response
    
    try:
        result = test_request()
    except Exception as e:
        print(f"最终失败: {e}")