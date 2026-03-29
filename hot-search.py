#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hot Search V2.2 - OpenClaw 适配版
统一调用入口 + 自然语言指令解析 + AI Agent 异步适配

作者：FishSome | 邮箱：fishsomes@gmail.com
版本：2.2.0 | 日期：2026-03-30

严格按飞书文档规范开发：
https://pcn1ryh3sn1i.feishu.cn/docx/C2TMdhRizoOoq9xkihycyks4nfd
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入核心模块
from search_skill import SearchEngine
from engines import get_baidu_hot, get_weibo_hot, get_zhihu_hot
from fetcher import scrape_url

# ==================== 配置 ====================

VERSION = "2.2.0"
TIMEOUT_SINGLE = 2  # 单引擎超时（秒）
TIMEOUT_TOTAL = 10  # 总超时（秒）
MAX_RESULTS = 50  # 最大结果数

# 自然语言指令映射
NATURAL_LANGUAGE_COMMANDS = {
    "今日全网热点": "hot all",
    "今日热点": "hot all",
    "抓取微博第一条热搜详情": "hot weibo --detail",
    "微博热搜": "hot weibo",
    "百度热搜": "hot baidu",
    "知乎热榜": "hot zhihu",
    "监控科技类热点": "monitor 科技 5000",
    "监控股票热点": "monitor 股票 10000",
    "搜索张雪机车夺冠新闻": "search 张雪机车夺冠",
    "查看昨天百度热搜": "history baidu yesterday",
    "昨天热搜": "history all yesterday",
}

# ==================== 核心功能函数 ====================

def get_hot(platform: str = "all", detail: bool = False) -> Dict[str, Any]:
    """
    获取热搜榜
    
    Args:
        platform: 平台名称 ("all" | "baidu" | "weibo" | "zhihu")
        detail: 是否获取详情
    
    Returns:
        {
            "success": True,
            "platform": "weibo",
            "count": 20,
            "data": [{"rank": 1, "title": "标题", "url": "链接", "hot": "热度"}, ...],
            "timestamp": "2026-03-30 01:38:00",
            "error": None
        }
    """
    result = {
        "success": True,
        "platform": platform,
        "count": 0,
        "data": {},
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "error": None
    }
    
    failed_platforms = []
    
    if platform in ("all", "baidu"):
        try:
            data = get_baidu_hot(20)
            if data:
                result["data"]["baidu"] = data
            else:
                failed_platforms.append("baidu")
        except Exception as e:
            failed_platforms.append(f"baidu: {str(e)}")
    
    if platform in ("all", "weibo"):
        try:
            data = get_weibo_hot(20)
            if data:
                result["data"]["weibo"] = data
            else:
                failed_platforms.append("weibo")
        except Exception as e:
            failed_platforms.append(f"weibo: {str(e)}")
    
    if platform in ("all", "zhihu"):
        try:
            data = get_zhihu_hot(20)
            if data:
                result["data"]["zhihu"] = data
            else:
                failed_platforms.append("zhihu")
        except Exception as e:
            failed_platforms.append(f"zhihu: {str(e)}")
    
    # 计算总数
    result["count"] = sum(len(items) for items in result["data"].values())
    
    # 记录失败
    if failed_platforms:
        result["failed_platforms"] = failed_platforms
    
    return result


def search(keyword: str, engine: str = "all") -> Dict[str, Any]:
    """
    关键词搜索
    
    Args:
        keyword: 搜索关键词
        engine: 搜索引擎 ("all" | "bing_cn" | "bing_global" | "yandex" | "swisscows" | "trading_economics")
    
    Returns:
        {
            "success": True,
            "keyword": "关键词",
            "engine": "all",
            "count": 30,
            "data": [{"title": "标题", "link": "链接", "engine": "引擎名"}, ...],
            "timestamp": "2026-03-30 01:38:00",
            "error": None
        }
    """
    result = {
        "success": True,
        "keyword": keyword,
        "engine": engine,
        "count": 0,
        "data": [],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "error": None
    }
    
    if not keyword:
        result["success"] = False
        result["error"] = "关键词不能为空"
        return result
    
    try:
        se = SearchEngine(timeout=TIMEOUT_SINGLE)
        
        if engine == "all":
            # 多引擎搜索
            raw = se.search_all(keyword)
            seen_links = set()
            
            for eng, items in raw.items():
                for item in items:
                    link = item.get("link", "")
                    if link and link not in seen_links:
                        seen_links.add(link)
                        result["data"].append({
                            "title": item.get("title", ""),
                            "link": link,
                            "engine": eng,
                            "snippet": item.get("snippet", "")[:200] if item.get("snippet") else ""
                        })
        else:
            # 单引擎搜索
            items = se.search(keyword, engine)
            for item in items:
                result["data"].append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "engine": engine,
                    "snippet": item.get("snippet", "")[:200] if item.get("snippet") else ""
                })
        
        result["count"] = len(result["data"])
        
        # 限制结果数
        if result["count"] > MAX_RESULTS:
            result["data"] = result["data"][:MAX_RESULTS]
            result["count"] = MAX_RESULTS
        
        # 记录失败引擎
        if hasattr(se, 'failed_engines') and se.failed_engines:
            result["failed_engines"] = se.failed_engines
            
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
    
    return result


def monitor(keyword: str, threshold: int = 10000) -> Dict[str, Any]:
    """
    热点监控
    
    Args:
        keyword: 监控关键词
        threshold: 热度阈值（超过此值触发告警）
    
    Returns:
        {
            "success": True,
            "keyword": "股票",
            "threshold": 10000,
            "alerts": [{"platform": "weibo", "title": "标题", "hot": "12000", "rank": 3}, ...],
            "alert_count": 2,
            "timestamp": "2026-03-30 01:38:00",
            "error": None
        }
    """
    result = {
        "success": True,
        "keyword": keyword,
        "threshold": threshold,
        "alerts": [],
        "alert_count": 0,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "error": None
    }
    
    if not keyword:
        result["success"] = False
        result["error"] = "监控关键词不能为空"
        return result
    
    try:
        # 获取全网热搜
        hot_data = get_hot("all")
        
        # 遍历查找匹配
        for platform, items in hot_data.get("data", {}).items():
            for item in items:
                title = item.get("title", "")
                hot_str = item.get("hot", "0")
                
                # 关键词匹配
                if keyword.lower() in title.lower():
                    # 解析热度值
                    try:
                        hot_val = int(hot_str.replace(",", "").replace("万", "0000"))
                    except:
                        hot_val = 0
                    
                    # 热度阈值检测
                    if hot_val >= threshold:
                        result["alerts"].append({
                            "platform": platform,
                            "title": title,
                            "hot": hot_str,
                            "hot_value": hot_val,
                            "rank": item.get("rank", 0),
                            "url": item.get("url", "")
                        })
        
        result["alert_count"] = len(result["alerts"])
        
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
    
    return result


def get_history(platform: str = "all", date: str = "today") -> Dict[str, Any]:
    """
    历史热搜查询
    
    Args:
        platform: 平台名称 ("all" | "baidu" | "weibo" | "zhihu")
        date: 日期 ("today" | "yesterday" | "YYYY-MM-DD")
    
    Returns:
        {
            "success": True,
            "platform": "baidu",
            "date": "2026-03-29",
            "data": {...},
            "timestamp": "2026-03-30 01:38:00",
            "error": None
        }
    """
    result = {
        "success": True,
        "platform": platform,
        "date": date,
        "data": {},
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "error": None
    }
    
    # 解析日期
    try:
        if date == "today":
            target_date = datetime.now()
        elif date == "yesterday":
            target_date = datetime.now() - timedelta(days=1)
        else:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        
        result["date"] = target_date.strftime("%Y-%m-%d")
    except:
        result["success"] = False
        result["error"] = f"日期格式错误: {date}，支持: today, yesterday, YYYY-MM-DD"
        return result
    
    # 历史数据存储路径
    history_dir = os.path.join(os.path.dirname(__file__), "history")
    history_file = os.path.join(history_dir, f"{result['date']}.json")
    
    # 尝试读取历史数据
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history_data = json.load(f)
            
            if platform == "all":
                result["data"] = history_data
            else:
                result["data"] = {platform: history_data.get(platform, [])}
                
        except Exception as e:
            result["success"] = False
            result["error"] = f"读取历史数据失败: {str(e)}"
    else:
        result["success"] = False
        result["error"] = f"暂无 {result['date']} 的历史数据"
        result["hint"] = "历史数据需要定时任务保存，请检查 monitor 配置"
    
    return result


def scrape(url: str) -> Dict[str, Any]:
    """
    URL 深度抓取
    
    Args:
        url: 目标 URL
    
    Returns:
        {
            "success": True,
            "url": "https://...",
            "title": "标题",
            "content": "正文（Markdown）",
            "keywords": ["关键词"],
            "timestamp": "2026-03-30 01:38:00",
            "error": None
        }
    """
    result = {
        "success": True,
        "url": url,
        "title": "",
        "content": "",
        "keywords": [],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "error": None
    }
    
    if not url:
        result["success"] = False
        result["error"] = "URL 不能为空"
        return result
    
    try:
        data = scrape_url(url)
        
        if data.get("error"):
            result["success"] = False
            result["error"] = data["error"]
        else:
            result["title"] = data.get("title", "")
            result["content"] = data.get("content", "")
            result["keywords"] = data.get("keywords", [])
            result["content_length"] = len(result["content"])
            
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
    
    return result


# ==================== 自然语言解析 ====================

def parse_natural_language(text: str) -> str:
    """
    解析自然语言指令，返回标准命令
    
    Args:
        text: 自然语言文本
    
    Returns:
        标准命令字符串
    """
    text = text.strip()
    
    # 精确匹配
    if text in NATURAL_LANGUAGE_COMMANDS:
        return NATURAL_LANGUAGE_COMMANDS[text]
    
    # 模糊匹配
    for nl_cmd, std_cmd in NATURAL_LANGUAGE_COMMANDS.items():
        if nl_cmd in text or text in nl_cmd:
            return std_cmd
    
    # 智能解析
    # "搜索 XXX" -> search XXX
    if text.startswith("搜索"):
        keyword = text[2:].strip()
        return f"search {keyword}"
    
    # "查询 XXX" -> search XXX
    if text.startswith("查询"):
        keyword = text[2:].strip()
        return f"search {keyword}"
    
    # "热搜" -> hot all
    if "热搜" in text or "热榜" in text:
        if "微博" in text:
            return "hot weibo"
        elif "百度" in text:
            return "hot baidu"
        elif "知乎" in text:
            return "hot zhihu"
        else:
            return "hot all"
    
    # "监控 XXX" -> monitor XXX
    if text.startswith("监控"):
        parts = text[2:].split()
        if len(parts) >= 2:
            keyword = parts[0]
            try:
                threshold = int(parts[1])
                return f"monitor {keyword} {threshold}"
            except:
                return f"monitor {parts[0]} 10000"
        else:
            return f"monitor {text[2:].strip()} 10000"
    
    # "历史" -> history
    if "历史" in text or "昨天" in text or "前天" in text:
        if "微博" in text:
            return "history weibo yesterday"
        elif "百度" in text:
            return "history baidu yesterday"
        elif "知乎" in text:
            return "history zhihu yesterday"
        else:
            return "history all yesterday"
    
    # 默认当作搜索
    return f"search {text}"


# ==================== 命令行入口 ====================

def main():
    """命令行入口 - 严格按飞书文档规范"""
    
    # 无参数时显示帮助
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: hot-search [command] [args]",
            "commands": {
                "hot": "hot-search [platform] - 获取热搜榜（all/baidu/weibo/zhihu）",
                "search": "hot-search search [keyword] [engine] - 关键词搜索",
                "monitor": "hot-search monitor [keyword] [threshold] - 热点监控",
                "history": "hot-search history [platform] [date] - 历史查询",
                "scrape": "hot-search scrape [url] - URL 深度抓取"
            },
            "examples": [
                "hot-search weibo",
                "hot-search search 张雪机车夺冠",
                "hot-search monitor 股票 10000",
                "hot-search history baidu 2026-03-30"
            ],
            "version": VERSION
        }, ensure_ascii=False, indent=2))
        return
    
    cmd = sys.argv[1].lower()
    
    # ========== hot 命令 ==========
    if cmd == "hot":
        platform = sys.argv[2] if len(sys.argv) > 2 else "all"
        detail = "--detail" in sys.argv
        
        # 平台参数处理
        if platform.startswith("--"):
            platform = "all"
        
        result = get_hot(platform, detail)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # ========== search 命令 ==========
    elif cmd == "search":
        if len(sys.argv) < 3:
            print(json.dumps({
                "success": False,
                "error": "请提供搜索关键词"
            }, ensure_ascii=False, indent=2))
            return
        
        keyword = sys.argv[2] if len(sys.argv) > 2 else ""
        engine = sys.argv[3] if len(sys.argv) > 3 else "all"
        
        result = search(keyword, engine)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # ========== monitor 命令 ==========
    elif cmd == "monitor":
        if len(sys.argv) < 3:
            print(json.dumps({
                "success": False,
                "error": "请提供监控关键词"
            }, ensure_ascii=False, indent=2))
            return
        
        keyword = sys.argv[2] if len(sys.argv) > 2 else ""
        threshold = int(sys.argv[3]) if len(sys.argv) > 3 else 10000
        
        result = monitor(keyword, threshold)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # ========== history 命令 ==========
    elif cmd == "history":
        platform = sys.argv[2] if len(sys.argv) > 2 else "all"
        date = sys.argv[3] if len(sys.argv) > 3 else "today"
        
        result = get_history(platform, date)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # ========== scrape 命令 ==========
    elif cmd == "scrape":
        if len(sys.argv) < 3:
            print(json.dumps({
                "success": False,
                "error": "请提供 URL"
            }, ensure_ascii=False, indent=2))
            return
        
        url = sys.argv[2]
        result = scrape(url)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # ========== parse 命令（自然语言解析）==========
    elif cmd == "parse":
        if len(sys.argv) < 3:
            print(json.dumps({
                "success": False,
                "error": "请提供自然语言指令"
            }, ensure_ascii=False, indent=2))
            return
        
        text = " ".join(sys.argv[2:])
        std_cmd = parse_natural_language(text)
        
        print(json.dumps({
            "success": True,
            "natural_language": text,
            "standard_command": std_cmd
        }, ensure_ascii=False, indent=2))
    
    # ========== version 命令 ==========
    elif cmd in ("version", "-v", "--version"):
        print(json.dumps({
            "success": True,
            "version": VERSION,
            "name": "Hot Search",
            "description": "全网热搜神器 V2.2 - OpenClaw 适配版"
        }, ensure_ascii=False, indent=2))
    
    # ========== 未知命令 ==========
    else:
        # 尝试自然语言解析
        text = " ".join(sys.argv[1:])
        std_cmd = parse_natural_language(text)
        
        print(json.dumps({
            "success": False,
            "error": f"未知命令: {cmd}",
            "hint": "已尝试自然语言解析",
            "parsed_command": std_cmd,
            "available_commands": ["hot", "search", "monitor", "history", "scrape", "parse"]
        }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()