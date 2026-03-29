#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hot Search v2.2 - 缓存管理模块

缓存策略：
1. 本地文件缓存（默认）
2. Redis 缓存（可选）
3. 缓存时间：5 分钟

作者：FishSome
"""

import json
import os
import hashlib
import time
from pathlib import Path
from typing import Optional, Any


class FileCache:
    """本地文件缓存"""
    
    def __init__(self, cache_dir: str = None, ttl: int = 300):
        """
        Args:
            cache_dir: 缓存目录路径
            ttl: 缓存有效期（秒），默认 5 分钟
        """
        if cache_dir is None:
            cache_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "cache"
            )
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl  # 缓存时间（秒）
    
    def _generate_key(self, key: str) -> str:
        """生成缓存键（文件名）"""
        # 简单 Hash 处理
        hash_obj = hashlib.md5(key.encode())
        return f"{hash_obj.hexdigest()}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """
        从缓存获取数据
        
        Args:
            key: 缓存键
        
        Returns:
            缓存数据，过期返回 None
        """
        filename = self._generate_key(key)
        filepath = self.cache_dir / filename
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 检查是否过期
            timestamp = data.get("timestamp", 0)
            if time.time() - timestamp > self.ttl:
                # 过期，删除文件
                filepath.unlink()
                return None
            
            return data.get("value")
        except (json.JSONDecodeError, IOError):
            return None
    
    def set(self, key: str, value: Any) -> bool:
        """
        设置缓存数据
        
        Args:
            key: 缓存键
            value: 缓存值
        
        Returns:
            True 表示成功
        """
        filename = self._generate_key(key)
        filepath = self.cache_dir / filename
        
        try:
            data = {
                "value": value,
                "timestamp": time.time(),
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except IOError:
            return False
    
    def delete(self, key: str) -> bool:
        """
        删除缓存数据
        
        Args:
            key: 缓存键
        
        Returns:
            True 表示成功
        """
        filename = self._generate_key(key)
        filepath = self.cache_dir / filename
        
        if filepath.exists():
            filepath.unlink()
            return True
        return False
    
    def clear(self) -> int:
        """
        清空所有缓存
        
        Returns:
            删除的文件数量
        """
        count = 0
        for filepath in self.cache_dir.glob("*.json"):
            filepath.unlink()
            count += 1
        return count
    
    def size(self) -> int:
        """获取缓存数据条数"""
        return len(list(self.cache_dir.glob("*.json")))


class CacheManager:
    """缓存管理器（单例）"""
    
    _instance: Optional["CacheManager"] = None
    _cache: Optional[FileCache] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = FileCache()
        return cls._instance
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> bool:
        """设置缓存"""
        return self._cache.set(key, value)
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        return self._cache.delete(key)
    
    def clear(self) -> int:
        """清空缓存"""
        return self._cache.clear()


# 全局缓存实例
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """获取缓存管理器单例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def cached(ttl: int = 300):
    """
    缓存装饰器
    
    Args:
        ttl: 缓存时间（秒）
    
    Usage:
        @cached(ttl=300)
        def get_hot(platform: str):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{args}:{sorted(kwargs.items())}"
            
            # 尝试从缓存获取
            cache = get_cache_manager()
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 调用原函数
            result = func(*args, **kwargs)
            
            # 存入缓存
            cache.set(cache_key, result)
            
            return result
        
        return wrapper
    return decorator


# 命令行工具
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("缓存管理工具")
        print("用法:")
        print("  python cache.py status     查看缓存状态")
        print("  python cache.py clear      清空缓存")
        print("  python cache.py delete <key>  删除指定缓存")
        sys.exit(0)
    
    cmd = sys.argv[1]
    manager = get_cache_manager()
    
    if cmd == "status":
        size = manager._cache.size()
        print(f"缓存目录: {manager._cache.cache_dir}")
        print(f"缓存条数: {size}")
        
    elif cmd == "clear":
        count = manager.clear()
        print(f"已清空 {count} 条缓存")
        
    elif cmd == "delete" and len(sys.argv) > 2:
        key = sys.argv[2]
        success = manager.delete(key)
        if success:
            print(f"已删除缓存: {key}")
        else:
            print(f"缓存不存在: {key}")
    else:
        print("未知命令")
        sys.exit(1)
