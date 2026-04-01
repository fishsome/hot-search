#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时调度器 - 早中晚定时抓取新闻
支持后台定时任务
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import threading
import time
import schedule
from core.news_fetcher import NewsAggregator
from core.cache import NewsCache
from core.recommender import NewsRecommender

logger = logging.getLogger(__name__)


class NewsScheduler:
    """新闻定时调度器"""

    def __init__(
        self,
        schedule_config: Dict[str, str] = None,
        batch_size: int = 50,
        max_batch_size: int = 100,
    ):
        # 默认调度配置
        if not schedule_config:
            schedule_config = {
                "morning": "07:00",
                "noon": "12:00",
                "evening": "21:00",
            }
        
        self.schedule_config = schedule_config
        self.batch_size = batch_size
        self.max_batch_size = max_batch_size
        
        # 核心组件
        self.news_fetcher = NewsAggregator()
        self.cache = NewsCache()
        self.recommender = NewsRecommender()
        
        # 运行状态
        self.running = False
        self.thread = None

    def start(self) -> None:
        """
        启动定时调度器（后台线程）
        """
        if self.running:
            logger.warning("调度器已运行")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info(f"定时调度器启动: {self.schedule_config}")

    def stop(self) -> None:
        """
        停止定时调度器
        """
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("定时调度器停止")

    def _run_scheduler(self) -> None:
        """
        运行调度器（后台线程）
        """
        # 配置定时任务
        schedule.clear()
        
        for period, time_str in self.schedule_config.items():
            schedule.every().day.at(time_str).do(self._fetch_and_cache_news, period=period)
            logger.info(f"定时任务配置: {period} @ {time_str}")
        
        # 运行调度循环
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

    def _fetch_and_cache_news(self, period: str) -> None:
        """
        定时任务：抓取并缓存新闻
        
        Args:
            period: 时间段（morning/noon/evening）
        """
        logger.info(f"定时任务执行: {period} @ {datetime.now().isoformat()}")
        
        try:
            # 抓取新闻
            news = self.news_fetcher.fetch_all_news(
                limit_per_source=self.batch_size // 4,
                total_limit=self.max_batch_size,
            )
            
            if news:
                # 缓存新闻
                self.cache.save_news(news)
                
                # 推荐新闻
                recommended = self.recommender.recommend(news, count=10)
                
                logger.info(f"定时任务完成: 抓取 {len(news)} 条，推荐 {len(recommended)} 条")
            else:
                logger.warning(f"定时任务失败: 无新闻抓取")
        except Exception as e:
            logger.error(f"定时任务异常: {e}")

    def fetch_now(
        self,
        batch_size: int = None,
    ) -> Dict:
        """
        立即抓取新闻（手动触发）
        
        Args:
            batch_size: 抓取条数
        
        Returns:
            抓取结果 {news, recommended, count}
        """
        if not batch_size:
            batch_size = self.batch_size
        
        logger.info(f"手动抓取: {batch_size} 条")
        
        try:
            # 抓取新闻
            news = self.news_fetcher.fetch_all_news(
                limit_per_source=batch_size // 4,
                total_limit=self.max_batch_size,
            )
            
            if news:
                # 缓存新闻
                self.cache.save_news(news)
                
                # 推荐新闻
                recommended = self.recommender.recommend(news, count=10)
                
                result = {
                    "news": news,
                    "recommended": recommended,
                    "count": len(news),
                    "timestamp": datetime.now().isoformat(),
                }
                
                logger.info(f"手动抓取完成: {len(news)} 条")
                return result
            else:
                return {
                    "news": [],
                    "recommended": [],
                    "count": 0,
                    "error": "无新闻抓取",
                }
        except Exception as e:
            logger.error(f"手动抓取失败: {e}")
            return {
                "news": [],
                "recommended": [],
                "count": 0,
                "error": str(e),
            }

    def get_cached_news(self, limit: int = 100) -> List[Dict]:
        """
        获取缓存的新闻
        
        Args:
            limit: 获取条数
        
        Returns:
            新闻列表
        """
        return self.cache.load_news(limit=limit)

    def get_recent_news(self, hours: int = 1) -> List[Dict]:
        """
        获取最近N小时的新闻
        
        Args:
            hours: 时间范围
        
        Returns:
            新闻列表
        """
        return self.cache.get_recent_news(hours=hours)


if __name__ == "__main__":
    # 测试
    scheduler = NewsScheduler()
    
    # 手动抓取测试
    result = scheduler.fetch_now(batch_size=30)
    
    print(f"抓取结果: {result['count']} 条新闻")
    print(f"推荐新闻: {len(result['recommended'])} 条")
    
    for i, item in enumerate(result["recommended"], 1):
        print(f"{i}. {item['title']}")