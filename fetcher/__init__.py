#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hot Search v2.0 - 抓取模块
"""

from .article import scrape_url, scrape_urls, ArticleFetcher, ContentExtractor
from .batch import BatchScraper, rate_limit, scrape_urls_batch, scrape_hot_with_details
from .sitemap import discover_sitemap, crawl_sitemap, SitemapCrawler, get_sitemap_urls

__all__ = [
    # 文章抓取
    "scrape_url",
    "scrape_urls",
    "ArticleFetcher",
    "ContentExtractor",
    # 批量抓取
    "BatchScraper",
    "rate_limit",
    "scrape_urls_batch",
    "scrape_hot_with_details",
    # 站点地图
    "discover_sitemap",
    "crawl_sitemap",
    "SitemapCrawler",
    "get_sitemap_urls",
]