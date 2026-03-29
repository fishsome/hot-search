#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hot Search v2.0 - URL 深度抓取模块
抓取 URL 并提取正文、自动去除广告、输出 Markdown 格式

作者：FishSome
支持：微信公众号、知乎、微博、今日头条等常见网站
"""

import os
import re
import time
import json
import random
import urllib.parse
from typing import Dict, Optional, List, Tuple
from bs4 import BeautifulSoup, Comment, NavigableString
import requests

# 导入反爬工具（支持直接运行和模块导入）
try:
    from ..utils.anti_crawl import (
        get_random_ua,
        get_headers,
        retry_request,
        create_retry_session,
        CookieManager,
    )
    from ..utils.config import get_config, get_config_manager
except ImportError:
    # 直接运行时使用绝对导入
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.anti_crawl import (
        get_random_ua,
        get_headers,
        retry_request,
        create_retry_session,
        CookieManager,
    )
    from utils.config import get_config, get_config_manager


# ==================== 正文提取策略 ====================

class ContentExtractor:
    """
    正文提取器
    
    使用多种策略提取正文：
    1. 域名特定规则（精准）
    2. 通用规则（启发式）
    3. 密度分析（兜底）
    """
    
    def __init__(self):
        self.config = get_config()
    
    def extract(self, html: str, url: str) -> Dict:
        """
        提取正文
        
        Args:
            html: HTML 内容
            url: 原始 URL
        
        Returns:
            {
                "title": "标题",
                "content": "正文（Markdown）",
                "content_html": "正文（HTML）",
                "summary": "摘要",
                "keywords": ["关键词"],
                "metadata": {...},
            }
        """
        soup = BeautifulSoup(html, "html.parser")
        
        # 获取域名配置
        domain = self._get_domain(url)
        domain_config = self.config.article_fetcher.supported_domains.get(domain)
        
        result = {
            "title": None,
            "content": None,
            "content_html": None,
            "summary": None,
            "keywords": [],
            "metadata": {
                "url": url,
                "domain": domain,
                "extractor": "unknown",
            },
        }
        
        # 策略 1: 域名特定规则
        if domain_config:
            result = self._extract_with_domain_config(soup, domain_config, result)
            result["metadata"]["extractor"] = "domain_specific"
        
        # 策略 2: 通用规则
        if not result["content"]:
            result = self._extract_with_generic_rules(soup, result)
            result["metadata"]["extractor"] = "generic"
        
        # 策略 3: 密度分析（兜底）
        if not result["content"]:
            result = self._extract_with_density_analysis(soup, result)
            result["metadata"]["extractor"] = "density"
        
        # 清理和优化
        if result["content"]:
            result["content"] = self._clean_content(result["content"])
            result["summary"] = self._generate_summary(result["content"])
            result["keywords"] = self._extract_keywords(result["content"])
        
        # 提取标题（如果还没有）
        if not result["title"]:
            result["title"] = self._extract_title(soup)
        
        # 提取元数据
        result["metadata"].update(self._extract_metadata(soup))
        
        return result
    
    def _get_domain(self, url: str) -> str:
        """获取域名"""
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc
    
    def _extract_with_domain_config(
        self, soup: BeautifulSoup, config: Dict, result: Dict
    ) -> Dict:
        """使用域名特定规则提取"""
        
        # 提取标题
        if "title_selector" in config:
            title_elem = soup.select_one(config["title_selector"])
            if title_elem:
                result["title"] = title_elem.get_text(strip=True)
        
        # 提取正文
        if "content_selector" in config:
            content_elem = soup.select_one(config["content_selector"])
            if content_elem:
                # 先清理噪音
                self._remove_noise(content_elem)
                result["content_html"] = str(content_elem)
                result["content"] = self._html_to_markdown(content_elem)
        
        # 提取作者
        if "author_selector" in config:
            author_elem = soup.select_one(config["author_selector"])
            if author_elem:
                result["metadata"]["author"] = author_elem.get_text(strip=True)
        
        # 提取日期
        if "date_selector" in config:
            date_elem = soup.select_one(config["date_selector"])
            if date_elem:
                result["metadata"]["date"] = date_elem.get_text(strip=True)
        
        return result
    
    def _extract_with_generic_rules(self, soup: BeautifulSoup, result: Dict) -> Dict:
        """使用通用规则提取"""
        
        # 尝试通用选择器
        for selector in self.config.article_fetcher.generic_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # 计算文本密度
                text = content_elem.get_text(strip=True)
                if len(text) > 200:  # 至少有一定内容
                    self._remove_noise(content_elem)
                    result["content_html"] = str(content_elem)
                    result["content"] = self._html_to_markdown(content_elem)
                    break
        
        return result
    
    def _extract_with_density_analysis(self, soup: BeautifulSoup, result: Dict) -> Dict:
        """使用密度分析提取（兜底策略）"""
        
        # 找到文本密度最高的元素
        body = soup.find("body")
        if not body:
            return result
        
        best_elem = None
        best_score = 0
        
        # 分析所有候选元素
        candidates = body.find_all(["div", "article", "section", "main"])
        
        for elem in candidates:
            # 计算文本密度
            text = elem.get_text(strip=True)
            text_len = len(text)
            
            # 计算标签密度
            tags = elem.find_all()
            tag_count = len(tags)
            
            # 计算链接密度
            links = elem.find_all("a")
            link_count = len(links)
            link_text_len = sum(len(a.get_text(strip=True)) for a in links)
            
            # 计算得分
            # 原则：文本多、标签少、链接比例低 = 正文
            if tag_count > 0:
                score = (
                    text_len / tag_count * 10  # 文本/标签密度
                    - (link_text_len / text_len if text_len > 0 else 0) * 100  # 链接惩罚
                )
            else:
                score = text_len
            
            # 更新最佳元素
            if score > best_score and text_len > 200:
                best_score = score
                best_elem = elem
        
        if best_elem:
            self._remove_noise(best_elem)
            result["content_html"] = str(best_elem)
            result["content"] = self._html_to_markdown(best_elem)
        
        return result
    
    def _remove_noise(self, elem):
        """去除噪音元素（广告、导航等）"""
        
        # 删除噪音选择器
        for selector in self.config.article_fetcher.noise_selectors:
            for noise in elem.select(selector):
                noise.decompose()
        
        # 删除注释
        for comment in elem.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # 删除空元素
        for tag in elem.find_all():
            if not tag.get_text(strip=True) and not tag.find_all(["img", "video", "iframe"]):
                tag.decompose()
    
    def _html_to_markdown(self, elem) -> str:
        """将 HTML 转换为 Markdown"""
        
        lines = []
        
        def process_element(element, depth=0):
            if isinstance(element, NavigableString):
                text = str(element).strip()
                if text:
                    lines.append(text)
                return
            
            if element.name in ["script", "style", "nav", "footer", "aside"]:
                return
            
            # 标题
            if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                level = int(element.name[1])
                text = element.get_text(strip=True)
                if text:
                    lines.append(f"\n{'#' * level} {text}\n")
                return
            
            # 段落
            if element.name == "p":
                text = element.get_text(strip=True)
                if text:
                    lines.append(f"\n{text}\n")
                return
            
            # 链接
            if element.name == "a":
                text = element.get_text(strip=True)
                href = element.get("href", "")
                if text and href:
                    lines.append(f"[{text}]({href})")
                return
            
            # 图片
            if element.name == "img":
                alt = element.get("alt", "")
                src = element.get("src", "")
                if src:
                    lines.append(f"\n![{alt}]({src})\n")
                return
            
            # 列表
            if element.name == "ul" or element.name == "ol":
                lines.append("")
                for li in element.find_all("li", recursive=False):
                    text = li.get_text(strip=True)
                    if text:
                        prefix = "-" if element.name == "ul" else f"{li.index + 1}."
                        lines.append(f"{prefix} {text}")
                lines.append("")
                return
            
            # 引用
            if element.name == "blockquote":
                text = element.get_text(strip=True)
                if text:
                    lines.append(f"\n> {text}\n")
                return
            
            # 代码块
            if element.name == "pre":
                code = element.find("code")
                if code:
                    text = code.get_text()
                else:
                    text = element.get_text()
                if text:
                    lines.append(f"\n```\n{text}\n```\n")
                return
            
            # 内联代码
            if element.name == "code":
                parent = element.parent
                if parent and parent.name != "pre":
                    text = element.get_text(strip=True)
                    if text:
                        lines.append(f"`{text}`")
                return
            
            # 强调
            if element.name == "strong" or element.name == "b":
                text = element.get_text(strip=True)
                if text:
                    lines.append(f"**{text}**")
                return
            
            if element.name == "em" or element.name == "i":
                text = element.get_text(strip=True)
                if text:
                    lines.append(f"*{text}*")
                return
            
            # 表格
            if element.name == "table":
                lines.append("")
                rows = element.find_all("tr")
                if rows:
                    # 表头
                    headers = rows[0].find_all(["th", "td"])
                    if headers:
                        header_text = [h.get_text(strip=True) for h in headers]
                        lines.append("| " + " | ".join(header_text) + " |")
                        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                    
                    # 表格内容
                    for row in rows[1:]:
                        cells = row.find_all("td")
                        if cells:
                            cell_text = [c.get_text(strip=True) for c in cells]
                            lines.append("| " + " | ".join(cell_text) + " |")
                lines.append("")
                return
            
            # 分割线
            if element.name == "hr":
                lines.append("\n---\n")
                return
            
            # 其他元素，递归处理子元素
            for child in element.children:
                process_element(child, depth + 1)
        
        process_element(elem)
        
        # 合并并清理
        markdown = "\n".join(lines)
        
        # 清理多余空白
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)
        markdown = re.sub(r"^\s+|\s+$", "", markdown)
        
        return markdown
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """提取标题"""
        
        # 优先级顺序
        selectors = [
            "h1",
            ".title",
            ".article-title",
            ".post-title",
            "title",
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                title = elem.get_text(strip=True)
                if title and len(title) > 5:
                    return title
        
        return None
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """提取元数据"""
        
        metadata = {}
        
        # 从 meta 标签提取
        meta_tags = soup.find_all("meta")
        
        for meta in meta_tags:
            name = meta.get("name", "") or meta.get("property", "")
            content = meta.get("content", "")
            
            if not name or not content:
                continue
            
            # 常见元数据
            if name in ["description", "og:description"]:
                metadata["description"] = content
            elif name in ["author", "article:author"]:
                metadata["author"] = content
            elif name in ["keywords"]:
                metadata["keywords"] = content.split(",") if "," in content else [content]
            elif name in ["publish-date", "article:published_time", "date"]:
                metadata["date"] = content
            elif name in ["og:title"]:
                metadata["og_title"] = content
            elif name in ["og:image"]:
                metadata["og_image"] = content
        
        return metadata
    
    def _clean_content(self, content: str) -> str:
        """清理正文"""
        
        # 限制长度
        max_len = self.config.article_fetcher.max_content_length
        if len(content) > max_len:
            content = content[:max_len] + "\n... (内容过长，已截断)"
        
        # 清理特殊字符
        content = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", content)
        
        # 清理多余的空白
        content = re.sub(r" {2,}", " ", content)
        
        return content.strip()
    
    def _generate_summary(self, content: str) -> str:
        """生成摘要"""
        
        # 提取前 300 字作为摘要
        text = re.sub(r"[#*\[\](){}|>`]", "", content)  # 移除 Markdown 标记
        text = re.sub(r"\s+", " ", text).strip()
        
        if len(text) > 200:
            # 在句号处截断
            sentences = re.split(r"[。！？.!?]", text)
            summary = ""
            for s in sentences[:3]:
                if len(summary + s) < 200:
                    summary += s + "。"
                else:
                    break
            return summary.strip()
        
        return text[:200].strip() + "..." if len(text) > 200 else text
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词"""
        
        # 简单的关键词提取：高频词
        # 提取中文词汇（2-4字）
        chinese_words = re.findall(r"[^\x00-\x7F]{2,4}", content)
        
        # 统计频率
        word_freq = {}
        for word in chinese_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 排序并返回前 5 个高频词
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        return [k[0] for k in keywords]


# ==================== URL 抓取器 ====================

class ArticleFetcher:
    """URL 深度抓取器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = get_config(config_path)
        self.extractor = ContentExtractor()
        self.session = create_retry_session(
            max_retries=self.config.max_retries,
            timeout=self.config.article_fetcher.timeout
        )
        self.cookie_manager = CookieManager()
    
    def scrape_url(self, url: str) -> Dict:
        """
        抓取 URL 并提取正文
        
        Args:
            url: 目标 URL
        
        Returns:
            {
                "title": "标题",
                "content": "正文内容（Markdown）",
                "summary": "摘要",
                "keywords": ["关键词"],
                "metadata": {...},
                "success": True/False,
                "error": None/错误信息,
            }
        """
        result = {
            "title": None,
            "content": None,
            "summary": None,
            "keywords": [],
            "metadata": {"url": url},
            "success": False,
            "error": None,
        }
        
        try:
            # 生成请求头
            headers = get_headers(referer=url)
            
            # 应用 Cookie
            self.cookie_manager.apply_to_session(self.session, url)
            
            # 发送请求
            response = self.session.get(
                url,
                headers=headers,
                timeout=self.config.article_fetcher.timeout,
                allow_redirects=True,
            )
            
            # 更新 Cookie
            self.cookie_manager.update_from_response(url, response)
            
            # 检查响应
            if response.status_code != 200:
                result["error"] = f"HTTP {response.status_code}"
                return result
            
            # 解码
            html = response.text
            
            # 提取正文
            extract_result = self.extractor.extract(html, url)
            
            # 合并结果
            result["title"] = extract_result["title"]
            result["content"] = extract_result["content"]
            result["summary"] = extract_result["summary"]
            result["keywords"] = extract_result["keywords"]
            result["metadata"] = extract_result["metadata"]
            result["success"] = bool(result["content"])
            
            if not result["success"]:
                result["error"] = "无法提取正文内容"
            
        except requests.exceptions.Timeout:
            result["error"] = "请求超时"
        except requests.exceptions.ConnectionError as e:
            result["error"] = f"连接错误: {str(e)[:50]}"
        except Exception as e:
            result["error"] = f"未知错误: {str(e)[:100]}"
        
        return result
    
    def scrape_urls(self, urls: List[str], delay_range: Tuple[float, float] = (0.5, 1.5)) -> Dict[str, Dict]:
        """
        批量抓取多个 URL
        
        Args:
            urls: URL 列表
            delay_range: 请求间隔范围（秒）
        
        Returns:
            {url: result}
        """
        results = {}
        
        for i, url in enumerate(urls):
            results[url] = self.scrape_url(url)
            
            # 请求间隔
            if i < len(urls) - 1:
                delay = random.uniform(*delay_range)
                time.sleep(delay)
        
        return results


# ==================== 便捷函数 ====================

def scrape_url(url: str, config_path: Optional[str] = None) -> Dict:
    """
    抓取 URL 并提取正文（便捷函数）
    
    Args:
        url: 目标 URL
        config_path: 配置文件路径
    
    Returns:
        {
            "title": "标题",
            "content": "正文内容（Markdown）",
            "summary": "摘要",
            "keywords": ["关键词"],
            "metadata": {...},
        }
    """
    fetcher = ArticleFetcher(config_path)
    return fetcher.scrape_url(url)


def scrape_urls(urls: List[str], config_path: Optional[str] = None) -> Dict[str, Dict]:
    """
    批量抓取多个 URL（便捷函数）
    
    Args:
        urls: URL 列表
        config_path: 配置文件路径
    
    Returns:
        {url: result}
    """
    fetcher = ArticleFetcher(config_path)
    return fetcher.scrape_urls(urls)


# ==================== 测试 ====================

if __name__ == "__main__":
    import sys
    
    print("=== URL 深度抓取测试 ===\n")
    
    if len(sys.argv) < 2:
        print("用法: python article.py <URL>")
        print("\n示例 URL:")
        print("  微信文章: https://mp.weixin.qq.com/s/xxx")
        print("  知乎文章: https://zhuanlan.zhihu.com/p/xxx")
        print("  博客园: https://www.cnblogs.com/xxx/p/xxx.html")
        sys.exit(1)
    
    url = sys.argv[1]
    print(f"抓取: {url}\n")
    
    result = scrape_url(url)
    
    if result["success"]:
        print(f"标题: {result['title']}")
        print(f"摘要: {result['summary']}")
        print(f"关键词: {', '.join(result['keywords'])}")
        print(f"\n正文（前 500 字）:")
        print(result["content"][:500] + "...")
        print(f"\n元数据: {json.dumps(result['metadata'], ensure_ascii=False, indent=2)}")
    else:
        print(f"失败: {result['error']}")
        print(f"元数据: {json.dumps(result['metadata'], ensure_ascii=False, indent=2)}")