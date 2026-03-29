#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hot Search v2.0 - 站点地图模块
发现和解析网站站点地图（sitemap.xml）

作者：FishSome
"""

import os
import sys
import re
import time
import random
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, urljoin
import requests

try:
    from ..utils.anti_crawl import get_headers, get_random_ua, retry_request, RateLimit
    from ..utils.config import get_config
except ImportError:
    # 直接运行时使用绝对导入
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.anti_crawl import get_headers, get_random_ua, retry_request, RateLimit
    from utils.config import get_config


# ==================== 站点地图发现 ====================

SITEMAP_COMMON_PATHS = [
    "/sitemap.xml",
    "/sitemap_index.xml",
    "/sitemap",
    "/sitemap.php",
    "/sitemap.txt",
    "/sitemap_index.xml.gz",
    "/sitemap.xml.gz",
    "/sitemap1.xml",
    "/sitemap-1.xml",
    "/robots_sitemap.xml",
]


def discover_sitemap(base_url: str) -> List[str]:
    """
    发现网站地图
    
    方法:
    1. 检查 robots.txt 中的 Sitemap
    2. 尝试常见路径: /sitemap.xml, /sitemap_index.xml
    3. 解析 XML 获取 URL 列表
    
    Args:
        base_url: 网站 URL（如 https://example.com）
    
    Returns:
        ["sitemap_url1", "sitemap_url2", ...]
    """
    sitemaps = []
    parsed = urlparse(base_url)
    domain = f"{parsed.scheme}://{parsed.netloc}"
    
    # 方法1: 检查 robots.txt
    robots_url = f"{domain}/robots.txt"
    print(f"检查 robots.txt: {robots_url}")
    
    try:
        headers = get_headers(referer=domain)
        response = requests.get(robots_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # 解析 robots.txt 中的 Sitemap 指令
            content = response.text
            for line in content.splitlines():
                line = line.strip()
                if line.lower().startswith("sitemap:"):
                    sitemap_url = line.split(":", 1)[1].strip()
                    sitemaps.append(sitemap_url)
                    print(f"从 robots.txt 发现: {sitemap_url}")
    except Exception as e:
        print(f"robots.txt 获取失败: {str(e)[:50]}")
    
    # 方法2: 尝试常见路径
    for path in SITEMAP_COMMON_PATHS:
        sitemap_url = f"{domain}{path}"
        
        # 跳过已发现的
        if sitemap_url in sitemaps:
            continue
        
        try:
            headers = get_headers(referer=domain)
            response = requests.get(sitemap_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # 验证是否为 XML
                content_type = response.headers.get("Content-Type", "")
                if "xml" in content_type.lower() or response.text.strip().startswith("<?xml"):
                    sitemaps.append(sitemap_url)
                    print(f"发现站点地图: {sitemap_url}")
                    
                    # 延迟，避免请求过快
                    time.sleep(random.uniform(0.5, 1.5))
        except Exception:
            pass
    
    return sitemaps


def parse_sitemap_xml(xml_content: str, base_url: str = None) -> List[Dict]:
    """
    解析站点地图 XML
    
    支持格式:
    - 标准 sitemap: <url><loc>...
    - 站点地图索引: <sitemap><loc>...
    
    Args:
        xml_content: XML 内容
        base_url: 基础 URL（用于相对路径）
    
    Returns:
        [{"url": "...", "lastmod": "...", "changefreq": "...", "priority": "..."}]
    """
    urls = []
    
    try:
        # 清理 XML（去除 BOM 等）
        xml_content = xml_content.strip()
        if xml_content.startswith("\ufeff"):
            xml_content = xml_content[1:]
        
        # 解析 XML
        root = ET.fromstring(xml_content)
        
        # 命名空间处理
        ns = {}
        if root.tag.startswith("{"):
            ns_uri = root.tag.split("}")[0][1:]
            ns = {"ns": ns_uri}
        
        # 判断是 sitemap 还是 sitemapindex
        # sitemapindex: 包含多个子站点地图
        # urlset: 包含具体 URL
        
        # 处理 sitemapindex（站点地图索引）
        sitemap_elems = root.findall("ns:sitemap", ns) if ns else root.findall("sitemap")
        if sitemap_elems:
            for sitemap in sitemap_elems:
                loc = sitemap.find("ns:loc", ns) if ns else sitemap.find("loc")
                if loc and loc.text:
                    urls.append({
                        "url": loc.text.strip(),
                        "type": "sitemap",  # 这是子站点地图
                    })
            return urls
        
        # 处理 urlset（具体 URL）
        url_elems = root.findall("ns:url", ns) if ns else root.findall("url")
        for url_elem in url_elems:
            loc = url_elem.find("ns:loc", ns) if ns else url_elem.find("loc")
            if loc and loc.text:
                url_data = {"url": loc.text.strip(), "type": "page"}
                
                # 其他属性
                lastmod = url_elem.find("ns:lastmod", ns) if ns else url_elem.find("lastmod")
                if lastmod and lastmod.text:
                    url_data["lastmod"] = lastmod.text.strip()
                
                changefreq = url_elem.find("ns:changefreq", ns) if ns else url_elem.find("changefreq")
                if changefreq and changefreq.text:
                    url_data["changefreq"] = changefreq.text.strip()
                
                priority = url_elem.find("ns:priority", ns) if ns else url_elem.find("priority")
                if priority and priority.text:
                    url_data["priority"] = priority.text.strip()
                
                urls.append(url_data)
        
    except ET.ParseError as e:
        print(f"XML 解析失败: {str(e)[:50]}")
        
        # 尝试正则提取（备用）
        pattern = r"<loc>(.*?)</loc>"
        matches = re.findall(pattern, xml_content, re.DOTALL)
        for match in matches:
            url = match.strip()
            if url.startswith("http"):
                urls.append({"url": url, "type": "page"})
    
    return urls


def crawl_sitemap(sitemap_url: str, max_urls: int = 100, depth: int = 2) -> List[Dict]:
    """
    从站点地图爬取 URL
    
    Args:
        sitemap_url: 站点地图 URL
        max_urls: 最大 URL 数量
        depth: 递归深度（处理 sitemapindex）
    
    Returns:
        [{"url": "...", "lastmod": "...", "changefreq": "..."}]
    """
    all_urls = []
    visited_sitemaps = set()
    
    def _crawl_recursive(url: str, current_depth: int):
        """递归爬取站点地图"""
        if url in visited_sitemaps or current_depth > depth:
            return
        
        visited_sitemaps.add(url)
        
        # 延迟控制
        time.sleep(random.uniform(0.5, 1.5))
        
        print(f"爬取站点地图: {url}")
        
        try:
            headers = get_headers()
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"获取失败: HTTP {response.status_code}")
                return
            
            # 解析 XML
            xml_content = response.text
            parsed_urls = parse_sitemap_xml(xml_content, url)
            
            for item in parsed_urls:
                if len(all_urls) >= max_urls:
                    print(f"达到最大 URL 数量限制: {max_urls}")
                    return
                
                if item.get("type") == "sitemap":
                    # 这是子站点地图，递归处理
                    _crawl_recursive(item["url"], current_depth + 1)
                else:
                    # 这是具体页面 URL
                    all_urls.append(item)
                    if len(all_urls) % 50 == 0:
                        print(f"已发现 {len(all_urls)} 个 URL...")
        
        except Exception as e:
            print(f"爬取失败: {str(e)[:50]}")
    
    # 开始递归爬取
    _crawl_recursive(sitemap_url, 1)
    
    print(f"总共发现 {len(all_urls)} 个 URL")
    return all_urls[:max_urls]


# ==================== 站点地图爬取器 ====================

class SitemapCrawler:
    """站点地图爬取器"""
    
    def __init__(
        self,
        max_urls: int = 100,
        depth: int = 2,
        min_delay: float = 0.5,
        max_delay: float = 1.5,
        timeout: int = 15,
    ):
        self.max_urls = max_urls
        self.depth = depth
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.timeout = timeout
        self._rate_limit = RateLimit(
            max_requests_per_minute=30,
            min_interval=min_delay
        )
    
    def discover(self, base_url: str) -> List[str]:
        """发现站点地图"""
        return discover_sitemap(base_url)
    
    def crawl(self, sitemap_url: str) -> List[Dict]:
        """爬取站点地图"""
        return crawl_sitemap(sitemap_url, self.max_urls, self.depth)
    
    def crawl_all_from_site(self, base_url: str) -> List[Dict]:
        """
        从网站发现并爬取所有站点地图
        
        Args:
            base_url: 网站 URL
        
        Returns:
            URL 列表
        """
        # 发现站点地图
        sitemaps = self.discover(base_url)
        
        if not sitemaps:
            print(f"未发现站点地图: {base_url}")
            return []
        
        # 爬取每个站点地图
        all_urls = []
        for sitemap in sitemaps:
            urls = self.crawl(sitemap)
            all_urls.extend(urls)
            
            if len(all_urls) >= self.max_urls:
                break
        
        return all_urls[:self.max_urls]
    
    def get_page_urls(self, base_url: str, filters: Optional[Dict] = None) -> List[str]:
        """
        获取页面 URL（过滤非页面链接）
        
        Args:
            base_url: 网站 URL
            filters: 过滤条件 {"include": [...], "exclude": [...]}
        
        Returns:
            URL 字符串列表
        """
        all_urls = self.crawl_all_from_site(base_url)
        
        # 过滤
        page_urls = []
        for item in all_urls:
            url = item.get("url", "")
            
            # 基本过滤：排除非页面 URL
            if any(ext in url.lower() for ext in [".pdf", ".jpg", ".png", ".gif", ".zip", ".xml"]):
                continue
            
            # 自定义过滤
            if filters:
                include = filters.get("include", [])
                exclude = filters.get("exclude", [])
                
                # 包含规则
                if include and not any(pattern in url for pattern in include):
                    continue
                
                # 排除规则
                if exclude and any(pattern in url for pattern in exclude):
                    continue
            
            page_urls.append(url)
        
        return page_urls


# ==================== 便捷函数 ====================

def get_sitemap_urls(base_url: str, max_urls: int = 100) -> List[Dict]:
    """发现并获取站点地图 URL（便捷函数）"""
    crawler = SitemapCrawler(max_urls=max_urls)
    return crawler.crawl_all_from_site(base_url)


def get_page_urls(base_url: str, max_urls: int = 100, **filters) -> List[str]:
    """获取页面 URL 列表（便捷函数）"""
    crawler = SitemapCrawler(max_urls=max_urls)
    return crawler.get_page_urls(base_url, filters)


# ==================== 测试 ====================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="站点地图测试")
    parser.add_argument("command", choices=["discover", "crawl", "urls"], help="测试命令")
    parser.add_argument("--url", required=True, help="网站 URL")
    parser.add_argument("--max", type=int, default=50, help="最大 URL 数量")
    parser.add_argument("--sitemap", help="站点地图 URL（crawl 命令）")
    
    args = parser.parse_args()
    
    print("=== 站点地图测试 ===\n")
    
    if args.command == "discover":
        print(f"发现站点地图: {args.url}\n")
        sitemaps = discover_sitemap(args.url)
        print(f"\n发现 {len(sitemaps)} 个站点地图:")
        for s in sitemaps:
            print(f"  {s}")
    
    elif args.command == "crawl":
        sitemap_url = args.sitemap or f"{args.url}/sitemap.xml"
        print(f"爬取站点地图: {sitemap_url}\n")
        urls = crawl_sitemap(sitemap_url, max_urls=args.max)
        print(f"\n发现 {len(urls)} 个 URL:")
        for u in urls[:10]:
            print(f"  {u.get('url', '')[:80]}")
        if len(urls) > 10:
            print(f"  ... 还有 {len(urls) - 10} 个")
    
    elif args.command == "urls":
        print(f"获取页面 URL: {args.url}\n")
        crawler = SitemapCrawler(max_urls=args.max)
        urls = crawler.get_page_urls(args.url)
        print(f"\n获取 {len(urls)} 个页面 URL:")
        for u in urls[:10]:
            print(f"  {u[:80]}")
        if len(urls) > 10:
            print(f"  ... 还有 {len(urls) - 10} 个")