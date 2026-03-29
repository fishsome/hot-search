# -*- coding: utf-8 -*-
"""
百度热搜引擎
数据源: https://top.baidu.com/board?tab=realtime
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


def get_baidu_hot(limit: int = 20) -> List[Dict]:
    """
    获取百度热搜榜 Top N
    
    Args:
        limit: 返回条数，默认 20
    
    Returns:
        [{"rank": 1, "title": "标题", "url": "链接", "hot": "热度"}]
    """
    url = "https://top.baidu.com/board?tab=realtime"
    
    headers = {
        "User-Agent": get_random_ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        # "Accept-Encoding": "gzip, deflate, br",  # 让 requests 自动处理
        "Referer": "https://www.baidu.com/",
        "Connection": "keep-alive",
    }
    
    response = fetch_with_retry(url, headers=headers, timeout=10, retries=3)
    
    print(f"百度热搜: 请求状态 = {response is not None}")
    
    if not response:
        print("百度热搜: 请求失败")
        return []
    
    print(f"百度热搜: HTTP {response.status_code}, 内容长度 {len(response.text)}")
    
    try:
        response.encoding = "utf-8"
        html = response.text
        
        # 百度热搜数据嵌入在 <script> 标签中
        # 格式: <!--s-data:{"data":{"cards":[...]}}-->
        # 或者: window.__INITIAL_STATE__ = {...}
        
        results = []
        
        # 方法1: 尝试从 <!--s-data: 中提取
        pattern = r'<!--s-data:(.*?)-->'
        match = re.search(pattern, html, re.DOTALL)
        
        if match:
            try:
                data = json.loads(match.group(1))
                cards = data.get("data", {}).get("cards", [])
                
                for card in cards:
                    # cardType 可能是 None，直接取 content
                    content = card.get("content", [])
                    for item in content:
                        # 只跳过置顶标记的
                        if item.get("isTop"):
                            continue
                        
                        title = item.get("word", "")
                        url = item.get("rawUrl", "") or item.get("url", "")
                        hot = str(item.get("hotScore", ""))
                        
                        if title:
                            results.append({
                                "rank": len(results) + 1,
                                "title": title,
                                "url": url,
                                "hot": hot,
                            })
                            if len(results) >= limit:
                                break
                    
                    if len(results) >= limit:
                        break
            except json.JSONDecodeError:
                pass
        
        # 方法2: 尝试从 window.__INITIAL_STATE__ 提取
        if not results:
            pattern = r'window\.__INITIAL_STATE__\s*=\s*({.*?});?\s*</script>'
            match = re.search(pattern, html, re.DOTALL)
            
            if match:
                try:
                    # 清理 JSON 字符串
                    json_str = match.group(1)
                    data = json.loads(json_str)
                    
                    # 遍历可能的数据结构
                    if "data" in data:
                        content = data["data"].get("content", [])
                        for i, item in enumerate(content[:limit], 1):
                            results.append({
                                "rank": i,
                                "title": item.get("word", item.get("title", "")),
                                "url": item.get("url", item.get("rawUrl", "")),
                                "hot": item.get("hotScore", item.get("hot", "")),
                            })
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # 方法3: 解析 HTML 元素（备用）
        if not results:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            
            items = soup.select(".category-wrap_iLKoo .content_1YWBm")[:limit]
            for i, item in enumerate(items, 1):
                title_elem = item.select_one(".title_dIF3B")
                hot_elem = item.select_one(".hot-index_1Bl1a")
                link_elem = item.find("a")
                
                title = title_elem.get_text(strip=True) if title_elem else ""
                hot = hot_elem.get_text(strip=True) if hot_elem else ""
                url = link_elem.get("href", "") if link_elem else ""
                
                if title:
                    results.append({
                        "rank": i,
                        "title": title,
                        "url": url,
                        "hot": hot,
                    })
        
        if results:
            print(f"百度热搜: 成功获取 {len(results)} 条")
            return results[:limit]
        
        print("百度热搜: 解析失败，未找到数据")
        return []
        
    except Exception as e:
        print(f"百度热搜: 解析异常 - {str(e)[:100]}")
        return []


if __name__ == "__main__":
    # 测试
    data = get_baidu_hot(20)
    print(f"\n获取到 {len(data)} 条百度热搜:")
    for item in data[:10]:
        print(f"{item['rank']:2}. {item['title'][:30]:<30} 🔥{item['hot']}")