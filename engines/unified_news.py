#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻抓取器 - 使用通用提取器
支持所有新闻源，自动检测类型
"""

import logging
from typing import List, Dict
from engines.universal_extractor import UniversalNewsExtractor
from config.news_sources import NEWS_SOURCES, NEWS_GROUPS

logger = logging.getLogger(__name__)


class UnifiedNewsFetcher:
    """统一新闻抓取器（使用通用提取器）"""

    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.extractor = UniversalNewsExtractor(timeout=timeout)

    def fetch_from_source(
        self,
        source: str,
        limit: int = 20,
    ) -> List[Dict]:
        """
        从特定新闻源抓取
        
        Args:
            source: 新闻源名称（NEWS_SOURCES的key）
            limit: 抓取条数
        
        Returns:
            新闻列表
        """
        if source not in NEWS_SOURCES:
            logger.error(f"新闻源 {source} 不存在")
            return []
        
        config = NEWS_SOURCES[source]
        
        try:
            news = self.extractor.extract(config['url'], limit=limit)
            logger.info(f"{config['name']}抓取成功: {len(news)}条")
            return news
        except Exception as e:
            logger.error(f"{config['name']}抓取失败: {e}")
            return []

    def fetch_all(
        self,
        limit_per_source: int = 10,
        total_limit: int = 100,
        sources: List[str] = None,
    ) -> List[Dict]:
        """
        抓取所有新闻源
        
        Args:
            limit_per_source: 每个新闻源抓取条数
            total_limit: 总结果条数上限
            sources: 指定新闻源列表（None则使用全部）
        
        Returns:
            新闻列表
        """
        if sources is None:
            sources = NEWS_GROUPS['all']
        
        all_news = []
        
        for source in sources:
            news = self.fetch_from_source(source, limit=limit_per_source)
            all_news.extend(news)
        
        # 去重（基于 link）
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

    def fetch_group(
        self,
        group: str = 'priority',
        limit_per_source: int = 10,
    ) -> List[Dict]:
        """
        抓取指定分组的新闻源
        
        Args:
            group: 分组名称（all/domestic/international/priority）
            limit_per_source: 每个新闻源抓取条数
        
        Returns:
            新闻列表
        """
        sources = NEWS_GROUPS.get(group, NEWS_GROUPS['all'])
        return self.fetch_all(limit_per_source=limit_per_source, sources=sources)


# 兼容旧版本的类名
class NewsSearchEngine(UnifiedNewsFetcher):
    """兼容旧版本的类名"""
    pass