#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻抓取聚合器 - 统一新闻抓取接口
4大新闻源：联合早报、RT、UN、AP
直接复用旧版本逻辑
"""

import logging
from typing import List, Dict
from engines.unified_news import UnifiedNewsFetcher
from anti_crawler.headers_pool import HeadersPool

logger = logging.getLogger(__name__)


class NewsAggregator:
    """新闻抓取聚合器"""

    def __init__(
        self,
        timeout: int = 3,
        sources: List[str] = ["zaobao", "rt", "un_news", "apnews"],
    ):
        self.timeout = timeout
        self.sources = sources
        
        # 使用统一的新闻抓取器（复用旧版本逻辑）
        self.fetcher = UnifiedNewsFetcher(timeout=timeout)
        
        # 反爬组件
        self.headers_pool = HeadersPool()

    def fetch_all_news(
        self,
        limit_per_source: int = 20,
        total_limit: int = 100,
    ) -> List[Dict]:
        """
        抓取所有新闻源
        
        Args:
            limit_per_source: 每个新闻源抓取条数
            total_limit: 总结果条数上限
        
        Returns:
            新闻列表 [{title, link, snippet, source}]
        """
        all_news = []
        
        # 并行抓取所有新闻源
        for source_name in self.sources:
            try:
                news = self.fetcher.fetch_from_source(source_name, limit=limit_per_source)
                all_news.extend(news)
                logger.info(f"新闻源 {source_name} 抓取 {len(news)} 条")
            except Exception as e:
                logger.error(f"新闻源 {source_name} 抓取失败: {e}")
                continue
        
        # 去重（基于link）
        seen_links = set()
        unique_news = []
        for item in all_news:
            link = item.get("link", "")
            if link and link not in seen_links:
                seen_links.add(link)
                unique_news.append(item)
        
        # 限制总数
        final_news = unique_news[:total_limit]
        
        logger.info(f"新闻聚合完成: {len(final_news)} 条新闻")
        return final_news

    def fetch_from_source(
        self,
        source: str,
        limit: int = 20,
    ) -> List[Dict]:
        """
        从特定新闻源抓取
        
        Args:
            source: 新闻源名称
            limit: 抓取条数
        
        Returns:
            新闻列表
        """
        return self.fetcher.fetch_from_source(source, limit=limit)


if __name__ == "__main__":
    # 测试
    aggregator = NewsAggregator()
    news = aggregator.fetch_all_news(limit_per_source=10, total_limit=30)
    
    print(f"新闻 ({len(news)}条):")
    for i, item in enumerate(news, 1):
        print(f"{i}. {item['title']} [{item['source']}]")