#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hot Search v2.0.0 - 全网热搜神器
统一入口：搜索 + 热搜榜 + URL 深度抓取

作者：FishSome | 邮箱：fishsomes@gmail.com
"""

import sys
import os
from typing import List, Dict, Optional

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入搜索模块（从原 hot_search.py）
from search_skill import SearchEngine as _SearchEngine

# 导入热搜引擎
from engines import get_baidu_hot, get_weibo_hot, get_zhihu_hot

# 导入 URL 抓取
from fetcher import scrape_url as _scrape_url


# ==================== 公开 API ====================

def search(keyword: str, engine: str = "all") -> List[Dict]:
    """
    全网搜索
    
    Args:
        keyword: 搜索关键词
        engine: 搜索引擎 ("all" | "bing_cn" | "bing_global" | "yandex" | "swisscows")
    
    Returns:
        [{"title": "标题", "link": "链接", "engine": "引擎名"}, ...]
    """
    se = _SearchEngine()
    
    if engine == "all":
        # 多引擎搜索
        results = []
        seen_links = set()
        raw = se.search_all(keyword)
        
        for eng, items in raw.items():
            for item in items:
                link = item.get("link", "")
                if link and link not in seen_links:
                    seen_links.add(link)
                    results.append({
                        "title": item.get("title", ""),
                        "link": link,
                        "engine": eng,
                    })
        return results
    else:
        # 单引擎搜索
        items = se.search(keyword, engine)
        return [
            {"title": item.get("title", ""), "link": item.get("link", ""), "engine": engine}
            for item in items
        ]


def get_hot(platform: str = "all") -> Dict[str, List[Dict]]:
    """
    获取热搜榜
    
    Args:
        platform: 平台名称 ("all" | "baidu" | "weibo" | "zhihu")
    
    Returns:
        {
            "baidu": [{"rank": 1, "title": "标题", "url": "链接", "hot": "热度"}, ...],
            "weibo": [...],
            "zhihu": [...]
        }
    """
    results = {}
    
    if platform in ("all", "baidu"):
        try:
            results["baidu"] = get_baidu_hot(20)
        except Exception as e:
            results["baidu"] = []
            print(f"百度热搜获取失败: {e}")
    
    if platform in ("all", "weibo"):
        try:
            results["weibo"] = get_weibo_hot(20)
        except Exception as e:
            results["weibo"] = []
            print(f"微博热搜获取失败: {e}")
    
    if platform in ("all", "zhihu"):
        try:
            results["zhihu"] = get_zhihu_hot(20)
        except Exception as e:
            results["zhihu"] = []
            print(f"知乎热搜获取失败: {e}")
    
    return results


def scrape_url(url: str) -> Dict:
    """
    URL 深度抓取，返回 Markdown + JSON
    
    Args:
        url: 目标 URL
    
    Returns:
        {
            "title": "标题",
            "content": "正文（Markdown）",
            "content_html": "正文（HTML）",
            "summary": "摘要",
            "keywords": ["关键词"],
            "metadata": {...},
            "error": None 或 "错误信息"
        }
    """
    return _scrape_url(url)


# ==================== 命令行入口 ====================

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("Hot Search v2.0.0 - 全网热搜神器")
        print()
        print("用法:")
        print("  python hot_search.py search <关键词> [引擎]")
        print("  python hot_search.py hot [平台]")
        print("  python hot_search.py scrape <URL>")
        print()
        print("命令:")
        print("  search  全网搜索（引擎: all/bing_cn/bing_global/yandex/swisscows）")
        print("  hot     获取热搜榜（平台: all/baidu/weibo/zhihu）")
        print("  scrape  URL 深度抓取，输出 Markdown")
        print()
        print("示例:")
        print("  python hot_search.py search 张雪机车夺冠")
        print("  python hot_search.py search 原油价格 bing_global")
        print("  python hot_search.py hot baidu")
        print("  python hot_search.py scrape https://news.sina.com.cn/xxx")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "search":
        keyword = sys.argv[2] if len(sys.argv) > 2 else ""
        engine = sys.argv[3] if len(sys.argv) > 3 else "all"
        
        if not keyword:
            print("错误: 请提供搜索关键词")
            sys.exit(1)
        
        print(f"\n【搜索】{keyword}（引擎: {engine}）\n")
        results = search(keyword, engine)
        
        if not results:
            print("未找到结果")
        else:
            for i, r in enumerate(results[:20], 1):
                print(f"{i:2}. [{r['engine']}] {r['title'][:50]}")
                print(f"    {r['link']}")
        
        print(f"\n共 {len(results)} 条结果")
    
    elif cmd == "hot":
        platform = sys.argv[2] if len(sys.argv) > 2 else "all"
        
        print(f"\n【热搜榜】{platform}\n")
        results = get_hot(platform)
        
        for plat, items in results.items():
            if items:
                print(f"\n{'='*50}")
                print(f"📱 {plat.upper()} 热搜榜")
                print('='*50)
                for item in items[:10]:
                    title = item.get("title", "")[:35]
                    hot = item.get("hot", "")
                    hot_str = f" 🔥{hot}" if hot else ""
                    print(f"{item.get('rank', '?'):2}. {title}{hot_str}")
            else:
                print(f"\n{plat}: 暂无数据")
    
    elif cmd == "scrape":
        url = sys.argv[2] if len(sys.argv) > 2 else ""
        
        if not url:
            print("错误: 请提供 URL")
            sys.exit(1)
        
        print(f"\n【抓取】{url}\n")
        result = scrape_url(url)
        
        if result.get("error"):
            print(f"错误: {result['error']}")
        else:
            print(f"标题: {result.get('title', '无标题')}")
            print(f"关键词: {', '.join(result.get('keywords', [])) or '无'}")
            print()
            print("-" * 50)
            print("正文:")
            print("-" * 50)
            content = result.get("content", "")
            if content:
                # 限制输出长度
                if len(content) > 3000:
                    print(content[:3000])
                    print("\n... (内容过长，已截断)")
                else:
                    print(content)
            else:
                print("未能提取正文")
    
    else:
        print(f"未知命令: {cmd}")
        print("可用命令: search, hot, scrape")
        sys.exit(1)


if __name__ == "__main__":
    main()