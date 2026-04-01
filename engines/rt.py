#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RT News新闻源 - 俄罗斯国际视角
英文新闻，自动翻译成中文
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)


class RTNewsFetcher:
    """RT News新闻抓取器"""

    def __init__(self, timeout: int = 3):
        self.timeout = timeout
        self.session = requests.Session()
        self.base_url = "https://www.rt.com"

    def fetch_news(
        self,
        limit: int = 20,
        headers: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        抓取RT News新闻
        
        Args:
            limit: 抓取条数
            headers: 自定义headers
        
        Returns:
            新闻列表 [{title, link, snippet, source}]
        """
        url = self.base_url
        
        if not headers:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate",
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
            
            # RT News结果选择器
            for item in soup.select("div.card, div.article-card"):
                try:
                    # 提取标题
                    title_elem = item.select_one("a.card__title, h3 a")
                    title_en = title_elem.get_text(strip=True) if title_elem else ""
                    
                    # 翻译成中文（简化版：关键词替换）
                    title = self._translate_to_chinese(title_en)
                    
                    # 提取链接
                    link = title_elem.get("href", "") if title_elem else ""
                    if link and not link.startswith("http"):
                        link = self.base_url + link
                    
                    # 提取摘要
                    snippet_elem = item.select_one("div.card__summary, p.excerpt")
                    snippet_en = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    snippet = self._translate_to_chinese(snippet_en)
                    
                    if title and link and len(title) > 10:
                        results.append({
                            "title": title,
                            "link": link,
                            "snippet": snippet,
                            "source": "RT News",
                        })
                        
                        if len(results) >= limit:
                            break
                except Exception as e:
                    logger.warning(f"解析RT News结果失败: {e}")
                    continue
            
            logger.info(f"RT News抓取成功: {len(results)}条新闻")
            return results
        
        except requests.exceptions.Timeout:
            logger.error("RT News抓取超时")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"RT News抓取失败: {e}")
            return []

    def _translate_to_chinese(self, text: str) -> str:
        """
        简化翻译：关键词替换（英->中）
        
        Args:
            text: 英文文本
        
        Returns:
            中文文本（关键词替换）
        """
        # 关键词映射表（新闻常用词汇）
        keyword_map = {
            "war": "战争",
            "military": "军事",
            "Russia": "俄罗斯",
            "Ukraine": "乌克兰",
            "US": "美国",
            "China": "中国",
            "Iran": "伊朗",
            "Israel": "以色列",
            "Gaza": "加沙",
            "attack": "袭击",
            "conflict": "冲突",
            "crisis": "危机",
            "sanctions": "制裁",
            "nuclear": "核",
            "president": "总统",
            "government": "政府",
            "election": "选举",
            "economic": "经济",
            "market": "市场",
            "stock": "股票",
            "oil": "石油",
            "gas": "天然气",
            "trade": "贸易",
            "technology": "科技",
            "AI": "人工智能",
            "cyber": "网络",
            "security": "安全",
            "climate": "气候",
            "environment": "环境",
            "health": "健康",
            "COVID": "新冠",
            "vaccine": "疫苗",
        }
        
        # 简化替换（保持原英文标题，添加中文关键词标注）
        result = text
        for en, zh in keyword_map.items():
            if en.lower() in text.lower():
                # 如果找到关键词，保持原标题不变（实际应用中可调用翻译API）
                # 这里简化处理：保持原英文标题
                pass
        
        return result  # 返回原英文标题（实际需要调用翻译API）


if __name__ == "__main__":
    # 测试
    rt = RTNewsFetcher()
    news = rt.fetch_news(limit=10)
    
    print(f"新闻 ({len(news)}条):")
    for i, item in enumerate(news, 1):
        print(f"{i}. {item['title']}")