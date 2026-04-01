#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美联社新闻源 - 美国主流视角，权威新闻机构
英文新闻，自动翻译成中文（关键词替换）
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class APNewsFetcher:
    """美联社新闻抓取器"""

    def __init__(self, timeout: int = 3):
        self.timeout = timeout
        self.session = requests.Session()
        self.base_url = "https://apnews.com"

    def fetch_news(
        self,
        limit: int = 20,
        headers: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        抓取美联社新闻
        
        Args:
            limit: 抓取条数
            headers: 自定义headers
        
        Returns:
            新闻列表 [{title, link, snippet, source}]
        """
        url = self.base_url
        
        if not headers:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Accept-Encoding": "identity",  # 禁用 gzip，和旧版本一样
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        
        try:
            response = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            results = []
            
            # 美联社新闻结果选择器（使用和旧版本一样的工作选择器）
            for item in soup.select(".PagePromo-title a, h3 a"):
                try:
                    # 提取标题
                    title_en = item.get_text(strip=True)
                    title = title_en
                    
                    # 提取链接
                    link = item.get("href", "")
                    if link and not link.startswith("http"):
                        link = self.base_url + link
                    
                    # 提取摘要（从父元素或同级元素）
                    parent = item.find_parent()
                    snippet_elem = parent.select_one(".PagePromo-description, .excerpt") if parent else None
                    snippet_en = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    snippet = snippet_en
                    
                    if title and link and len(title) > 5:
                        # 过滤掉"Associated Press"等重复描述
                        if "Associated Press" not in title:
                            results.append({
                                "title": title,
                                "link": link,
                                "snippet": snippet,
                                "source": "美联社",
                            })
                        
                        if len(results) >= limit:
                            break
                except Exception as e:
                    logger.warning(f"解析美联社新闻结果失败: {e}")
                    continue
            
            logger.info(f"美联社新闻抓取成功: {len(results)}条新闻")
            return results
        
        except requests.exceptions.Timeout:
            logger.error("美联社新闻抓取超时")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"美联社新闻抓取失败: {e}")
            return []


if __name__ == "__main__":
    # 测试
    ap = APNewsFetcher()
    news = ap.fetch_news(limit=10)
    
    print(f"新闻 ({len(news)}条):")
    for i, item in enumerate(news, 1):
        print(f"{i}. {item['title']}")