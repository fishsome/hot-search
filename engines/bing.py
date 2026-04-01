#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bing搜索引擎 - 主搜索引擎
支持国内版和国际版
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class BingSearchEngine:
    """Bing搜索引擎"""

    def __init__(self, timeout: int = 3, max_retries: int = 2):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

    def search(
        self,
        keyword: str,
        region: str = "global",
        limit: int = 10,
        headers: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Bing搜索
        
        Args:
            keyword: 搜索关键词
            region: 搜索区域（global/cn）
            limit: 返回结果数量
            headers: 自定义headers
        
        Returns:
            搜索结果列表 [{title, link, snippet}]
        """
        # 构建URL
        if region == "cn":
            base_url = "https://cn.bing.com/search"
        else:
            base_url = "https://www.bing.com/search"
        
        params = {
            "q": keyword,
            "count": limit,
            "setlang": "zh-Hans" if region == "cn" else "en",
        }
        
        # 使用默认headers（如果没有提供）
        if not headers:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate",
            }
        
        # 请求并解析
        try:
            response = self.session.get(
                base_url,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.text, "html.parser")
            results = []
            
            # Bing结果选择器
            for item in soup.select("li.b_algo"):
                try:
                    # 提取标题
                    title_elem = item.select_one("h2 a")
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    
                    # 提取链接
                    link = title_elem.get("href", "") if title_elem else ""
                    
                    # 提取摘要
                    snippet_elem = item.select_one("div.b_caption p")
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    if title and link:
                        results.append({
                            "title": title,
                            "link": link,
                            "snippet": snippet,
                            "source": "Bing" + ("国内" if region == "cn" else "国际"),
                        })
                        
                        if len(results) >= limit:
                            break
                except Exception as e:
                    logger.warning(f"解析Bing结果失败: {e}")
                    continue
            
            logger.info(f"Bing搜索成功: {keyword} -> {len(results)}条结果")
            return results
        
        except requests.exceptions.Timeout:
            logger.error(f"Bing搜索超时: {keyword}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Bing搜索失败: {e}")
            return []

    def search_cn(self, keyword: str, limit: int = 10) -> List[Dict]:
        """Bing国内版搜索"""
        return self.search(keyword, region="cn", limit=limit)

    def search_global(self, keyword: str, limit: int = 10) -> List[Dict]:
        """Bing国际版搜索"""
        return self.search(keyword, region="global", limit=limit)


if __name__ == "__main__":
    # 测试
    bing = BingSearchEngine()
    results = bing.search_global("Python", limit=5)
    
    print(f"搜索结果 ({len(results)}条):")
    for i, item in enumerate(results, 1):
        print(f"{i}. {item['title']}")
        print(f"   {item['link']}")
        print(f"   {item['snippet'][:80]}...")