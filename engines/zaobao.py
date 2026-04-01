#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
联合早报新闻源 - 东南亚权威华人媒体
复用旧版本的选择器逻辑
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# 新闻源配置（复用旧版本）
NEWS_SOURCE = {
    "name": "联合早报",
    "url": "https://www.zaobao.com",
    "selectors": {
        "title": "h3 a, .article-title a",
        "link": "h3 a, .article-title a",
        "snippet": ".article-summary, .excerpt"
    }
}


class ZaobaoNewsFetcher:
    """联合早报新闻抓取器"""

    def __init__(self, timeout: int = 3):
        self.timeout = timeout
        self.session = requests.Session()
        self.config = NEWS_SOURCE

    def fetch_news(
        self,
        limit: int = 20,
        headers: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        抓取联合早报新闻（复用旧版本逻辑）
        
        Args:
            limit: 抓取条数
            headers: 自定义headers
        
        Returns:
            新闻列表 [{title, link, snippet, source}]
        """
        # 使用旧版本的 headers（禁用 gzip）
        if not headers:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                "Accept-Encoding": "identity",  # 禁用 gzip，关键！
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        
        try:
            response = self.session.get(
                self.config["url"],
                headers=headers,
                timeout=self.timeout,
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                results = []
                
                # 使用旧版本的选择器
                for item in soup.select(self.config["selectors"]["title"]):
                    try:
                        title = item.get_text(strip=True)
                        link = item.get("href", "")
                        
                        if link and not link.startswith("http"):
                            link = self.config["url"] + link
                        
                        # 简化：snippet 留空
                        snippet = ""
                        
                        if title and link and len(title) > 10:
                            results.append({
                                "title": title,
                                "link": link,
                                "snippet": snippet,
                                "source": self.config["name"],
                            })
                            
                            if len(results) >= limit:
                                break
                    except Exception as e:
                        logger.warning(f"解析联合早报结果失败: {e}")
                        continue
                
                logger.info(f"联合早报抓取成功: {len(results)}条新闻")
                return results
            
            logger.error(f"联合早报HTTP错误: {response.status_code}")
            return []
        
        except requests.exceptions.Timeout:
            logger.error("联合早报抓取超时")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"联合早报抓取失败: {e}")
            return []


if __name__ == "__main__":
    # 测试
    zaobao = ZaobaoNewsFetcher()
    news = zaobao.fetch_news(limit=10)
    
    print(f"新闻 ({len(news)}条):")
    for i, item in enumerate(news, 1):
        print(f"{i}. {item['title']}")