# -*- coding: utf-8 -*-
"""
微博热搜引擎
数据源: https://s.weibo.com/top/summary
"""

import json
import re
import sys
import os
from typing import List, Dict

# 支持单独运行
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from engines.base import fetch_with_retry, get_random_ua
else:
    from .base import fetch_with_retry, get_random_ua


def get_weibo_hot(limit: int = 20) -> List[Dict]:
    """
    获取微博热搜榜 Top N
    
    Args:
        limit: 返回条数，默认 20
    
    Returns:
        [{"rank": 1, "title": "标题", "url": "链接", "hot": "热度"}]
    """
    url = "https://s.weibo.com/top/summary"
    
    headers = {
        "User-Agent": get_random_ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://s.weibo.com/",
        "Connection": "keep-alive",
        "Cookie": "SUB=_2AkMR5oacf8NxqwJRmPsXzGLgbItxyQzEieKl-2VYJRUxHRlYzx6ZqhERtRB6AoXV7wYlWfjdJq8XE9j-dJiKYvTzGLxM; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9W5CFgWJUvC-5YQ5bBFqNZKF",  # 模拟登录 Cookie
    }
    
    response = fetch_with_retry(url, headers=headers, timeout=5, retries=3)
    
    if not response:
        print("微博热搜: 请求失败")
        return []
    
    try:
        response.encoding = "utf-8"
        html = response.text
        
        results = []
        
        # 方法1: 解析 HTML 表格
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        
        # 微博热搜在表格中
        rows = soup.select("tbody tr")
        
        for row in rows[1:]:  # 跳过表头
            try:
                td_list = row.find_all("td")
                if len(td_list) < 3:
                    continue
                
                # 排名
                rank_td = td_list[0]
                rank = rank_td.get_text(strip=True)
                if not rank.isdigit():
                    rank = str(len(results) + 1)
                
                # 标题和链接
                title_td = td_list[1]
                link = title_td.find("a")
                if not link:
                    continue
                
                title = link.get_text(strip=True)
                href = link.get("href", "")
                
                # 补全链接
                if href.startswith("//"):
                    href = "https:" + href
                elif href.startswith("/"):
                    href = "https://s.weibo.com" + href
                
                # 热度
                hot_td = td_list[2] if len(td_list) > 2 else None
                hot = hot_td.get_text(strip=True) if hot_td else ""
                
                if title:
                    results.append({
                        "rank": int(rank) if rank.isdigit() else len(results) + 1,
                        "title": title,
                        "url": href,
                        "hot": hot,
                    })
                    
                    if len(results) >= limit:
                        break
                        
            except Exception as e:
                continue
        
        # 方法2: 尝试从 script 标签提取 JSON
        if not results:
            pattern = r'<script[^>]*>.*?var\s+data\s*=\s*(\[.*?\]);?\s*</script>'
            match = re.search(pattern, html, re.DOTALL)
            
            if match:
                try:
                    data = json.loads(match.group(1))
                    for i, item in enumerate(data[:limit], 1):
                        results.append({
                            "rank": i,
                            "title": item.get("word", item.get("title", "")),
                            "url": item.get("url", f"https://s.weibo.com/weibo?q={item.get('word', '')}"),
                            "hot": str(item.get("num", item.get("hot", ""))),
                        })
                except (json.JSONDecodeError, TypeError):
                    pass
        
        # 方法3: 尝试从API获取（备用）
        if not results:
            api_url = "https://weibo.com/ajax/side/hotSearch"
            api_headers = headers.copy()
            api_headers["X-Requested-With"] = "XMLHttpRequest"
            
            api_response = fetch_with_retry(api_url, headers=api_headers, timeout=5, retries=1)
            
            if api_response:
                try:
                    data = api_response.json()
                    if data.get("ok") == 1:
                        items = data.get("data", {}).get("realtime", [])
                        for i, item in enumerate(items[:limit], 1):
                            results.append({
                                "rank": i,
                                "title": item.get("word", ""),
                                "url": f"https://s.weibo.com/weibo?q={item.get('word', '')}",
                                "hot": str(item.get("num", "")),
                            })
                except (json.JSONDecodeError, KeyError):
                    pass
        
        if results:
            print(f"微博热搜: 成功获取 {len(results)} 条")
            return results[:limit]
        
        print("微博热搜: 解析失败，未找到数据")
        return []
        
    except Exception as e:
        print(f"微博热搜: 解析异常 - {str(e)[:100]}")
        return []


if __name__ == "__main__":
    # 测试
    data = get_weibo_hot(20)
    print(f"\n获取到 {len(data)} 条微博热搜:")
    for item in data[:10]:
        print(f"{item['rank']:2}. {item['title'][:30]:<30} 🔥{item['hot']}")