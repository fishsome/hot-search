#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度搜索引擎 - 备用搜索引擎
国内主流搜索引擎，中文内容最强
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
from urllib.parse import quote_plus, urlparse

logger = logging.getLogger(__name__)


class BaiduSearchEngine:
    """百度搜索引擎"""

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
        百度搜索
        
        Args:
            keyword: 搜索关键词
            limit: 返回结果数量
            headers: 自定义headers
        
        Returns:
            搜索结果列表 [{title, link, snippet}]
        """
        base_url = "https://www.baidu.com/s"
        
        params = {
            "wd": keyword,
            "rn": limit,
        }
        
        # 使用默认headers
        if not headers:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
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
            
            # 百度结果选择器
            for item in soup.select("div.result"):
                try:
                    # 提取标题
                    title_elem = item.select_one("h3 a")
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    
                    # 提取链接（百度链接需要跳转，提取真实URL）
                    baidu_link = title_elem.get("href", "") if title_elem else ""
                    link = self._extract_real_url(baidu_link)
                    
                    # 提取摘要
                    snippet_elem = item.select_one("div.c-abstract")
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    if title and link:
                        results.append({
                            "title": title,
                            "link": link,
                            "snippet": snippet,
                            "source": "百度",
                        })
                        
                        if len(results) >= limit:
                            break
                except Exception as e:
                    logger.warning(f"解析百度结果失败: {e}")
                    continue
            
            logger.info(f"百度搜索成功: {keyword} -> {len(results)}条结果")
            return results
        
        except requests.exceptions.Timeout:
            logger.error(f"百度搜索超时: {keyword}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"百度搜索失败: {e}")
            return []

    def _extract_real_url(self, baidu_link: str) -> str:
        """
        提取百度跳转链接的真实URL
        
        Args:
            baidu_link: 百度跳转链接
        
        Returns:
            真实URL
        """
        if not baidu_link:
            return ""
        
        # 如果已经是真实URL，直接返回
        if baidu_link.startswith("http") and "baidu.com" not in baidu_link:
            return baidu_link
        
        # 百度跳转链接格式：https://www.baidu.com/link?url=xxx
        # 需要访问该链接获取真实URL（简化处理，直接返回跳转链接）
        # 实际应用中可能需要二次请求获取真实URL
        
        try:
            # 尝试从URL参数中提取真实链接（某些情况下可用）
            parsed = urlparse(baidu_link)
            if "url" in parsed.query:
                # 简化：直接返回百度跳转链接（实际需要二次请求）
                return baidu_link
            return baidu_link
        except Exception:
            return baidu_link


if __name__ == "__main__":
    # 测试
    baidu = BaiduSearchEngine()
    results = baidu.search("Python", limit=5)
    
    print(f"搜索结果 ({len(results)}条):")
    for i, item in enumerate(results, 1):
        print(f"{i}. {item['title']}")