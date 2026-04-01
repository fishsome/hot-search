#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存管理模块 - 本地缓存新闻数据
JSON Lines格式缓存，支持过期清理
"""

import json
import logging
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)


class NewsCache:
    """新闻缓存管理器"""

    def __init__(
        self,
        cache_path: str = "./cache/news_cache.log",
        max_age: int = 24,  # 小时
        max_size: int = 1000,  # 最大条数
    ):
        self.cache_path = Path(cache_path)
        self.max_age = max_age
        self.max_size = max_size
        
        # 确保缓存目录存在
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

    def save_news(self, news: List[Dict]) -> bool:
        """
        保存新闻到缓存
        
        Args:
            news: 新闻列表
        
        Returns:
            是否保存成功
        """
        try:
            # 添加时间戳
            timestamp = datetime.now().isoformat()
            
            # 写入JSON Lines格式（每行一个JSON对象）
            with open(self.cache_path, "a", encoding="utf-8") as f:
                for item in news:
                    cache_item = {
                        "timestamp": timestamp,
                        "data": item,
                    }
                    f.write(json.dumps(cache_item, ensure_ascii=False) + "\n")
            
            logger.info(f"保存 {len(news)} 条新闻到缓存")
            
            # 清理过期缓存
            self._clean_expired_cache()
            
            return True
        except Exception as e:
            logger.error(f"保存新闻缓存失败: {e}")
            return False

    def load_news(
        self,
        limit: int = 100,
        source: Optional[str] = None,
    ) -> List[Dict]:
        """
        从缓存加载新闻
        
        Args:
            limit: 加载条数
            source: 过滤新闻源（可选）
        
        Returns:
            新闻列表
        """
        if not self.cache_path.exists():
            logger.info("缓存文件不存在")
            return []
        
        try:
            news = []
            with open(self.cache_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        cache_item = json.loads(line.strip())
                        item = cache_item.get("data", {})
                        
                        # 过滤新闻源
                        if source and item.get("source") != source:
                            continue
                        
                        news.append(item)
                        
                        if len(news) >= limit:
                            break
                    except json.JSONDecodeError:
                        continue
            
            logger.info(f"从缓存加载 {len(news)} 条新闻")
            return news
        except Exception as e:
            logger.error(f"加载新闻缓存失败: {e}")
            return []

    def get_recent_news(self, hours: int = 1) -> List[Dict]:
        """
        获取最近N小时的新闻
        
        Args:
            hours: 时间范围（小时）
        
        Returns:
            新闻列表
        """
        if not self.cache_path.exists():
            return []
        
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_news = []
            
            with open(self.cache_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        cache_item = json.loads(line.strip())
                        timestamp_str = cache_item.get("timestamp", "")
                        timestamp = datetime.fromisoformat(timestamp_str)
                        
                        # 过滤时间范围
                        if timestamp >= cutoff_time:
                            recent_news.append(cache_item.get("data", {}))
                    except (json.JSONDecodeError, ValueError):
                        continue
            
            return recent_news
        except Exception as e:
            logger.error(f"获取最近新闻失败: {e}")
            return []

    def _clean_expired_cache(self) -> None:
        """
        清理过期缓存
        """
        if not self.cache_path.exists():
            return
        
        try:
            cutoff_time = datetime.now() - timedelta(hours=self.max_age)
            valid_items = []
            
            # 读取所有缓存
            with open(self.cache_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        cache_item = json.loads(line.strip())
                        timestamp_str = cache_item.get("timestamp", "")
                        timestamp = datetime.fromisoformat(timestamp_str)
                        
                        # 保留未过期的缓存
                        if timestamp >= cutoff_time:
                            valid_items.append(cache_item)
                    except (json.JSONDecodeError, ValueError):
                        continue
            
            # 限制最大条数
            if len(valid_items) > self.max_size:
                valid_items = valid_items[-self.max_size:]
            
            # 重写缓存文件
            with open(self.cache_path, "w", encoding="utf-8") as f:
                for item in valid_items:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
            
            logger.info(f"清理过期缓存，保留 {len(valid_items)} 条")
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")

    def clear_cache(self) -> bool:
        """
        清空缓存
        
        Returns:
            是否清空成功
        """
        try:
            if self.cache_path.exists():
                self.cache_path.unlink()
                logger.info("缓存已清空")
            return True
        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
            return False


if __name__ == "__main__":
    # 测试
    cache = NewsCache()
    
    # 保存测试新闻
    test_news = [
        {"title": "测试新闻1", "link": "http://example.com/1", "source": "测试"},
        {"title": "测试新闻2", "link": "http://example.com/2", "source": "测试"},
    ]
    cache.save_news(test_news)
    
    # 加载新闻
    loaded_news = cache.load_news(limit=10)
    print(f"加载新闻: {len(loaded_news)} 条")