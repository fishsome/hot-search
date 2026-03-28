#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hot Search v1.0.2 - 全网热搜神器
作者：FishSome | 邮箱：fishsomes@gmail.com

功能：多引擎搜索 + 金融数据 + 新闻抓取（纯Python，不用浏览器）
"""

import requests
from bs4 import BeautifulSoup
import random
import time
import re
import urllib.parse
from typing import List, Dict, Optional

# ==================== 配置 ====================

USER_AGENTS = {
    "chrome": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    ],
    "firefox": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0",
    ],
    "safari": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    ],
}

# 浏览器指纹
BROWSER_FINGERPRINTS = {
    "chrome": {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept_language": "zh-CN,zh;q=0.9,en;q=0.8",
        "accept_encoding": "gzip, deflate, br",
        "sec_ch_ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        "sec_ch_ua_mobile": "?0",
        "sec_ch_ua_platform": '"Windows"',
        "sec_fetch_dest": "document",
        "sec_fetch_mode": "navigate",
        "sec_fetch_site": "none",
        "sec_fetch_user": "?1",
        "upgrade_insecure_requests": "1",
    },
    "firefox": {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "accept_language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "accept_encoding": "gzip, deflate, br",
        "te": "trailers",
    },
}

TIMEOUT = 10  # 单次请求超时（秒）

# 搜索引擎配置
ENGINES = {
    "bing_global": {"url": "https://global.bing.com/search", "params": {"q": "{kw}"}},
    "bing_cn": {"url": "https://cn.bing.com/search", "params": {"q": "{kw}"}},
    "yandex": {"url": "https://yandex.com/search", "params": {"text": "{kw}"}},
    "swisscows": {"url": "https://swisscows.com/web", "params": {"q": "{kw}"}},
}

# 新闻源配置（纯静态抓取，不用浏览器）
NEWS_SOURCES = {
    "zaobao": {
        "name": "联合早报",
        "url": "https://www.zaobao.com/news/world",
        "pattern": "/story",  # 链接匹配模式
        "lang": "zh",
    },
    "rt": {
        "name": "RT俄罗斯",
        "url": "https://www.rt.com/",
        "pattern": "/news/",
        "lang": "en",
    },
    "un_news": {
        "name": "联合国新闻",
        "url": "https://news.un.org/zh",
        "pattern": "/story/",
        "lang": "zh",
    },
}

# 金融数据关键词映射
FINANCE_MAP = {
    "wti": ("commodity/crude-oil", "WTI原油"),
    "原油": ("commodity/crude-oil", "WTI原油"),
    "brent": ("commodity/brent-crude-oil", "布伦特原油"),
    "gold": ("commodity/gold", "黄金"),
    "黄金": ("commodity/gold", "黄金"),
    "bitcoin": ("crypto", "比特币"),
    "比特币": ("crypto", "比特币"),
}

# 中文翻译映射
ZH_EN = {
    "战争": "war", "原油": "crude oil", "油价": "oil price", "股市": "stock market",
    "经济": "economy", "科技": "technology", "政治": "politics", "中国": "China",
    "美国": "USA", "俄罗斯": "Russia", "伊朗": "Iran", "以色列": "Israel",
}

# ==================== 核心类 ====================

class HotSearch:
    """热搜神器：搜索 + 金融 + 新闻 + 跳转访问"""
    
    def __init__(self, timeout: int = TIMEOUT, browser: str = "chrome", cookie_file: str = None):
        self.timeout = timeout
        self.browser = browser
        self.session = requests.Session()
        
        # 初始化浏览器指纹
        self._init_fingerprint()
        
        # Cookie 持久化
        self.cookie_file = cookie_file or "/tmp/hot_search_cookies.json"
        self._load_cookies()
        
        # 模拟人工操作的延迟范围（秒）
        self.delay_range = (0.5, 2.0)
    
    def _init_fingerprint(self):
        """初始化浏览器指纹"""
        ua = random.choice(USER_AGENTS.get(self.browser, USER_AGENTS["chrome"]))
        fp = BROWSER_FINGERPRINTS.get(self.browser, {})
        
        self.session.headers.update({
            "User-Agent": ua,
            **fp
        })
    
    def _load_cookies(self):
        """加载保存的Cookie"""
        try:
            import json
            with open(self.cookie_file, "r") as f:
                cookies = json.load(f)
                for name, value in cookies.items():
                    self.session.cookies.set(name, value)
        except:
            pass
    
    def _save_cookies(self):
        """保存Cookie到文件"""
        try:
            import json
            cookies = {c.name: c.value for c in self.session.cookies}
            with open(self.cookie_file, "w") as f:
                json.dump(cookies, f)
        except:
            pass
    
    def _human_delay(self):
        """模拟人工操作延迟"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
    
    def _random_referer(self, url: str):
        """随机设置Referer"""
        domain = urllib.parse.urlparse(url).netloc
        referers = [
            f"https://www.google.com/search?q={random.choice(['news', 'today', 'latest'])}",
            f"https://www.baidu.com/s?wd={random.choice(['新闻', '今日', '最新'])}",
            f"https://{domain}/",
        ]
        self.session.headers["Referer"] = random.choice(referers)
    
    # ----- 跳转访问 -----
    def fetch(self, url: str, render_js: bool = False) -> Dict:
        """
        访问新页面，自动判断是否JS渲染
        
        Args:
            url: 目标链接
            render_js: 是否尝试执行JS（默认False，检测到JS时自动尝试）
        
        Returns:
            {"html": 内容, "is_js": 是否JS渲染, "title": 标题, "text": 纯文本}
        """
        result = {"url": url, "html": None, "text": None, "title": None, "is_js": False}
        
        try:
            # 模拟人工操作
            self._human_delay()
            self._random_referer(url)
            
            r = self.session.get(url, timeout=self.timeout)
            html = r.text
            
            # 保存Cookie
            self._save_cookies()
            
            # 判断是否JS渲染
            is_js = self._is_js_rendered(html)
            result["is_js"] = is_js
            
            if is_js and render_js:
                html = self._exec_js(html) or html
            
            soup = BeautifulSoup(html, "html.parser")
            result["html"] = html
            result["text"] = soup.get_text(strip=True)[:5000]
            result["title"] = soup.title.string if soup.title else None
            
        except Exception as e:
            result["error"] = str(e)[:50]
        
        return result
    
    def _is_js_rendered(self, html: str) -> bool:
        """判断页面是否JS渲染"""
        # 判断依据：body内容很少 + 有JS框架特征
        soup = BeautifulSoup(html, "html.parser")
        body = soup.find("body")
        if not body:
            return True
        
        text_len = len(body.get_text(strip=True))
        has_js_framework = any(x in html for x in ["__NEXT_DATA__", "__INITIAL_STATE__", "react", "vue", "angular", "window.__"])
        
        # 内容很少 + 有JS框架 = JS渲染
        return text_len < 500 and has_js_framework
    
    def _exec_js(self, html: str) -> str:
        """执行页面JS获取内容（无浏览器）"""
        try:
            import execjs
            soup = BeautifulSoup(html, "html.parser")
            
            # 提取并执行关键JS
            for script in soup.find_all("script"):
                code = script.string
                if code and any(x in code for x in ["article", "content", "data"]):
                    try:
                        ctx = execjs.compile(code)
                        return str(ctx.eval("this"))
                    except:
                        pass
        except:
            pass
        return None
    
    # ----- 搜索 -----
    def search(self, keyword: str, engine: str = "bing_global") -> List[Dict]:
        """单引擎搜索"""
        if engine not in ENGINES:
            return []
        
        cfg = ENGINES[engine]
        url = cfg["url"] + "?" + urllib.parse.urlencode({k: v.format(kw=keyword) for k, v in cfg["params"].items()})
        
        try:
            r = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(r.text, "html.parser")
            results = []
            for item in soup.select(".b_algo, .serp-item, .result")[:10]:
                t = item.find(["h2", "h3"])
                a = item.find("a")
                if t and a:
                    results.append({"title": t.get_text(strip=True), "link": a.get("href", "")})
            return results
        except:
            return []
    
    def search_all(self, keyword: str) -> Dict[str, List]:
        """多引擎搜索（阻塞控制：总超时10秒）"""
        results = {}
        start = time.time()
        for engine in ENGINES:
            if time.time() - start > 10:
                break
            results[engine] = self.search(keyword, engine)
            time.sleep(0.5)
        return results
    
    # ----- 金融数据 -----
    def finance(self, keyword: str) -> Dict:
        """金融数据查询（Trading Economics）"""
        kw = keyword.lower()
        path, name = FINANCE_MAP.get(kw, (None, keyword))
        
        if not path:
            return {"error": "不支持的关键词"}
        
        url = f"https://tradingeconomics.com/{path}"
        
        try:
            r = self.session.get(url, timeout=self.timeout)
            text = r.text
            
            # 提取价格
            price_match = re.search(r'(?:rose to|at)\s+([\d.]+)\s*(?:USD|USD/Bbl|\$)', text)
            price = price_match.group(1) if price_match else None
            
            # 提取涨跌
            change_match = re.search(r'(up|down)\s+([\d.]+)%', text)
            change = f"{'+' if change_match and change_match.group(1)=='up' else '-'}{change_match.group(2) if change_match else '?'}%"
            
            return {"name": name, "price": f"{price} USD" if price else None, "change": change, "url": url}
        except Exception as e:
            return {"error": str(e)[:50]}
    
    # ----- 新闻抓取 -----
    def news(self, sources: List[str] = None, limit: int = 5) -> Dict[str, List]:
        """新闻抓取（纯静态，不用浏览器）"""
        if not sources:
            sources = list(NEWS_SOURCES.keys())
        
        results = {}
        for src in sources:
            if src not in NEWS_SOURCES:
                continue
            
            cfg = NEWS_SOURCES[src]
            try:
                r = self.session.get(cfg["url"], timeout=self.timeout)
                soup = BeautifulSoup(r.text, "html.parser")
                
                articles = []
                for link in soup.find_all("a", href=True):
                    href, text = link.get("href", ""), link.get_text(strip=True)
                    if cfg["pattern"] in href and 5 < len(text) < 100:
                        if href.startswith("/"):
                            href = cfg["url"].split("//")[0] + "//" + cfg["url"].split("//")[1].split("/")[0] + href
                        articles.append({"title": text, "url": href})
                
                # 去重
                seen = set()
                results[src] = [a for a in articles if a["url"] not in seen and not seen.add(a["url"])][:limit]
            except:
                results[src] = []
        
        return results
    
    # ----- 图片搜索 -----
    def images(self, keyword: str, limit: int = 5, save_dir: str = "/tmp") -> List[str]:
        """图片搜索并下载"""
        url = f"https://global.bing.com/images/search?q={urllib.parse.quote(keyword)}"
        try:
            r = self.session.get(url, timeout=self.timeout)
            imgs = re.findall(r'm="(https?://[^"]+\.(jpg|png))', r.text)[:limit]
            saved = []
            for i, (img_url, _) in enumerate(imgs):
                path = f"{save_dir}/{keyword}_{i}.jpg"
                if self._download(img_url, path):
                    saved.append(path)
            return saved
        except:
            return []
    
    def _download(self, url: str, path: str) -> bool:
        """下载文件"""
        try:
            r = self.session.get(url, timeout=self.timeout)
            if r.status_code == 200:
                with open(path, "wb") as f:
                    f.write(r.content)
                return True
        except:
            pass
        return False

# ==================== 命令行入口 ====================

if __name__ == "__main__":
    import sys
    
    hs = HotSearch()
    
    if len(sys.argv) < 2:
        print("用法: python search_skill.py <命令> [参数]")
        print("命令: search <关键词> | finance <关键词> | news | images <关键词>")
        sys.exit(1)
    
    cmd, arg = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ""
    
    if cmd == "search":
        for eng, res in hs.search_all(arg).items():
            if res:
                print(f"\n【{eng}】{len(res)}条")
                for r in res[:3]:
                    print(f"  - {r['title'][:50]}")
    
    elif cmd == "finance":
        data = hs.finance(arg)
        print(f"\n【{data.get('name', arg)}】")
        print(f"  价格: {data.get('price', '-')}")
        print(f"  涨跌: {data.get('change', '-')}")
        print(f"  链接: {data.get('url', '-')}")
    
    elif cmd == "news":
        for src, articles in hs.news().items():
            if articles:
                print(f"\n【{NEWS_SOURCES[src]['name']}】{len(articles)}条")
                for a in articles[:3]:
                    print(f"  - {a['title'][:50]}")
    
    elif cmd == "images":
        saved = hs.images(arg)
        print(f"\n下载 {len(saved)} 张图片:")
        for p in saved:
            print(f"  - {p}")