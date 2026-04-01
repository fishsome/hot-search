#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hot-search v4.0 - 主CLI入口
聚焦主线，简化功能

命令：
  hot-search search [keyword] [engine]        # 搜索聚合
  hot-search news [source] [limit]            # 新闻抓取
  hot-search fetch [batch_size]               # 立即抓取新闻
  hot-search recommend [count]                # 推荐新闻
  hot-search cache [limit]                    # 获取缓存新闻
  hot-search scheduler start                  # 启动定时调度
  hot-search scheduler stop                   # 停止定时调度
  hot-search config show                      # 显示配置
  hot-search config update [category] [weight] # 更新权重
"""

import sys
import json
import logging
from typing import Dict, Any
import yaml
from pathlib import Path

# 核心模块
from core.searcher import SearchAggregator
from core.news_fetcher import NewsAggregator
from core.cache import NewsCache
from core.recommender import NewsRecommender
from core.scheduler import NewsScheduler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class HotSearchCLI:
    """hot-search CLI 主类"""

    def __init__(self, config_path: str = "./config/config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # 初始化核心组件
        self.searcher = SearchAggregator(
            timeout=self.config.get("search", {}).get("timeout", 3),
            max_retries=self.config.get("search", {}).get("max_retries", 2),
        )
        
        self.news_fetcher = NewsAggregator(
            timeout=self.config.get("news", {}).get("timeout", 3),
        )
        
        self.cache = NewsCache(
            cache_path=self.config.get("cache", {}).get("path", "./cache/news_cache.log"),
            max_age=self.config.get("cache", {}).get("max_age", 24),
            max_size=self.config.get("cache", {}).get("max_size", 1000),
        )
        
        self.recommender = NewsRecommender(
            user_focus=self.config.get("recommend", {}).get("user_focus"),
            recommend_count=self.config.get("recommend", {}).get("recommend_count", 5),
        )
        
        self.scheduler = NewsScheduler(
            schedule_config=self.config.get("scheduler", {}).get("schedule"),
            batch_size=self.config.get("scheduler", {}).get("batch_size", 50),
            max_batch_size=self.config.get("scheduler", {}).get("max_batch_size", 100),
        )

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    logger.info(f"加载配置: {self.config_path}")
                    return config
            except Exception as e:
                logger.warning(f"加载配置失败: {e}")
        
        # 默认配置
        return {
            "search": {
                "primary": "bing",
                "fallback": ["sougou", "baidu"],
                "timeout": 3,
                "max_retries": 2,
            },
            "news": {
                "sources": ["zaobao", "rt", "un_news", "apnews"],
                "timeout": 3,
            },
            "scheduler": {
                "schedule": {
                    "morning": "07:00",
                    "noon": "12:00",
                    "evening": "21:00",
                },
                "batch_size": 50,
                "max_batch_size": 100,
            },
            "cache": {
                "path": "./cache/news_cache.log",
                "max_age": 24,
                "max_size": 1000,
            },
            "recommend": {
                "user_focus": {
                    "finance": 3,
                    "war": 2,
                    "tech": 2,
                    "entertainment": 1,
                    "sports": 1,
                },
                "recommend_count": 5,
            },
        }

    def search(self, keyword: str, engine: str = "all") -> Dict:
        """搜索聚合"""
        logger.info(f"搜索: {keyword}, 引擎: {engine}")
        
        if engine == "all":
            results = self.searcher.search_global(keyword, limit=10)
        elif engine == "cn":
            results = self.searcher.search_cn(keyword, limit=10)
        else:
            results = self.searcher.search(keyword, limit=10)
        
        return {
            "success": True,
            "keyword": keyword,
            "engine": engine,
            "count": len(results),
            "results": results,
        }

    def news(self, source: str = "all", limit: int = 20) -> Dict:
        """新闻抓取"""
        logger.info(f"新闻抓取: {source}, 条数: {limit}")
        
        if source == "all":
            news = self.news_fetcher.fetch_all_news(
                limit_per_source=limit // 4,
                total_limit=limit,
            )
        else:
            news = self.news_fetcher.fetch_from_source(source, limit=limit)
        
        return {
            "success": True,
            "source": source,
            "count": len(news),
            "news": news,
        }

    def fetch(self, batch_size: int = 50) -> Dict:
        """立即抓取新闻"""
        logger.info(f"立即抓取: {batch_size} 条")
        return self.scheduler.fetch_now(batch_size=batch_size)

    def recommend(self, count: int = 5) -> Dict:
        """推荐新闻"""
        logger.info(f"推荐新闻: {count} 条")
        
        # 从缓存加载新闻
        cached_news = self.cache.load_news(limit=100)
        
        if cached_news:
            recommended = self.recommender.recommend(cached_news, count=count)
            return {
                "success": True,
                "count": len(recommended),
                "recommended": recommended,
            }
        else:
            return {
                "success": False,
                "error": "缓存无新闻，请先抓取",
            }

    def get_cache(self, limit: int = 100) -> Dict:
        """获取缓存新闻"""
        logger.info(f"获取缓存: {limit} 条")
        
        cached_news = self.cache.load_news(limit=limit)
        
        return {
            "success": True,
            "count": len(cached_news),
            "news": cached_news,
        }

    def scheduler_start(self) -> Dict:
        """启动定时调度"""
        logger.info("启动定时调度")
        self.scheduler.start()
        return {
            "success": True,
            "message": "定时调度器已启动",
            "schedule": self.scheduler.schedule_config,
        }

    def scheduler_stop(self) -> Dict:
        """停止定时调度"""
        logger.info("停止定时调度")
        self.scheduler.stop()
        return {
            "success": True,
            "message": "定时调度器已停止",
        }

    def config_show(self) -> Dict:
        """显示配置"""
        return {
            "success": True,
            "config": self.config,
        }

    def config_update(self, category: str, weight: int) -> Dict:
        """更新权重配置"""
        logger.info(f"更新权重: {category} -> {weight}")
        
        success = self.recommender.update_focus(category, weight)
        
        if success:
            return {
                "success": True,
                "message": f"权重已更新: {category} -> {weight}",
                "user_focus": self.recommender.user_focus,
            }
        else:
            return {
                "success": False,
                "error": f"类别 {category} 不存在",
            }


def main():
    """CLI主入口"""
    cli = HotSearchCLI()
    
    # 解析命令
    if len(sys.argv) < 2:
        print("用法: hot-search [command] [args]")
        print("命令:")
        print("  search [keyword] [engine]        # 搜索聚合")
        print("  news [source] [limit]            # 新闻抓取")
        print("  fetch [batch_size]               # 立即抓取")
        print("  recommend [count]                # 推荐新闻")
        print("  cache [limit]                    # 缓存新闻")
        print("  scheduler start/stop             # 定时调度")
        print("  config show                      # 显示配置")
        print("  config update [category] [weight] # 更新权重")
        sys.exit(1)
    
    command = sys.argv[1]
    
    # 执行命令
    try:
        result = None
        
        if command == "search":
            keyword = sys.argv[2] if len(sys.argv) > 2 else "Python"
            engine = sys.argv[3] if len(sys.argv) > 3 else "all"
            result = cli.search(keyword, engine)
        
        elif command == "news":
            source = sys.argv[2] if len(sys.argv) > 2 else "all"
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            result = cli.news(source, limit)
        
        elif command == "fetch":
            batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            result = cli.fetch(batch_size)
        
        elif command == "recommend":
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            result = cli.recommend(count)
        
        elif command == "cache":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 100
            result = cli.get_cache(limit)
        
        elif command == "scheduler":
            action = sys.argv[2] if len(sys.argv) > 2 else "start"
            if action == "start":
                result = cli.scheduler_start()
            elif action == "stop":
                result = cli.scheduler_stop()
        
        elif command == "config":
            action = sys.argv[2] if len(sys.argv) > 2 else "show"
            if action == "show":
                result = cli.config_show()
            elif action == "update":
                category = sys.argv[3] if len(sys.argv) > 3 else "finance"
                weight = int(sys.argv[4]) if len(sys.argv) > 4 else 3
                result = cli.config_update(category, weight)
        
        else:
            print(f"未知命令: {command}")
            sys.exit(1)
        
        # 输出结果（JSON格式）
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()