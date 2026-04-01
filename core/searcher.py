#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索聚合器 - 统一搜索接口
主搜索引擎：Bing
备用搜索引擎：Sougou、百度
"""

import logging
from typing import List, Dict, Optional
from engines.bing import BingSearchEngine
from engines.sougou import SougouSearchEngine
from engines.baidu import BaiduSearchEngine
from anti_crawler.headers_pool import HeadersPool
from anti_crawler.retry import RetryManager

logger = logging.getLogger(__name__)


class SearchAggregator:
    """搜索聚合器"""

    def __init__(
        self,
        timeout: int = 3,
        max_retries: int = 2,
        primary: str = "bing",
        fallback: List[str] = ["sougou", "baidu"],
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.primary = primary
        self.fallback = fallback
        
        # 初始化搜索引擎
        self.engines = {
            "bing": BingSearchEngine(timeout=timeout),
            "sougou": SougouSearchEngine(timeout=timeout),
            "baidu": BaiduSearchEngine(timeout=timeout),
        }
        
        # 反爬组件
        self.headers_pool = HeadersPool()
        self.retry_manager = RetryManager(max_retries=max_retries)

    def search(
        self,
        keyword: str,
        limit: int = 10,
        region: str = "global",
    ) -> List[Dict]:
        """
        搜索聚合
        
        Args:
            keyword: 搜索关键词
            limit: 返回结果数量
            region: 搜索区域（global/cn）
        
        Returns:
            搜索结果列表 [{title, link, snippet, source}]
        """
        results = []
        
        # 1. 尝试主搜索引擎
        logger.info(f"使用主搜索引擎: {self.primary}")
        primary_engine = self.engines.get(self.primary)
        
        if primary_engine:
            headers = self.headers_pool.get_headers_for_site(self.primary)
            
            try:
                if self.primary == "bing":
                    primary_results = primary_engine.search(
                        keyword,
                        region=region,
                        limit=limit,
                        headers=headers,
                    )
                else:
                    primary_results = primary_engine.search(
                        keyword,
                        limit=limit,
                        headers=headers,
                    )
                
                results.extend(primary_results)
                logger.info(f"主引擎 {self.primary} 返回 {len(primary_results)} 条结果")
            except Exception as e:
                logger.error(f"主引擎 {self.primary} 失败: {e}")
        
        # 2. 如果主引擎失败或结果不足，尝试备用引擎
        if len(results) < limit:
            logger.info(f"主引擎结果不足 ({len(results)}/{limit})，尝试备用引擎")
            
            for fallback_engine_name in self.fallback:
                if len(results) >= limit:
                    break
                
                fallback_engine = self.engines.get(fallback_engine_name)
                if not fallback_engine:
                    continue
                
                headers = self.headers_pool.get_headers_for_site(fallback_engine_name)
                
                try:
                    fallback_results = fallback_engine.search(
                        keyword,
                        limit=limit - len(results),
                        headers=headers,
                    )
                    results.extend(fallback_results)
                    logger.info(f"备用引擎 {fallback_engine_name} 返回 {len(fallback_results)} 条结果")
                except Exception as e:
                    logger.error(f"备用引擎 {fallback_engine_name} 失败: {e}")
        
        # 3. 去重（基于link）
        unique_results = self._deduplicate(results)
        
        logger.info(f"搜索聚合完成: {len(unique_results)} 条结果")
        return unique_results[:limit]

    def search_cn(self, keyword: str, limit: int = 10) -> List[Dict]:
        """国内版搜索"""
        return self.search(keyword, limit=limit, region="cn")

    def search_global(self, keyword: str, limit: int = 10) -> List[Dict]:
        """国际版搜索"""
        return self.search(keyword, limit=limit, region="global")

    def _deduplicate(self, results: List[Dict]) -> List[Dict]:
        """
        去重（基于link）
        
        Args:
            results: 搜索结果列表
        
        Returns:
            去重后的结果列表
        """
        seen_links = set()
        unique_results = []
        
        for item in results:
            link = item.get("link", "")
            if link and link not in seen_links:
                seen_links.add(link)
                unique_results.append(item)
        
        return unique_results


if __name__ == "__main__":
    # 测试
    aggregator = SearchAggregator()
    results = aggregator.search_global("Python教程", limit=10)
    
    print(f"搜索结果 ({len(results)}条):")
    for i, item in enumerate(results, 1):
        print(f"{i}. {item['title']} [{item['source']}]")