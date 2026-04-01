#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻源配置 - 所有可用新闻源
使用通用提取器自动提取
"""

# 新闻源列表（按优先级排序）
NEWS_SOURCES = {
    # 国内新闻源
    'xinhua_world': {
        'name': '新华网-国际',
        'url': 'https://www.news.cn/world/',
        'priority': 1,
        'category': 'domestic',
    },
    'jiemian': {
        'name': '界面新闻',
        'url': 'https://www.jiemian.com/',
        'priority': 2,
        'category': 'domestic',
    },
    'thepaper': {
        'name': '澎湃新闻',
        'url': 'https://www.thepaper.cn/news_1',
        'priority': 2,
        'category': 'domestic',
        'type': 'nextjs',
        'data_path': 'props.pageProps.data.recommendImg',
    },
    'zaobao': {
        'name': '联合早报',
        'url': 'https://www.zaobao.com/',
        'priority': 1,
        'category': 'international',
        'encoding': 'utf-8',
    },
    'un_news': {
        'name': '联合国新闻',
        'url': 'https://news.un.org/zh',
        'priority': 2,
        'category': 'international',
    },
    'apnews': {
        'name': '美联社',
        'url': 'https://apnews.com',
        'priority': 1,
        'category': 'international',
    },
}

# 新闻源分组
NEWS_GROUPS = {
    'all': list(NEWS_SOURCES.keys()),
    'domestic': ['xinhua_world', 'jiemian', 'thepaper'],
    'international': ['zaobao', 'un_news', 'apnews'],
    'priority': ['xinhua_world', 'zaobao', 'apnews'],  # 高优先级源
}