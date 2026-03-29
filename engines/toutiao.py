# -*- coding: utf-8 -*-
"""
今日头条热搜引擎
数据源: https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc
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


def get_toutiao_hot(limit: int = 30) -> List[Dict]:
    """
    获取今日头条热点榜 Top N
    
    Args:
        limit: 返回条数，默认 30
    
    Returns:
        [{"rank": 1, "title": "标题", "url": "链接", "hot": "热度"}]
    """
    url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
    
    headers = {
        "User-Agent": get_random_ua(),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.toutiao.com/",
        "Origin": "https://www.toutiao.com",
        "Connection": "keep-alive",
    }
    
    response = fetch_with_retry(url, headers=headers, timeout=10, retries=3)
    
    if not response:
        print("今日头条: 请求失败")
        return []
    
    try:
        data = response.json()
        
        results = []
        
        # 解析热搜列表
        hot_list = data.get("data", [])
        
        for item in hot_list[:limit]:
            try:
                title = item.get("Title", "")
                hot_value = item.get("HotValue", 0)
                # 使用提供的 URL 或构建搜索链接
                url = item.get("Url", "")
                if not url:
                    url = f"https://www.toutiao.com/search?keyword={title}"
                
                if title:
                    results.append({
                        "rank": len(results) + 1,
                        "title": title,
                        "url": url,
                        "hot": str(hot_value),
                    })
            except Exception as e:
                continue
        
        if results:
            print(f"今日头条: 成功获取 {len(results)} 条")
            return results
        
        print("今日头条: 解析失败，未找到数据")
        return []
        
    except Exception as e:
        print(f"今日头条: 解析异常 - {str(e)[:100]}")
        return []


if __name__ == "__main__":
    # 测试
    data = get_toutiao_hot(30)
    print(f"\n获取到 {len(data)} 条今日头条热搜:")
    for item in data[:10]:
        print(f"{item['rank']:2}. {item['title'][:30]:<30} 🔥{item['hot']}")