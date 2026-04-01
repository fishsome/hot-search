#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sougou搜索引擎 - 备用搜索引擎
国内搜索引擎，中文内容友好
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class SougouSearchEngine:
    """Sougou搜索引擎"""

    def __init__(self, timeout: int = 3, max_retries: int = 2):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

    def search(
        self,
        keyword: str,
        limit: int = 10,
        headers: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Sougou搜索
        
        Args:
            keyword: 搜索关键词
            limit: 返回结果数量
            headers: 自定义headers
        
        Returns:
            搜索结果列表 [{title, link, snippet}]
        """
        base_url = "https://www.sogou.com/web"
        
        params = {
            "query": keyword,
            "num": limit,
        }
        
        # 使用默认headers
        if not headers:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Accept-Encoding": "gzip, deflate",
            }
        
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
            
            # Sougou结果选择器
            for item in soup.select("div.result"):
                try:
                    # 提取标题
                    title_elem = item.select_one("h3 a")
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    
                    # 提取链接
                    link = title_elem.get("href", "") if title_elem else ""
                    
                    # 提取摘要
                    snippet_elem = item.select_one("p.str-text-info")
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    if title and link:
                        results.append({
                            "title": title,
                            "link": link,
                            "snippet": snippet,
                            "source": "Sougou",
                        })
                        
                        if len(results) >= limit:
                            break
                except Exception as e:
                    logger.warning(f"解析Sougou结果失败: {e}")
                    continue
            
            logger.info(f"Sougou搜索成功: {keyword} -> {len(results)}条结果")
            return results
        
        except requests.exceptions.Timeout:
            logger.error(f"Sougou搜索超时: {keyword}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Sougou搜索失败: {e}")
            return []


if __name__ == "__main__":
    # 测试
    sougou = SougouSearchEngine()
    results = sougou.search("Python", limit=5)
    
    print(f"搜索结果 ({len(results)}条):")
    for i, item in enumerate(results, 1):
        print(f"{i}. {item['title']}")