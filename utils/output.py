# -*- coding: utf-8 -*-
"""
热点输出格式化工具

功能：
1. 输出 Markdown 格式
2. 输出 JSON 格式（LLM 友好）
"""

import json
from typing import List, Dict
from datetime import datetime


def to_markdown(news_list: List[Dict], title: str = "热搜榜", show_source: bool = False) -> str:
    """
    输出 Markdown 格式
    
    Args:
        news_list: 新闻列表
        title: 标题
        show_source: 是否显示来源
    
    Returns:
        Markdown 格式字符串
    """
    if not news_list:
        return f"# {title}\n\n暂无数据"
    
    lines = []
    lines.append(f"# {title}")
    lines.append(f"\n> 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    
    for item in news_list:
        rank = item.get("rank", "")
        title_text = item.get("title", "")
        url = item.get("url", "")
        hot = item.get("hot", "")
        source = item.get("source", "")
        
        # 格式化热度
        hot_str = f" 🔥{hot}" if hot else ""
        
        # 格式化来源
        source_str = f" [{source}]" if show_source and source else ""
        
        # 生成行
        if url:
            line = f"{rank}. [{title_text}]({url}){hot_str}{source_str}"
        else:
            line = f"{rank}. {title_text}{hot_str}{source_str}"
        
        lines.append(line)
    
    return "\n".join(lines)


def to_json(news_list: List[Dict], indent: int = 2) -> str:
    """
    输出 JSON 格式（LLM 友好）
    
    Args:
        news_list: 新闻列表
        indent: 缩进空格数
    
    Returns:
        JSON 格式字符串
    """
    if not news_list:
        return json.dumps({"count": 0, "data": []}, ensure_ascii=False, indent=indent)
    
    # 标准化数据结构
    result = {
        "count": len(news_list),
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "data": []
    }
    
    for item in news_list:
        data_item = {
            "rank": item.get("rank", 0),
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "hot": item.get("hot", ""),
        }
        
        # 可选字段
        if "source" in item:
            data_item["source"] = item["source"]
        if "cluster" in item:
            data_item["cluster"] = item["cluster"]
        if "keywords" in item:
            data_item["keywords"] = item["keywords"]
        
        result["data"].append(data_item)
    
    return json.dumps(result, ensure_ascii=False, indent=indent)


def to_table(news_list: List[Dict]) -> str:
    """
    输出表格格式
    
    Args:
        news_list: 新闻列表
    
    Returns:
        表格格式字符串
    """
    if not news_list:
        return "暂无数据"
    
    lines = []
    lines.append("| 排名 | 标题 | 热度 |")
    lines.append("|:----:|:-----|-----:|")
    
    for item in news_list:
        rank = item.get("rank", "")
        title = item.get("title", "")
        hot = item.get("hot", "-")
        
        # 截断长标题
        if len(title) > 30:
            title = title[:30] + "..."
        
        lines.append(f"| {rank} | {title} | {hot} |")
    
    return "\n".join(lines)


def to_simple_list(news_list: List[Dict]) -> str:
    """
    输出简单列表格式
    
    Args:
        news_list: 新闻列表
    
    Returns:
        简单列表字符串
    """
    if not news_list:
        return "暂无数据"
    
    lines = []
    for item in news_list:
        rank = item.get("rank", "")
        title = item.get("title", "")
        hot = item.get("hot", "")
        
        hot_str = f" 🔥{hot}" if hot else ""
        lines.append(f"{rank}. {title}{hot_str}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    test_news = [
        {"rank": 1, "title": "某某明星官宣结婚", "url": "http://example.com/1", "hot": "100万", "source": "微博"},
        {"rank": 2, "title": "中国女排夺得世界杯冠军", "url": "http://example.com/2", "hot": "200万", "source": "百度"},
        {"rank": 3, "title": "华为发布新款手机", "url": "http://example.com/3", "hot": "150万", "source": "微博"},
    ]
    
    print("=== Markdown 格式 ===")
    print(to_markdown(test_news, "热搜榜", show_source=True))
    
    print("\n=== JSON 格式 ===")
    print(to_json(test_news))
    
    print("\n=== 表格格式 ===")
    print(to_table(test_news))
    
    print("\n=== 简单列表格式 ===")
    print(to_simple_list(test_news))