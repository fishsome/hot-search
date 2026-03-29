# -*- coding: utf-8 -*-
"""
热点去重和聚类工具

功能：
1. 根据标题相似度去重
2. 按主题聚类
"""

from typing import List, Dict
from difflib import SequenceMatcher
import re


def similarity(a: str, b: str) -> float:
    """
    计算两个字符串的相似度
    
    Args:
        a: 字符串 A
        b: 字符串 B
    
    Returns:
        相似度 0.0 ~ 1.0
    """
    return SequenceMatcher(None, a, b).ratio()


def normalize_title(title: str) -> str:
    """
    标准化标题（去除标点、空格、统一大小写）
    
    Args:
        title: 原始标题
    
    Returns:
        标准化后的标题
    """
    # 去除特殊字符，只保留中文、英文、数字
    normalized = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', title)
    return normalized.lower()


def deduplicate_by_title(news_list: List[Dict], threshold: float = 0.8) -> List[Dict]:
    """
    根据标题相似度去重
    
    Args:
        news_list: 新闻列表，每个元素包含 {"rank", "title", "url", "hot"}
        threshold: 相似度阈值，默认 0.8（80%以上视为重复）
    
    Returns:
        去重后的新闻列表
    """
    if not news_list:
        return []
    
    unique = []
    seen_titles = []
    
    for item in news_list:
        title = item.get("title", "")
        if not title:
            continue
        
        # 标准化标题
        norm_title = normalize_title(title)
        
        # 检查是否与已存在的标题相似
        is_duplicate = False
        for seen in seen_titles:
            if similarity(norm_title, seen) >= threshold:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique.append(item)
            seen_titles.append(norm_title)
    
    # 重新排序
    for i, item in enumerate(unique, 1):
        item["rank"] = i
    
    return unique


def extract_keywords(title: str) -> List[str]:
    """
    从标题中提取关键词（简单实现）
    
    Args:
        title: 标题
    
    Returns:
        关键词列表
    """
    # 移除常见停用词
    stop_words = {
        "的", "了", "是", "在", "有", "和", "与", "或", "等", "中", "为",
        "对", "这", "那", "上", "下", "不", "也", "都", "而", "及", "以",
        "被", "将", "会", "能", "可", "应", "要", "会", "到", "从", "把"
    }
    
    # 简单分词（按空格和标点分割）
    words = re.split(r'[\s,，。！？、；：""''【】《》（）\-\|/\\]+', title)
    
    # 过滤停用词和短词
    keywords = []
    for w in words:
        w = w.strip()
        if len(w) >= 2 and w not in stop_words:
            keywords.append(w)
    
    return keywords


def cluster_by_topic(news_list: List[Dict]) -> Dict[str, List[Dict]]:
    """
    按主题聚类
    
    Args:
        news_list: 新闻列表
    
    Returns:
        {主题: [新闻列表]}
    """
    if not news_list:
        return {}
    
    # 定义主题关键词映射
    topic_keywords = {
        "娱乐": ["明星", "演员", "电影", "电视剧", "综艺", "歌手", "艺人", "娱乐圈", "红毯", "获奖"],
        "体育": ["比赛", "联赛", "球员", "世界杯", "奥运", "足球", "篮球", "网球", "冠军", "运动员"],
        "科技": ["AI", "人工智能", "芯片", "手机", "科技", "互联网", "软件", "华为", "苹果", "小米", "百度"],
        "财经": ["股票", "基金", "经济", "股市", "金融", "投资", "银行", "上市", "财报", "GDP"],
        "社会": ["警方", "法院", "判决", "案件", "调查", "通报", "事故", "灾难", "疫情"],
        "国际": ["美国", "中国", "日本", "韩国", "俄罗斯", "乌克兰", "战争", "外交", "总统"],
        "教育": ["高考", "大学", "学校", "教育", "招生", "考研", "学生", "老师"],
        "健康": ["疫情", "病毒", "医院", "疫苗", "健康", "医疗", "病例"],
        "汽车": ["汽车", "新能源", "电动车", "特斯拉", "比亚迪", "驾照", "交通"],
        "房产": ["房价", "楼市", "房地产", "买房", "租房", "物业"],
    }
    
    clusters = {topic: [] for topic in topic_keywords}
    clusters["其他"] = []
    
    for item in news_list:
        title = item.get("title", "")
        matched = False
        
        # 检查每个主题的关键词
        for topic, keywords in topic_keywords.items():
            for kw in keywords:
                if kw in title:
                    clusters[topic].append(item)
                    matched = True
                    break
            if matched:
                break
        
        if not matched:
            clusters["其他"].append(item)
    
    # 移除空的分类
    return {k: v for k, v in clusters.items() if v}


if __name__ == "__main__":
    # 测试
    test_news = [
        {"rank": 1, "title": "某某明星官宣结婚", "url": "http://example.com/1", "hot": "100万"},
        {"rank": 2, "title": "某某明星官宣结婚（现场图）", "url": "http://example.com/2", "hot": "80万"},
        {"rank": 3, "title": "中国女排夺得世界杯冠军", "url": "http://example.com/3", "hot": "200万"},
        {"rank": 4, "title": "华为发布新款手机", "url": "http://example.com/4", "hot": "150万"},
        {"rank": 5, "title": "股市大跌原因分析", "url": "http://example.com/5", "hot": "50万"},
    ]
    
    print("原始数据:", len(test_news), "条")
    
    # 去重
    unique = deduplicate_by_title(test_news)
    print("去重后:", len(unique), "条")
    for item in unique:
        print(f"  {item['rank']}. {item['title']}")
    
    # 聚类
    print("\n聚类结果:")
    clusters = cluster_by_topic(unique)
    for topic, items in clusters.items():
        print(f"  [{topic}]: {len(items)} 条")
        for item in items:
            print(f"    - {item['title']}")