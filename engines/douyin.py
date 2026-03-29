# -*- coding: utf-8 -*-
"""
抖音热点引擎
数据源: https://www.douyin.com/aweme/v1/web/hot/search/list/
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


def get_douyin_hot(limit: int = 30) -> List[Dict]:
    """
    获取抖音热点榜 Top N
    
    Args:
        limit: 返回条数，默认 30
    
    Returns:
        [{"rank": 1, "title": "标题", "url": "链接", "hot": "热度"}]
    """
    url = "https://www.douyin.com/aweme/v1/web/hot/search/list/"
    
    headers = {
        "User-Agent": get_random_ua(),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.douyin.com/",
        "Origin": "https://www.douyin.com",
        "Connection": "keep-alive",
    }
    
    response = fetch_with_retry(url, headers=headers, timeout=10, retries=3)
    
    if not response:
        print("抖音热点: 请求失败")
        return []
    
    try:
        data = response.json()
        
        results = []
        
        # 解析热搜列表
        word_list = data.get("data", {}).get("word_list", [])
        
        if not word_list:
            # 尝试其他数据结构
            word_list = data.get("word_list", [])
        
        for item in word_list[:limit]:
            try:
                title = item.get("word", "")
                hot_value = item.get("hot_value", 0)
                # 构建搜索链接
                url = f"https://www.douyin.com/search/{title}"
                
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
            print(f"抖音热点: 成功获取 {len(results)} 条")
            return results
        
        print("抖音热点: 解析失败，未找到数据")
        return []
        
    except Exception as e:
        print(f"抖音热点: 解析异常 - {str(e)[:100]}")
        return []


if __name__ == "__main__":
    # 测试
    data = get_douyin_hot(30)
    print(f"\n获取到 {len(data)} 条抖音热点:")
    for item in data[:10]:
        print(f"{item['rank']:2}. {item['title'][:30]:<30} 🔥{item['hot']}")