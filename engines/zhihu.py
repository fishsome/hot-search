# -*- coding: utf-8 -*-
"""
知乎热榜引擎
数据源: 
1. 知乎热搜词 API (无需登录): https://www.zhihu.com/api/v4/search/top_search
2. 备用: 热榜 API (需要登录)
"""

import json
import sys
import os
import requests
from typing import List, Dict

# 支持单独运行
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from engines.base import fetch_with_retry, get_random_ua
else:
    from .base import fetch_with_retry, get_random_ua


def _create_zhihu_session() -> requests.Session:
    """创建知乎 Session 并获取必要的 Cookie"""
    session = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
    }
    
    # 访问首页获取 Cookie
    try:
        session.get("https://www.zhihu.com/", headers=headers, timeout=3)
    except Exception:
        pass
    
    return session


def get_zhihu_hot(limit: int = 20) -> List[Dict]:
    """
    获取知乎热榜 Top N
    
    Args:
        limit: 返回条数，默认 20（知乎热搜 API 最多返回 10 条）
    
    Returns:
        [{"rank": 1, "title": "标题", "url": "链接", "hot": "热度"}]
    """
    # 方案 1: 使用知乎热搜词 API（无需登录）
    results = _get_zhihu_top_search(limit)
    if results:
        return results
    
    # 方案 2: 尝试热榜 API（可能需要登录）
    results = _get_zhihu_hot_from_api(limit)
    if results:
        return results
    
    # 方案 3: HTML 解析（备用）
    return _get_zhihu_hot_from_html(limit)


def _get_zhihu_top_search(limit: int) -> List[Dict]:
    """从知乎热搜词 API 获取数据（无需登录）"""
    session = _create_zhihu_session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": "https://www.zhihu.com/",
        "Origin": "https://www.zhihu.com",
    }
    
    try:
        response = session.get(
            "https://www.zhihu.com/api/v4/search/top_search",
            headers=headers,
            timeout=3
        )
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        words = data.get("top_search", {}).get("words", [])
        
        results = []
        for i, item in enumerate(words[:limit], 1):
            title = item.get("display_query") or item.get("query", "")
            if not title:
                continue
            
            # 构造搜索链接
            url = f"https://www.zhihu.com/search?q={title}"
            
            results.append({
                "rank": i,
                "title": title,
                "url": url,
                "hot": "",  # 热搜 API 不提供热度
            })
        
        if results:
            print(f"知乎热搜: 成功获取 {len(results)} 条")
            return results
        
    except Exception as e:
        print(f"知乎热搜: 获取失败 - {str(e)[:50]}")
    
    return []


def _get_zhihu_hot_from_api(limit: int) -> List[Dict]:
    """从知乎热榜 API 获取数据（需要登录态）"""
    session = _create_zhihu_session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.zhihu.com/",
        "Origin": "https://www.zhihu.com",
        "x-xsrftoken": session.cookies.get("_xsrf", ""),
    }
    
    try:
        response = session.get(
            "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total",
            headers=headers,
            timeout=3
        )
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        items = data.get("data", [])
        
        results = []
        for i, item in enumerate(items[:limit], 1):
            target = item.get("target", {}) or item.get("children", [{}])[0] if item.get("children") else {}
            
            title = target.get("title", "") or item.get("title", "")
            url = target.get("url", "")
            
            if not url:
                question_id = target.get("id", "")
                if question_id:
                    url = f"https://www.zhihu.com/question/{question_id}"
            
            hot = item.get("detail_text", "") or str(item.get("hot", "")) or str(item.get("heat", ""))
            
            if title:
                results.append({
                    "rank": i,
                    "title": title,
                    "url": url,
                    "hot": hot,
                })
        
        if results:
            print(f"知乎热榜: 成功获取 {len(results)} 条")
            return results
        
    except Exception as e:
        print(f"知乎热榜 API: 获取失败 - {str(e)[:50]}")
    
    return []


def _get_zhihu_hot_from_html(limit: int = 20) -> List[Dict]:
    """
    从 HTML 页面解析知乎热榜（备用方案）
    注意: 知乎对匿名访问有严格限制，此方案可能失败
    """
    session = _create_zhihu_session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": "https://www.zhihu.com/",
    }
    
    try:
        response = session.get("https://www.zhihu.com/hot", headers=headers, timeout=5)
        
        if response.status_code != 200:
            print(f"知乎热榜: HTML 请求失败 (状态码: {response.status_code})")
            return []
        
        import re
        from bs4 import BeautifulSoup
        
        html = response.text
        results = []
        
        # 方法1: 从 script 标签提取初始状态
        pattern = r'<script[^>]*id="js-initialData"[^>]*>(.*?)</script>'
        match = re.search(pattern, html, re.DOTALL)
        
        if match:
            try:
                initial_data = json.loads(match.group(1))
                hot_list = (
                    initial_data.get("initialState", {})
                    .get("hotList", {})
                    .get("data", [])
                )
                
                for i, item in enumerate(hot_list[:limit], 1):
                    target = item.get("target", {})
                    
                    title = target.get("title", "")
                    question_id = target.get("id", "")
                    url = f"https://www.zhihu.com/question/{question_id}" if question_id else ""
                    hot = str(item.get("detailText", ""))
                    
                    if title:
                        results.append({
                            "rank": i,
                            "title": title,
                            "url": url,
                            "hot": hot,
                        })
                        
            except (json.JSONDecodeError, KeyError) as e:
                print(f"知乎热榜: initialData 解析失败 - {str(e)[:50]}")
        
        # 方法2: 解析 HTML 元素
        if not results:
            soup = BeautifulSoup(html, "html.parser")
            items = soup.select(".HotList-item")[:limit]
            
            for i, item in enumerate(items, 1):
                title_elem = item.select_one(".HotList-item-title")
                hot_elem = item.select_one(".HotList-item-metrics")
                link_elem = item.find("a")
                
                title = title_elem.get_text(strip=True) if title_elem else ""
                hot = hot_elem.get_text(strip=True) if hot_elem else ""
                href = link_elem.get("href", "") if link_elem else ""
                
                # 补全链接
                if href.startswith("//"):
                    href = "https:" + href
                elif href.startswith("/"):
                    href = "https://www.zhihu.com" + href
                
                if title:
                    results.append({
                        "rank": i,
                        "title": title,
                        "url": href,
                        "hot": hot,
                    })
        
        if results:
            print(f"知乎热榜: HTML 解析成功获取 {len(results)} 条")
            return results[:limit]
        
        print("知乎热榜: HTML 解析失败，未找到数据")
        return []
        
    except Exception as e:
        print(f"知乎热榜: HTML 解析异常 - {str(e)[:100]}")
        return []


if __name__ == "__main__":
    # 测试
    data = get_zhihu_hot(20)
    print(f"\n获取到 {len(data)} 条知乎热榜:")
    for item in data[:10]:
        print(f"{item['rank']:2}. {item['title'][:30]:<30} 🔥{item['hot']}")