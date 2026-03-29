#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hot Search v2.0 - 配置管理模块
外置配置文件，支持平台开关、频率控制

作者：FishSome
"""

import json
import os
import sys
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path

# 默认配置文件路径（支持脚本直接运行）
def _get_default_config_path():
    """获取默认配置路径"""
    # 尝试多种路径
    candidates = [
        # 作为模块运行时
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json"),
        # 从工作目录运行时
        os.path.expanduser("~/.openclaw/workspace/skills/hot-search/config.json"),
        # 当前目录
        os.path.join(os.getcwd() if hasattr(os, 'getcwd') else '.', "config.json"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    # 返回第一个存在的候选路径或默认路径（用于创建）
    return candidates[1]

DEFAULT_CONFIG_PATH = _get_default_config_path()


@dataclass
class PlatformConfig:
    """平台配置"""
    enabled: bool = True
    timeout: int = 10  # 秒
    retry: int = 2
    delay_range: tuple = (0.5, 1.5)  # 请求间隔（秒）
    max_results: int = 10  # 最大返回结果数


@dataclass
class AntiCrawlConfig:
    """反爬配置"""
    user_agent_rotation: bool = True
    referer_rotation: bool = True
    cookie_persistence: bool = True
    request_delay: bool = True
    max_requests_per_minute: int = 30


@dataclass
class ArticleFetcherConfig:
    """文章抓取配置"""
    supported_domains: Dict[str, Dict] = field(default_factory=lambda: {
        # 微信公众号
        "mp.weixin.qq.com": {
            "name": "微信公众号",
            "content_selector": "#js_content",
            "title_selector": "#activity-name",
            "author_selector": "#js_name",
            "date_selector": "#publish_time",
        },
        # 知乎
        "zhuanlan.zhihu.com": {
            "name": "知乎专栏",
            "content_selector": ".Post-RichText, .RichText",
            "title_selector": ".Post-Title, h1",
        },
        "www.zhihu.com": {
            "name": "知乎问答",
            "content_selector": ".RichContent-inner",
            "title_selector": ".QuestionHeader-title",
        },
        # 微博
        "weibo.com": {
            "name": "微博",
            "content_selector": ".WB_text, .detail_text",
            "title_selector": ".WB_text",
        },
        "m.weibo.cn": {
            "name": "微博移动版",
            "content_selector": ".weibo-text",
            "title_selector": ".weibo-text",
        },
        # 今日头条
        "www.toutiao.com": {
            "name": "今日头条",
            "content_selector": ".article-content",
            "title_selector": ".article-title",
        },
        # 36氪
        "36kr.com": {
            "name": "36氪",
            "content_selector": ".article-content, .detail-content",
            "title_selector": ".article-title, h1",
        },
        # 少数派
        "sspai.com": {
            "name": "少数派",
            "content_selector": ".article-content",
            "title_selector": ".article-title",
        },
        # 掘金
        "juejin.cn": {
            "name": "掘金",
            "content_selector": ".article-content",
            "title_selector": ".article-title",
        },
        # 博客园
        "www.cnblogs.com": {
            "name": "博客园",
            "content_selector": "#cnblogs_post_body",
            "title_selector": "#cb_post_title_url",
        },
        # CSDN
        "blog.csdn.net": {
            "name": "CSDN",
            "content_selector": "#article_content",
            "title_selector": ".title-article",
        },
        # 简书
        "www.jianshu.com": {
            "name": "简书",
            "content_selector": ".article",
            "title_selector": ".title",
        },
        # 腾讯新闻
        "new.qq.com": {
            "name": "腾讯新闻",
            "content_selector": ".content-article, #article-content",
            "title_selector": ".title, h1",
        },
        # 网易新闻
        "news.163.com": {
            "name": "网易新闻",
            "content_selector": ".post_body, #content",
            "title_selector": ".title, h1",
        },
        # 新浪新闻
        "news.sina.com.cn": {
            "name": "新浪新闻",
            "content_selector": "#article, .article-content",
            "title_selector": ".main-title, h1",
        },
        # 澎湃新闻
        "www.thepaper.cn": {
            "name": "澎湃新闻",
            "content_selector": ".news_content, .article-content",
            "title_selector": ".news_title, h1",
        },
        # 观察者网
        "www.guancha.cn": {
            "name": "观察者网",
            "content_selector": ".content, .article-content",
            "title_selector": ".title, h1",
        },
        # 环球网
        "world.huanqiu.com": {
            "name": "环球网",
            "content_selector": ".article-content",
            "title_selector": ".title, h1",
        },
    })
    
    # 通用正文提取规则（当没有特定规则时使用）
    generic_selectors: list = field(default_factory=lambda: [
        "article",
        ".article-content",
        ".post-content",
        ".entry-content",
        ".content",
        "#content",
        ".main-content",
        "main",
    ])
    
    # 广告/噪音选择器（去除这些元素）
    noise_selectors: list = field(default_factory=lambda: [
        "script", "style", "nav", "header", "footer",
        ".ad", ".ads", ".advertisement", ".sidebar",
        ".related-posts", ".recommend", ".comments",
        ".social-share", ".share-btn", ".author-info",
        "#comments", "#sidebar", "#footer",
        "[class*='ad-']", "[class*='ads-']",
        "[id*='ad-']", "[id*='ads-']",
    ])
    
    # 最大内容长度（字符）
    max_content_length: int = 50000
    
    # 超时时间（秒）
    timeout: int = 15


@dataclass
class Config:
    """总配置"""
    version: str = "2.0.0"
    platforms: Dict[str, PlatformConfig] = field(default_factory=lambda: {
        "bing_global": PlatformConfig(enabled=True, timeout=10, max_results=10),
        "bing_cn": PlatformConfig(enabled=True, timeout=10, max_results=10),
        "yandex": PlatformConfig(enabled=True, timeout=10, max_results=10),
        "swisscows": PlatformConfig(enabled=True, timeout=10, max_results=10),
        "trading_economics": PlatformConfig(enabled=True, timeout=15, max_results=5),
    })
    anti_crawl: AntiCrawlConfig = field(default_factory=AntiCrawlConfig)
    article_fetcher: ArticleFetcherConfig = field(default_factory=ArticleFetcherConfig)
    
    # 全局设置
    global_timeout: int = 30  # 单次操作最大超时
    max_retries: int = 3
    user_agent: str = "auto"  # auto/chrome/firefox/safari


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = DEFAULT_CONFIG_PATH):
        self.config_path = config_path
        self._config: Optional[Config] = None
    
    def load(self) -> Config:
        """加载配置"""
        if self._config is not None:
            return self._config
        
        # 尝试从文件加载
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._config = self._dict_to_config(data)
                return self._config
            except Exception as e:
                print(f"配置文件加载失败，使用默认配置: {e}")
        
        # 使用默认配置
        self._config = Config()
        return self._config
    
    def save(self, config: Optional[Config] = None):
        """保存配置"""
        if config is None:
            config = self._config or Config()
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        # 转换为字典并保存
        data = self._config_to_dict(config)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _dict_to_config(self, data: Dict) -> Config:
        """字典转配置对象"""
        config = Config()
        
        # 版本
        if "version" in data:
            config.version = data["version"]
        
        # 平台配置
        if "platforms" in data:
            platforms = {}
            for name, pdata in data["platforms"].items():
                platforms[name] = PlatformConfig(
                    enabled=pdata.get("enabled", True),
                    timeout=pdata.get("timeout", 10),
                    retry=pdata.get("retry", 2),
                    delay_range=tuple(pdata.get("delay_range", [0.5, 1.5])),
                    max_results=pdata.get("max_results", 10),
                )
            config.platforms = platforms
        
        # 反爬配置
        if "anti_crawl" in data:
            ac = data["anti_crawl"]
            config.anti_crawl = AntiCrawlConfig(
                user_agent_rotation=ac.get("user_agent_rotation", True),
                referer_rotation=ac.get("referer_rotation", True),
                cookie_persistence=ac.get("cookie_persistence", True),
                request_delay=ac.get("request_delay", True),
                max_requests_per_minute=ac.get("max_requests_per_minute", 30),
            )
        
        # 文章抓取配置
        if "article_fetcher" in data:
            af = data["article_fetcher"]
            config.article_fetcher = ArticleFetcherConfig(
                supported_domains=af.get("supported_domains", {}),
                generic_selectors=af.get("generic_selectors", []),
                noise_selectors=af.get("noise_selectors", []),
                max_content_length=af.get("max_content_length", 50000),
                timeout=af.get("timeout", 15),
            )
        
        # 全局设置
        for key in ["global_timeout", "max_retries", "user_agent"]:
            if key in data:
                setattr(config, key, data[key])
        
        return config
    
    def _config_to_dict(self, config: Config) -> Dict:
        """配置对象转字典"""
        result = {
            "version": config.version,
            "global_timeout": config.global_timeout,
            "max_retries": config.max_retries,
            "user_agent": config.user_agent,
        }
        
        # 平台配置
        result["platforms"] = {}
        for name, pc in config.platforms.items():
            result["platforms"][name] = {
                "enabled": pc.enabled,
                "timeout": pc.timeout,
                "retry": pc.retry,
                "delay_range": list(pc.delay_range),
                "max_results": pc.max_results,
            }
        
        # 反爬配置
        result["anti_crawl"] = {
            "user_agent_rotation": config.anti_crawl.user_agent_rotation,
            "referer_rotation": config.anti_crawl.referer_rotation,
            "cookie_persistence": config.anti_crawl.cookie_persistence,
            "request_delay": config.anti_crawl.request_delay,
            "max_requests_per_minute": config.anti_crawl.max_requests_per_minute,
        }
        
        # 文章抓取配置
        result["article_fetcher"] = {
            "supported_domains": config.article_fetcher.supported_domains,
            "generic_selectors": config.article_fetcher.generic_selectors,
            "noise_selectors": config.article_fetcher.noise_selectors,
            "max_content_length": config.article_fetcher.max_content_length,
            "timeout": config.article_fetcher.timeout,
        }
        
        return result
    
    def get_platform(self, name: str) -> Optional[PlatformConfig]:
        """获取平台配置"""
        config = self.load()
        return config.platforms.get(name)
    
    def set_platform(self, name: str, **kwargs):
        """设置平台配置"""
        config = self.load()
        if name not in config.platforms:
            config.platforms[name] = PlatformConfig()
        
        for key, value in kwargs.items():
            if hasattr(config.platforms[name], key):
                setattr(config.platforms[name], key, value)
        
        self.save(config)
    
    def enable_platform(self, name: str):
        """启用平台"""
        self.set_platform(name, enabled=True)
    
    def disable_platform(self, name: str):
        """禁用平台"""
        self.set_platform(name, enabled=False)
    
    def get_domain_config(self, domain: str) -> Optional[Dict]:
        """获取域名配置"""
        config = self.load()
        return config.article_fetcher.supported_domains.get(domain)
    
    def reload(self) -> Config:
        """重新加载配置"""
        self._config = None
        return self.load()


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """获取配置管理器单例"""
    global _config_manager
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    if _config_manager is None or _config_manager.config_path != config_path:
        _config_manager = ConfigManager(config_path)
    return _config_manager


def get_config(config_path: Optional[str] = None) -> Config:
    """获取配置对象"""
    return get_config_manager(config_path).load()


# 命令行入口
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python config.py <命令>")
        print("命令:")
        print("  show       显示当前配置")
        print("  init       初始化配置文件")
        print("  enable <平台>  启用平台")
        print("  disable <平台> 禁用平台")
        sys.exit(1)
    
    cmd = sys.argv[1]
    manager = get_config_manager()
    
    if cmd == "show":
        config = manager.load()
        print(json.dumps(manager._config_to_dict(config), ensure_ascii=False, indent=2))
    
    elif cmd == "init":
        manager.save()
        print(f"配置文件已创建: {manager.config_path}")
    
    elif cmd == "enable" and len(sys.argv) > 2:
        platform = sys.argv[2]
        manager.enable_platform(platform)
        print(f"已启用平台: {platform}")
    
    elif cmd == "disable" and len(sys.argv) > 2:
        platform = sys.argv[2]
        manager.disable_platform(platform)
        print(f"已禁用平台: {platform}")
    
    else:
        print("未知命令")
        sys.exit(1)