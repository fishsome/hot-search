#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用新闻提取器 - 自动检测网站类型并提取新闻
支持：Next.js、普通HTML、API等
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class UniversalNewsExtractor:
    """通用新闻提取器"""
    
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.session = requests.Session()
        
        # 默认headers
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.5',
            'Accept-Encoding': 'identity',  # 关键！禁用gzip
            'Connection': 'keep-alive',
        }
        
        # 网站特定配置
        self.site_configs = {
            'zaobao.com': {'encoding': 'utf-8'},
            'news.cn': {'encoding': 'utf-8'},
            'people.com.cn': {'encoding': 'utf-8'},
            'thepaper.cn': {'type': 'nextjs', 'data_path': 'props.pageProps.data.recommendImg'},
            'cls.cn': {'type': 'nextjs'},
            'jiemian.com': {'encoding': 'utf-8'},
        }
    
    def extract(self, url: str, limit: int = 10) -> List[Dict]:
        """
        自动提取新闻
        
        Args:
            url: 网站URL
            limit: 返回条数
        
        Returns:
            新闻列表 [{title, link, source}]
        """
        try:
            # 获取网站配置
            config = self._get_site_config(url)
            
            # 请求页面
            headers = self.default_headers.copy()
            if 'headers' in config:
                headers.update(config['headers'])
            
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            
            # 设置编码
            encoding = config.get('encoding', response.apparent_encoding)
            response.encoding = encoding
            
            # 根据网站类型提取
            site_type = config.get('type')
            
            if site_type == 'nextjs':
                # Next.js网站：提取 __NEXT_DATA__
                news = self._extract_from_nextjs(response, config, limit)
            else:
                # 普通网站：提取新闻链接
                news = self._extract_from_html(response, config, limit)
            
            logger.info(f"提取成功: {url} -> {len(news)}条")
            return news
            
        except Exception as e:
            logger.error(f"提取失败: {url} -> {str(e)[:50]}")
            return []
    
    def _get_site_config(self, url: str) -> Dict:
        """获取网站特定配置"""
        for domain, config in self.site_configs.items():
            if domain in url:
                return config
        return {}
    
    def _extract_from_nextjs(self, response, config: Dict, limit: int) -> List[Dict]:
        """
        从Next.js网站提取新闻
        
        Args:
            response: HTTP响应
            config: 网站配置
            limit: 返回条数
        
        Returns:
            新闻列表
        """
        soup = BeautifulSoup(response.text, 'html.parser')
        next_data = soup.find('script', id='__NEXT_DATA__')
        
        if not next_data:
            logger.warning("未找到 __NEXT_DATA__")
            return []
        
        try:
            data = json.loads(next_data.string)
            
            # 根据配置的数据路径提取
            data_path = config.get('data_path', '')
            
            if data_path:
                # 按路径查找数据
                news_list = self._get_nested_value(data, data_path)
            else:
                # 自动查找新闻列表
                news_list = self._find_news_list(data)
            
            if not news_list:
                return []
            
            # 提取新闻
            results = []
            for item in news_list[:limit]:
                title = item.get('title') or item.get('name', '')
                
                # 构建链接
                link = item.get('link', '')
                if not link:
                    cont_id = item.get('contId') or item.get('id', '')
                    if cont_id:
                        if 'thepaper.cn' in response.url:
                            link = f'https://www.thepaper.cn/newsDetail_forward_{cont_id}'
                        else:
                            link = f'{response.url}?id={cont_id}'
                elif link and not link.startswith('http'):
                    link = response.url.rstrip('/') + '/' + link.lstrip('/')
                
                if title:
                    results.append({
                        'title': title,
                        'link': link,
                        'snippet': '',
                        'source': self._extract_domain(response.url),
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Next.js提取失败: {e}")
            return []
    
    def _extract_from_html(self, response, config: Dict, limit: int) -> List[Dict]:
        """
        从普通HTML提取新闻
        
        Args:
            response: HTTP响应
            config: 网站配置
            limit: 返回条数
        
        Returns:
            新闻列表
        """
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找新闻链接
        results = []
        seen_links = set()
        
        for a in soup.find_all('a', href=True):
            href = a.get('href', '')
            text = a.get_text(strip=True)
            
            # 判断是否是新闻链接
            if text and len(text) > 15:
                is_news = any(pattern in href for pattern in [
                    '/news/', '/story/', '/article/', 
                    '.html', '/world/', '/detail/',
                    '/gn/', '/cj/', '/sh/'
                ])
                
                if is_news and href not in seen_links:
                    # 补全链接
                    if href and not href.startswith('http'):
                        if href.startswith('/'):
                            href = response.url.split('/')[0] + '//' + response.url.split('/')[2] + href
                        else:
                            href = response.url.rstrip('/') + '/' + href
                    
                    seen_links.add(href)
                    
                    results.append({
                        'title': text,
                        'link': href,
                        'snippet': '',
                        'source': self._extract_domain(response.url),
                    })
                    
                    if len(results) >= limit:
                        break
        
        return results
    
    def _get_nested_value(self, data: Dict, path: str):
        """根据路径获取嵌套值"""
        keys = path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list) and key.isdigit():
                value = value[int(key)]
            else:
                return None
        
        return value
    
    def _find_news_list(self, data) -> Optional[List]:
        """自动查找新闻列表"""
        if isinstance(data, dict):
            # 查找列表类型的值
            for k, v in data.items():
                if isinstance(v, list) and len(v) > 0:
                    if isinstance(v[0], dict) and ('title' in v[0] or 'name' in v[0]):
                        return v
                # 递归查找
                result = self._find_news_list(v)
                if result:
                    return result
        elif isinstance(data, list):
            return data
        
        return None
    
    def _extract_domain(self, url: str) -> str:
        """提取域名"""
        match = re.search(r'://([^/]+)', url)
        return match.group(1) if match else url


# 便捷函数
def fetch_news(url: str, limit: int = 10) -> List[Dict]:
    """
    快速提取新闻（便捷函数）
    
    Args:
        url: 网站URL
        limit: 返回条数
    
    Returns:
        新闻列表
    """
    extractor = UniversalNewsExtractor()
    return extractor.extract(url, limit)


if __name__ == "__main__":
    # 测试
    test_urls = [
        'https://www.zaobao.com/',
        'https://www.news.cn/world/',
        'https://www.thepaper.cn/news_1',
        'https://www.jiemian.com/',
    ]
    
    extractor = UniversalNewsExtractor()
    
    for url in test_urls:
        print(f'\n测试: {url}')
        news = extractor.extract(url, limit=5)
        print(f'成功: {len(news)}条')
        for i, item in enumerate(news[:3], 1):
            print(f'{i}. {item["title"][:40]}')