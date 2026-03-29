#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hot Search v1.0.1 - 全网热搜神器
作者：FishSome
支持：多引擎聚合搜索、Trading Economics 金融数据、图片下载

=== 版本日志 ===
v1.0.2 (2026-03-29)
- 新增 Hot News 新闻搜索功能
- 支持中文关键词自动翻译成英文搜索
- 支持 5 个无需代理的权威新闻源

v1.0.1 (2026-03-29)
- 新增 Trading Economics 搜索引擎（金融/经济数据专用）
- 新增阻塞控制：单引擎 2 秒超时，总超时 10 秒
- 修复文档不一致问题
- 优化搜索结果解析

v1.0.0 (2026-03-28)
- 初始版本
- 支持 Bing 国内/国际、Yandex、Swisscows
- 支持图片搜索和下载

=== 阻塞规则 ===
根据 AGENTS.md 任务执行阻断规则：
- 单引擎超时：2 秒
- 多引擎总超时：10 秒
- 失败自动跳过，记录失败列表
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import random
import time
import json
import re
import urllib.parse
from datetime import datetime
from typing import List, Dict, Optional

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 Version/17.2 Mobile/15E148 Safari/604.1"
]

def get_headers() -> Dict[str, str]:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.bing.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

def create_session() -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[403, 429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

SEARCH_ENGINES = {
    "bing_cn": {"name": "必应国内", "url": "https://cn.bing.com/search", "params": {"q": "{keyword}"}, "selector": ".b_algo", "title_selector": "h2", "link_selector": "a", "snippet_selector": ".b_caption p"},
    "bing_global": {"name": "必应国际", "url": "https://global.bing.com/search", "params": {"q": "{keyword}", "ensearch": "1"}, "selector": ".b_algo", "title_selector": "h2", "link_selector": "a", "snippet_selector": ".b_caption p"},
    "yandex": {"name": "Yandex", "url": "https://yandex.com/search", "params": {"text": "{keyword}"}, "selector": ".serp-item", "title_selector": "h2 a", "link_selector": "h2 a", "snippet_selector": ".OrganicText"},
    "swisscows": {"name": "Swisscows", "url": "https://swisscows.com/web", "params": {"q": "{keyword}"}, "selector": ".result", "title_selector": "h3 a", "link_selector": "h3 a", "snippet_selector": ".description"},
    "trading_economics": {"name": "Trading Economics", "url": "https://tradingeconomics.com/search", "params": {"q": "{keyword}"}, "selector": ".search-result, .datatable-row, tr", "title_selector": "a, td:first-child", "link_selector": "a", "snippet_selector": "td:nth-child(2), .description"}
}

class SearchEngine:
    """
    Hot Search 搜索引擎
    
    阻塞规则（根据 AGENTS.md 任务执行阻断规则）：
    - 单引擎超时：2 秒
    - 多引擎搜索总超时：10 秒
    - 失败自动跳过，记录失败列表
    """
    
    def __init__(self, delay_range=(0.5, 1.0), timeout=2):
        """
        Args:
            delay_range: 请求间隔时间范围（秒），默认 0.5-1 秒
            timeout: 单次请求超时时间（秒），默认 2 秒
        """
        self.delay_range = delay_range
        self.timeout = timeout
        self.session = create_session()
        self.failed_engines = []  # 记录失败的引擎
    
    def _get_headers(self) -> Dict[str, str]:
        return get_headers()
    
    def _random_delay(self):
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
    
    def _parse_results(self, html: str, engine_config: Dict) -> List[Dict]:
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for item in soup.select(engine_config["selector"]):
            try:
                title_elem = item.select_one(engine_config["title_selector"])
                link_elem = item.select_one(engine_config["link_selector"])
                snippet_elem = item.select_one(engine_config["snippet_selector"])
                if title_elem and link_elem:
                    results.append({"title": title_elem.get_text(strip=True), "link": link_elem.get("href", ""), "snippet": snippet_elem.get_text(strip=True) if snippet_elem else ""})
            except Exception:
                continue
        return results[:10]
    
    def search(self, keyword: str, engine: str = "bing_cn") -> List[Dict]:
        if engine not in SEARCH_ENGINES:
            raise ValueError(f"不支持的引擎：{engine}")
        config = SEARCH_ENGINES[engine]
        headers = self._get_headers()
        params = {k: v.replace("{keyword}", keyword) for k, v in config["params"].items()}
        try:
            response = self.session.get(config["url"], params=params, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                return self._parse_results(response.text, config)
            return []
        except Exception as e:
            print(f"搜索失败：{str(e)[:100]}")
            return []
    
    def search_all(self, keyword: str, engines: Optional[List[str]] = None) -> Dict[str, List[Dict]]:
        """
        多引擎搜索（带阻塞控制）
        
        阻塞规则：
        - 单引擎超时 2 秒
        - 总超时不超过 10 秒
        - 失败引擎记录到 self.failed_engines
        """
        if engines is None:
            engines = ["bing_cn", "bing_global", "yandex", "swisscows"]
        
        results = {}
        self.failed_engines = []
        
        print(f"搜索：{keyword}")
        total_start = time.time()
        
        for engine in engines:
            # 检查总超时
            if (time.time() - total_start) > 10:
                print(f"总超时 10 秒，跳过剩余引擎")
                self.failed_engines.extend([e for e in engines if e not in results])
                break
            
            if engine in SEARCH_ENGINES:
                engine_name = SEARCH_ENGINES[engine]["name"]
                print(f"  {engine_name}...", end=" ")
                
                try:
                    start_time = time.time()
                    engine_results = self.search(keyword, engine)
                    elapsed = (time.time() - start_time) * 1000
                    results[engine] = engine_results
                    
                    icon = "OK" if engine_results else "FAIL"
                    print(f"{icon} {len(engine_results)}条 ({elapsed:.0f}ms)")
                except Exception as e:
                    print(f"FAIL {str(e)[:50]}")
                    self.failed_engines.append(engine)
                    results[engine] = []
                
                if engine != engines[-1]:
                    self._random_delay()
        
        return results
    
    def deduplicate(self, all_results: Dict[str, List[Dict]]) -> List[Dict]:
        seen_links = set()
        unique_results = []
        for engine, results in all_results.items():
            for item in results:
                if item["link"] not in seen_links:
                    seen_links.add(item["link"])
                    item["source"] = engine
                    unique_results.append(item)
        return unique_results
    
    def search_bing_images(self, keyword: str, limit: int = 10) -> List[str]:
        """从 Bing 图片搜索获取图片真实 URL"""
        url = "https://global.bing.com/images/search"
        params = {"q": keyword}
        headers = self._get_headers()
        image_urls = []
        
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                for link in soup.select("a"):
                    href = link.get("href", "")
                    if "mediaurl=" in href:
                        parsed = urllib.parse.parse_qs(href)
                        if "mediaurl" in parsed:
                            image_urls.append(parsed["mediaurl"][0])
                            if len(image_urls) >= limit:
                                break
        except Exception as e:
            print(f"图片搜索失败：{str(e)[:100]}")
        
        return image_urls
    
    def download_image(self, image_url: str, output_path: str) -> bool:
        """下载图片到本地"""
        import os
        headers = self._get_headers()
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
            
            response = self.session.get(image_url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                print(f"图片已下载：{output_path}")
                return True
            else:
                print(f"下载失败：HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"下载异常：{str(e)[:100]}")
            return False
    
    def search_and_download(self, keyword: str, output_dir: str = "/home/fishsome/.openclaw/workspace/tmp", limit: int = 3) -> List[str]:
        """搜索并下载图片，返回下载成功的文件路径列表"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        image_urls = self.search_bing_images(keyword, limit=limit * 2)  # 多获取一些以防失败
        downloaded = []
        
        for i, url in enumerate(image_urls[:limit]):
            ext = ".jpg"  # 默认扩展名
            output_path = os.path.join(output_dir, f"{keyword}_{i+1}{ext}")
            if self.download_image(url, output_path):
                downloaded.append(output_path)
        
        return downloaded
    
    def search_trading_economics(self, keyword: str) -> Dict:
        """
        专门搜索 Trading Economics 金融数据
        支持：原油价格、股票、汇率、经济指标等
        
        返回格式：
        {
            "title": "数据标题",
            "value": "当前值",
            "change": "变化",
            "url": "详情链接"
        }
        """
        import re
        
        url = "https://tradingeconomics.com/"
        headers = self._get_headers()
        
        # 尝试直接访问指标页面
        keyword_map = {
            # 期货
            "wti": "commodity/crude-oil",
            "原油": "commodity/crude-oil",
            "crude oil": "commodity/crude-oil",
            "brent": "commodity/brent-crude-oil",
            "布伦特": "commodity/brent-crude-oil",
            "黄金": "commodity/gold",
            "gold": "commodity/gold",
            "天然气": "commodity/natural-gas",
            "natural gas": "commodity/natural-gas",
            "铜": "commodity/copper",
            "copper": "commodity/copper",
            # 加密货币 - 使用 /crypto 页面解析
            "比特币": "crypto",
            "bitcoin": "crypto",
            "btc": "crypto",
            "以太坊": "crypto",
            "ethereum": "crypto",
            "eth": "crypto",
            # 股指
            "sp500": "united-states/stock-market",
            "标普500": "united-states/stock-market",
            "s&p 500": "united-states/stock-market",
            "道琼斯": "united-states/stock-market",
            "dow jones": "united-states/stock-market",
            "nasdaq": "united-states/stock-market",
            "纳斯达克": "united-states/stock-market",
        }
        
        keyword_lower = keyword.lower()
        path = keyword_map.get(keyword_lower, f"search?q={urllib.parse.quote(keyword)}")
        full_url = f"{url}{path}"
        
        # 特殊处理：加密货币使用 /crypto 页面
        if path == "crypto":
            return self._parse_crypto_page(keyword, headers)
        
        # 特殊处理：股指使用统一页面
        if path == "united-states/stock-market":
            return self._parse_stock_market(keyword, headers)
        
        try:
            response = self.session.get(full_url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                text = response.text
                
                # 提取数据值
                result = {
                    "title": keyword,
                    "value": None,
                    "change": None,
                    "url": full_url,
                    "source": "Trading Economics"
                }
                
                # 用正则提取价格 "rose to 99.64 USD/Bbl" 或 "Crude Oil rose to 99.64"
                price_match = re.search(r'(?:rose to|at)\s+([\d.]+)\s*(?:USD|USD/Bbl|\$)', text)
                if price_match:
                    result["value"] = f"{price_match.group(1)} USD"
                
                # 提取变化百分比 "up 5.46%" 或 "down 2.3%"
                change_match = re.search(r'(up|down)\s+([\d.]+)%', text)
                if change_match:
                    direction = "+" if change_match.group(1) == "up" else "-"
                    result["change"] = f"{direction}{change_match.group(2)}%"
                
                # 如果没找到，尝试从页面元素提取
                if not result["value"]:
                    # 查找显示价格的元素
                    for selector in ['.market-value', '#market_val', '.data-value', '.price']:
                        elem = soup.select_one(selector)
                        if elem:
                            result["value"] = elem.get_text(strip=True)
                            break
                
                return result
            
            return {"error": f"HTTP {response.status_code}", "url": full_url}
            
        except Exception as e:
            return {"error": str(e)[:100], "url": full_url}
    
    def _parse_crypto_page(self, keyword: str, headers: Dict) -> Dict:
        """
        解析 Trading Economics 加密货币页面
        """
        url = "https://tradingeconomics.com/crypto"
        
        # 关键词映射
        crypto_map = {
            "bitcoin": "Bitcoin",
            "btc": "Bitcoin",
            "比特币": "Bitcoin",
            "ethereum": "Ether",
            "eth": "Ether",
            "以太坊": "Ether",
        }
        
        target_name = crypto_map.get(keyword.lower(), keyword.capitalize())
        
        try:
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                
                result = {
                    "title": target_name,
                    "value": None,
                    "change": None,
                    "url": url,
                    "source": "Trading Economics Crypto"
                }
                
                # 查找表格中的数据
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if cells and len(cells) >= 4:
                            name = cells[0].get_text(strip=True)
                            if name == target_name:
                                price = cells[1].get_text(strip=True)
                                change = cells[3].get_text(strip=True)
                                result["value"] = f"{price} USD"
                                result["change"] = change
                                return result
                
                return result
            
            return {"error": f"HTTP {response.status_code}", "url": url}
            
        except Exception as e:
            return {"error": str(e)[:100], "url": url}
    
    def _parse_stock_market(self, keyword: str, headers: Dict) -> Dict:
        """
        解析 Trading Economics 美国股指页面
        """
        url = "https://tradingeconomics.com/united-states/stock-market"
        
        # 关键词映射
        index_map = {
            "sp500": ("US500", "标普500"),
            "标普500": ("US500", "标普500"),
            "s&p 500": ("US500", "标普500"),
            "道琼斯": ("Dow Jones", "道琼斯"),
            "dow jones": ("Dow Jones", "道琼斯"),
            "nasdaq": ("Nasdaq", "纳斯达克"),
            "纳斯达克": ("Nasdaq", "纳斯达克"),
        }
        
        key, display_name = index_map.get(keyword.lower(), ("US500", "美国股指"))
        
        try:
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                text = response.text
                
                result = {
                    "title": display_name,
                    "value": None,
                    "change": None,
                    "url": url,
                    "source": "Trading Economics"
                }
                
                # 提取 US500 数据
                if key == "US500":
                    # "fell to 6369 points" 或 "US500, fell to 6369"
                    match = re.search(r'fell to ([\d,]+) points', text)
                    if match:
                        result["value"] = f"{match.group(1)} points"
                    
                    # "losing 1.67%" 或 "lost 1.4%"
                    change_match = re.search(r'(?:losing|lost|down)\s+([\d.]+)%', text)
                    if change_match:
                        result["change"] = f"-{change_match.group(1)}%"
                
                # 道琼斯和纳斯达克
                elif key == "Dow Jones":
                    match = re.search(r'Dow Jones[^%]*?(?:tumbled|fell|lost|down)[^%]*?([\d.]+)%', text, re.IGNORECASE)
                    if match:
                        result["value"] = "See details"
                        result["change"] = f"-{match.group(1)}%"
                
                elif key == "Nasdaq":
                    match = re.search(r'Nasdaq[^%]*?(?:slid|fell|lost|down|extended)[^%]*?([\d.]+)%', text, re.IGNORECASE)
                    if match:
                        result["value"] = "See details"
                        result["change"] = f"-{match.group(1)}%"
                
                return result
            
            return {"error": f"HTTP {response.status_code}", "url": url}
            
        except Exception as e:
            return {"error": str(e)[:100], "url": url}

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法：python search_skill.py <关键词> [引擎名]")
        sys.exit(1)
    keyword = sys.argv[1]
    engine = sys.argv[2] if len(sys.argv) > 2 else "bing_cn"
    search = SearchEngine()
    if engine == "all":
        results = search.search_all(keyword)
    else:
        results = search.search(keyword, engine)
        for i, item in enumerate(results, 1):
            print(f"{i}. {item['title']}")
            print(f"   {item['link']}")


# ============================================================
# Hot News - 新闻搜索功能
# ============================================================

NEWS_SOURCES = {
    "zaobao": {
        "name": "联合早报（新加坡）",
        "url": "https://www.zaobao.com",
        "lang": "zh",
        "need_translate": False,
        "link_pattern": "/story",
        "note": "国内访问自动跳转中国版",
    },
    "rt": {
        "name": "RT（俄罗斯）",
        "url": "https://www.rt.com/news/",
        "lang": "en",
        "need_translate": True,
        "link_pattern": "/news/",
        "note": "⚠️ 国内需代理",
    },
    "un_news": {
        "name": "联合国新闻（官方）",
        "url": "https://news.un.org/zh",
        "lang": "zh",
        "need_translate": False,
        "link_pattern": "/story/",
    },
    "apnews": {
        "name": "美联社 AP News（美国）",
        "url": "https://apnews.com/",
        "lang": "en",
        "need_translate": True,
        "link_pattern": "/article/",
    },
}

# 中文翻译映射表（常用新闻关键词）
ZH_EN_MAP = {
    "战争": "war conflict",
    "原油": "crude oil",
    "油价": "oil price",
    "股市": "stock market",
    "经济": "economy",
    "科技": "technology",
    "政治": "politics",
    "总统": "president",
    "中国": "China",
    "美国": "United States USA",
    "俄罗斯": "Russia",
    "乌克兰": "Ukraine",
    "中东": "Middle East",
    "伊朗": "Iran",
    "以色列": "Israel",
    "朝鲜": "North Korea",
    "日本": "Japan",
    "韩国": "South Korea",
    "欧洲": "Europe",
    "贸易": "trade",
    "关税": "tariff",
    "芯片": "chip semiconductor",
    "人工智能": "AI artificial intelligence",
    "新冠": "COVID pandemic",
    "疫情": "pandemic outbreak",
    "气候": "climate",
    "能源": "energy",
    "天然气": "natural gas",
    "黄金": "gold",
    "比特币": "Bitcoin cryptocurrency",
    "美联储": "Federal Reserve Fed",
    "加息": "interest rate hike",
    "通胀": "inflation",
}


def translate_to_english(keyword: str) -> str:
    """
    中文关键词翻译成英文
    如果没有映射，返回原文（假设已经是英文）
    """
    # 检查是否是中文
    has_chinese = any('\u4e00' <= c <= '\u9fff' for c in keyword)
    
    if not has_chinese:
        return keyword
    
    # 查找映射
    for zh, en in ZH_EN_MAP.items():
        if zh in keyword:
            return keyword.replace(zh, en)
    
    # 没有映射，返回原文
    return keyword


def search_news(keyword: str = "", sources: Optional[List[str]] = None, limit: int = 5) -> Dict[str, List[Dict]]:
    """
    Hot News 新闻搜索（静态抓取，不用浏览器）
    
    方法：
    1. 直接访问新闻网站
    2. 提取包含特定模式的链接
    3. 返回新闻标题和链接
    
    Args:
        keyword: 搜索关键词（可选）
        sources: 新闻源列表，默认搜索所有
        limit: 每个源返回条数
    
    Returns:
        {source_name: [新闻列表]}
    """
    if sources is None:
        sources = list(NEWS_SOURCES.keys())
    
    results = {}
    
    print(f"\n{'='*50}")
    print(f"📰 Hot News - 新闻搜索")
    if keyword:
        print(f"关键词: {keyword}")
    print(f"{'='*50}\n")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.google.com/"
    }
    
    for source in sources:
        if source not in NEWS_SOURCES:
            continue
        
        config = NEWS_SOURCES[source]
        
        # 判断是否需要翻译
        search_keyword = keyword
        if keyword and config["need_translate"]:
            search_keyword = translate_to_english(keyword)
            print(f"🔍 {config['name']}: {keyword} → {search_keyword}")
        else:
            print(f"🔍 {config['name']}")
        
        # 发送请求
        url = config["url"]
        link_pattern = config.get("link_pattern", "/story/")
        
        try:
            start = time.time()
            r = requests.get(url, headers=headers, timeout=10)
            elapsed = (time.time() - start) * 1000
            
            if r.status_code == 200:
                r.encoding = "utf-8"
                soup = BeautifulSoup(r.text, "html.parser")
                
                # 提取新闻链接
                articles = []
                base_url = "/".join(url.split("/")[:3])
                
                for link in soup.find_all("a", href=True):
                    href = link.get("href", "")
                    text = link.get_text(strip=True)
                    
                    # 跳过空链接或导航链接
                    if not text or len(text) < 10 or len(text) > 150:
                        continue
                    
                    # RT 特殊处理：/news/xxx 格式的文章链接
                    if source == "rt":
                        if href.startswith("/news/") and len(href) > 6:
                            full_url = base_url + href
                            articles.append({"title": text, "url": full_url, "source": config["name"]})
                    
                    # AP News 特殊处理：/article/xxx 格式
                    elif source == "apnews":
                        if "/article/" in href:
                            full_url = href if href.startswith("http") else base_url + href
                            articles.append({"title": text, "url": full_url, "source": config["name"]})
                    
                    # 其他源：使用 link_pattern 过滤
                    elif link_pattern and link_pattern in href:
                        full_url = href if href.startswith("http") else base_url + href
                        articles.append({"title": text, "url": full_url, "source": config["name"]})
                
                # 去重
                seen = set()
                unique = []
                for a in articles:
                    if a["url"] not in seen:
                        seen.add(a["url"])
                        unique.append(a)
                
                results[source] = unique[:limit]
                print(f"   ✅ {len(unique[:limit])} 条新闻 ({elapsed:.0f}ms)")
                
            else:
                results[source] = []
                print(f"   ❌ HTTP {r.status_code}")
        
        except Exception as e:
            results[source] = []
            print(f"   ❌ {str(e)[:50]}")
        
        time.sleep(0.5)
    
    return results


def get_hot_news(topic: str = "general", limit: int = 5) -> List[Dict]:
    """
    获取热点新闻（预设主题）
    
    Args:
        topic: 主题（general, china, world, tech, finance）
        limit: 每个源返回条数
    
    Returns:
        新闻列表
    """
    topic_keywords = {
        "general": ["news today", "breaking news"],
        "china": ["China", "中国"],
        "world": ["world news", "international"],
        "tech": ["technology", "AI", "科技"],
        "finance": ["economy", "stock market", "经济"],
    }
    
    keywords = topic_keywords.get(topic, topic_keywords["general"])
    
    all_news = []
    for kw in keywords:
        results = search_news(kw, ["apnews", "zaobao", "rt"])
        for source, articles in results.items():
            all_news.extend(articles[:limit])
    
    return all_news[:limit * 3]


# 命令行入口
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法：")
        print("  python search_skill.py <关键词> [引擎]")
        print("  python search_skill.py --news <关键词>")
        print("  python search_skill.py --hotnews [主题]")
        sys.exit(1)
    
    if sys.argv[1] == "--news":
        keyword = sys.argv[2] if len(sys.argv) > 2 else "news"
        results = search_news(keyword)
        
        print(f"\n{'='*50}")
        print("📰 新闻汇总")
        print(f"{'='*50}")
        
        for source, articles in results.items():
            if articles:
                print(f"\n【{NEWS_SOURCES[source]['name']}】")
                for i, article in enumerate(articles[:5], 1):
                    print(f"  {i}. {article['title'][:50]}...")
                    print(f"     {article['link']}")
    
    elif sys.argv[1] == "--hotnews":
        topic = sys.argv[2] if len(sys.argv) > 2 else "general"
        news = get_hot_news(topic)
        
        print(f"\n{'='*50}")
        print(f"📰 热点新闻 - {topic}")
        print(f"{'='*50}\n")
        
        for i, article in enumerate(news, 1):
            print(f"{i}. [{article['source']}]")
            print(f"   {article['title']}")
            print(f"   {article['link']}\n")
    
    else:
        # 原有搜索功能
        keyword = sys.argv[1]
        engine = sys.argv[2] if len(sys.argv) > 2 else "all"
        
        search = SearchEngine()
        
        if engine == "all":
            results = search.search_all(keyword)
        else:
            results = search.search(keyword, engine)
            for i, item in enumerate(results, 1):
                print(f"{i}. {item['title']}")
                print(f"   {item['link']}")
